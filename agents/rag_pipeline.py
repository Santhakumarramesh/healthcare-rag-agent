"""
LangGraph Multi-Agent RAG Pipeline for Healthcare FAQ.

Agent Flow:
User Query
    └─► ROUTER AGENT      — Classifies intent, detects emergencies, routes query
            ├─► RETRIEVER AGENT   — Fetches relevant chunks from FAISS
            │       └─► RESPONDER AGENT  — Generates grounded, safe medical response
            │               └─► EVALUATOR AGENT — Scores response quality & flags issues
            └─► (Emergency) ── Direct safety response bypassing retrieval
"""
import sys
from pathlib import Path
from typing import TypedDict, Annotated, List, Dict, Any
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

# langchain-nvidia-ai-endpoints and tavily are optional (not installed on Render).
# They are imported lazily inside the functions that need them.
import operator
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config
from vectorstore.retriever import HybridRetriever, RetrievedChunk


# ─── Enums ────────────────────────────────────────────────────────────────────

class QueryIntent(str, Enum):
    MEDICAL_FAQ = "medical_faq"
    EMERGENCY = "emergency"
    GENERAL_GREETING = "greeting"
    OUT_OF_SCOPE = "out_of_scope"
    WEB_SEARCH = "web_search"
    FOLLOW_UP = "follow_up"


# ─── Graph State ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """The state of the RAG pipeline."""
    # Input
    user_query: str
    conversation_history: Annotated[list, operator.add]

    # Router outputs
    intent: QueryIntent
    is_emergency: bool
    reformulated_query: str
    decision: str # Added for routing decisions

    # Retriever outputs
    retrieved_chunks: List[Dict[str, Any]] # More specific type
    context: str
    retrieval_confidence: float

    # Responder outputs
    response: str
    disclaimer_added: bool

    # Evaluator outputs
    quality_score: float
    hallucination_risk: str
    evaluation_notes: str

    # Metadata
    agent_trace: Annotated[list, operator.add]
    error: str
    retry_count: int


# ─── LLM Setup ────────────────────────────────────────────────────────────────

def get_llm(temperature: float = 0.0, streaming: bool = False):
    """
    LLM factory — 3 modes, resolved in priority order:
      1. LOCAL_MODE=true  → AirLLM (Llama 3 8B on-device, no API key, private)
      2. NVIDIA_API_KEY   → NVIDIA NIM (cloud, fast, powerful)
      3. default          → OpenAI GPT-4o-mini (cloud, fast, cheap)
    """
    # ── Mode 1: Local privacy mode via AirLLM ────────────────────────────────
    if config.LOCAL_MODE:
        try:
            from utils.local_llm import LocalLLM, is_apple_silicon
            if is_apple_silicon():
                logger.info("[LLM] Using LOCAL mode (AirLLM + Llama 3 8B on Apple MLX)")
                return LocalLLM(model_id=config.LOCAL_MODEL_ID)
            else:
                logger.warning("[LLM] LOCAL_MODE=true but not Apple Silicon — falling back to OpenAI")
        except ImportError:
            logger.warning("[LLM] AirLLM not installed — falling back to OpenAI. Run: pip install airllm mlx mlx-lm")

    # ── Mode 2: NVIDIA NIM cloud ─────────────────────────────────────────────
    if config.NVIDIA_API_KEY and "your-" not in config.NVIDIA_API_KEY:
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            logger.debug(f"[LLM] Using NVIDIA NIM: {config.NVIDIA_MODEL}")
            return ChatNVIDIA(
                model=config.NVIDIA_MODEL,
                api_key=config.NVIDIA_API_KEY,
                temperature=temperature,
                streaming=streaming,
            )
        except ImportError:
            logger.warning("[LLM] langchain_nvidia_ai_endpoints not installed — falling back to OpenAI")

    # ── Mode 3: OpenAI (default) ─────────────────────────────────────────────
    logger.debug(f"[LLM] Using OpenAI: {config.OPENAI_MODEL}")
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=temperature,
        streaming=streaming,
    )


# ─── Agent 1: Router ──────────────────────────────────────────────────────────

ROUTER_SYSTEM_PROMPT = """You are a medical query router for a Healthcare FAQ assistant.

Analyze the user's query and respond with ONLY a JSON object containing:
{
  "intent": "<medical_faq|emergency|greeting|out_of_scope|web_search|follow_up>",
  "is_emergency": <true|false>,
  "reformulated_query": "<cleaned, specific version of the query for retrieval>",
  "reasoning": "<brief explanation>"
}

Intent definitions:
- medical_faq: General non-emergency medical questions.
- emergency: Life-threatening situations (heart attack, stroke, etc.)
- web_search: Queries about RECENT news, recalls (2024-2025), or current health outbreaks.
- greeting: Simple hello/hi.
- out_of_scope: Non-medical topics (sports, cooking, finance, etc.)
- follow_up: Continuation of previous medical discussion

Emergency examples: "I have crushing chest pain", "Someone is having a seizure", "I think I overdosed"

IMPORTANT: When in doubt about emergency status, set is_emergency=true. Safety first.
Respond ONLY with valid JSON. No markdown, no explanation outside JSON."""


async def router_agent(state: AgentState) -> AgentState:
    """
    Agent 1: Routes the query, detects emergencies, reformulates for retrieval.
    """
    logger.info(f"[ROUTER] Processing: '{state['user_query'][:60]}...'")
    llm = get_llm(temperature=0.0)

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['user_query']}"),
    ]

    try:
        import json
        response = await llm.ainvoke(messages)
        result = json.loads(response.content.strip())

        logger.info(
            f"[ROUTER] Intent: {result['intent']} | "
            f"Emergency: {result['is_emergency']} | "
            f"Reformulated: {result['reformulated_query'][:50]}"
        )

        return {
            **state,
            "intent": result["intent"],
            "is_emergency": result["is_emergency"],
            "reformulated_query": result.get("reformulated_query", state["user_query"]),
            "agent_trace": [f"ROUTER: {result['intent']} | emergency={result['is_emergency']}"],
        }
    except Exception as e:
        logger.error(f"[ROUTER] Failed: {e}")
        return {
            **state,
            "intent": QueryIntent.MEDICAL_FAQ,
            "is_emergency": False,
            "reformulated_query": state["user_query"],
            "agent_trace": [f"ROUTER: fallback due to error: {e}"],
            "error": str(e),
        }


# ─── Agent 2: Retriever ───────────────────────────────────────────────────────

_retriever_instance = None

def get_retriever() -> HybridRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = HybridRetriever()
    return _retriever_instance


async def retriever_agent(state: AgentState) -> AgentState:
    """
    Agent 2: Fetches relevant chunks from FAISS + reranks them.
    """
    query = state.get("reformulated_query") or state["user_query"]
    logger.info(f"[RETRIEVER] Searching: '{query[:60]}...'")

    try:
        retriever = get_retriever()
        # In a real async system, we'd use an async retriever, but for now we'll run in a thread
        import asyncio
        chunks = await asyncio.to_thread(retriever.retrieve, query)
        context = retriever.format_context(chunks)

        # Confidence = average of top rerank scores
        confidence = (
            sum(c.rerank_score for c in chunks) / len(chunks) if chunks else 0.0
        )

        logger.info(f"[RETRIEVER] Found {len(chunks)} chunks | Confidence: {confidence:.3f}")

        return {
            **state,
            "retrieved_chunks": [
                {"text": c.text, "metadata": c.metadata, "score": c.rerank_score}
                for c in chunks
            ],
            "context": context,
            "retrieval_confidence": confidence,
            "agent_trace": [f"RETRIEVER: {len(chunks)} chunks | confidence={confidence:.3f}"],
        }
    except Exception as e:
        logger.error(f"[RETRIEVER] Failed: {e}")
        return {
            **state,
            "retrieved_chunks": [],
            "context": "Knowledge base unavailable.",
            "retrieval_confidence": 0.0,
            "agent_trace": [f"RETRIEVER: error - {e}"],
            "error": str(e),
        }


# ─── Agent 3: Web Search ──────────────────────────────────────────────────────

async def web_search_agent(state: AgentState) -> AgentState:
    """Agent 3b: Real-time search fallback for recent events."""
    query = state.get("reformulated_query") or state["user_query"]
    logger.info(f"[WEB_SEARCH] Searching for: {query}")
    
    if not config.TAVILY_API_KEY or config.TAVILY_API_KEY == "tvly-your-key-here":
        logger.warning("Tavily API key not found. Skipping web search.")
        return {**state, "context": "Error: Web search required but API key missing.", "agent_trace": ["WEB_SEARCH: error - missing key"]}

    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=config.TAVILY_API_KEY)
        # Search for medical news/recalls
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        
        context_parts = []
        sources = []
        for result in response.get("results", []):
            context_parts.append(f"Source: {result['url']}\nContent: {result['content']}")
            sources.append({"source": result['url'], "title": result.get("title", "Web Result")})
            
        full_context = "\n\n---\n\n".join(context_parts)
        
        return {
            **state,
            "context": full_context,
            "retrieved_chunks": sources, # Mocking structure for SSE
            "retrieval_confidence": 0.8, # Web search is usually relevant
            "agent_trace": [f"WEB_SEARCH: {len(sources)} results found"],
        }
    except Exception as e:
        logger.error(f"[WEB_SEARCH] Failed: {e}")
        return {**state, "error": str(e), "agent_trace": [f"WEB_SEARCH: error - {e}"]}


# ─── Agent 3: Responder ───────────────────────────────────────────────────────

RESPONDER_SYSTEM_PROMPT = """You are a knowledgeable, empathetic Healthcare FAQ Assistant.

Your role:
- Answer medical questions accurately based ONLY on the provided context
- Be clear, concise, and compassionate
- Use plain language (avoid excessive jargon)
- Structure answers with clear sections when appropriate

STRICT RULES:
1. ONLY use information from the provided context. Do NOT use outside knowledge.
2. If context is insufficient, honestly say you don't have enough information.
3. NEVER diagnose conditions or prescribe treatments.
4. ALWAYS recommend consulting a healthcare provider for personal medical decisions.
5. For any life-threatening symptoms mentioned, direct to 911 or emergency services immediately.
6. Add the medical disclaimer at the end of EVERY response.

Response format:
- Direct answer to the question
- Key points (if applicable)
- When to seek immediate care (if relevant)
- Medical disclaimer (ALWAYS include)

Disclaimer to include:
"⚕️ Medical Disclaimer: This information is for educational purposes only and does not constitute medical advice. Always consult a qualified healthcare provider for personal medical decisions."
"""

EMERGENCY_RESPONSE = """🚨 **MEDICAL EMERGENCY — CALL 911 IMMEDIATELY**

Based on your description, you may be experiencing a **medical emergency** that requires immediate professional attention.

**Please take these steps RIGHT NOW:**
1. **Call 911** (or have someone call for you)
2. **Do not drive yourself** to the hospital
3. **Stay calm** and follow the dispatcher's instructions
4. **Unlock your door** so emergency responders can enter

**Emergency Resources:**
- 🚑 **Emergency:** 911
- 🧠 **Stroke:** 911 (note the time symptoms started)
- ❤️ **Cardiac Emergency:** 911 (chew aspirin 325mg if not allergic)
- 🆘 **Suicide/Crisis:** 988 Suicide & Crisis Lifeline
- ☠️ **Poison Control:** 1-800-222-1222

⚕️ *I am an AI assistant and cannot provide emergency medical care. Please contact emergency services immediately.*"""

GREETING_RESPONSE = """👋 Hello! I'm your **Healthcare FAQ Assistant**, powered by AI.

I can help you with:
- 🩺 **Symptoms & Conditions** — Understanding common medical symptoms
- 💊 **Medications** — General information about common drugs
- 🛡️ **Preventive Care** — Vaccines, screenings, wellness tips
- ❤️ **Heart Health** — Cardiac symptoms and risk factors
- 🧠 **Mental Health** — Depression, anxiety, and mental wellness
- 👩 **Women's Health** — PCOS, hormonal health, and more
- 🚨 **Emergency Guidance** — When to call 911

**How to use:** Just ask your health question in plain English!

*Example: "What are symptoms of high blood pressure?" or "Can I take ibuprofen with acetaminophen?"*

⚕️ *Remember: I provide general health information only. For personal medical advice, always consult your healthcare provider.*"""

OUT_OF_SCOPE_RESPONSE = """I'm sorry, but I'm specifically designed for **healthcare and medical FAQ** questions only.

I'm not able to help with that topic. However, I'd be happy to answer questions about:
- Medical symptoms and conditions
- Medications and drug interactions
- Preventive care and screenings
- Mental health information
- Emergency guidance

Is there a health-related question I can help you with? 😊"""


async def responder_agent(state: AgentState) -> AgentState:
    """
    Agent 3: Generates the final response grounded in retrieved context.
    Handles special intents (emergency, greeting, out-of-scope) directly.
    """
    intent = state.get("intent", QueryIntent.MEDICAL_FAQ)
    logger.info(f"[RESPONDER] Generating response for intent: {intent}")

    # Handle non-retrieval intents directly
    if state.get("is_emergency"):
        return {**state, "response": EMERGENCY_RESPONSE, "disclaimer_added": True,
                "agent_trace": ["RESPONDER: emergency direct response"]}

    if intent == QueryIntent.GENERAL_GREETING:
        return {**state, "response": GREETING_RESPONSE, "disclaimer_added": True,
                "agent_trace": ["RESPONDER: greeting direct response"]}

    if intent == QueryIntent.OUT_OF_SCOPE:
        return {**state, "response": OUT_OF_SCOPE_RESPONSE, "disclaimer_added": False,
                "agent_trace": ["RESPONDER: out-of-scope response"]}

    # Generate LLM response grounded in context
    llm = get_llm(temperature=0.1)
    context = state.get("context", "No relevant context found.")
    confidence = state.get("retrieval_confidence", 0.0)

    low_confidence_note = (
        "\n\n*Note: I couldn't find highly specific information about this query in my knowledge base. "
        "The response below is based on the closest available information.*"
        if confidence < config.CONFIDENCE_THRESHOLD else ""
    )

    # Build conversation history for context
    history_messages = []
    for msg in state.get("conversation_history", [])[-4:]:  # Last 2 turns
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))

    # Build system prompt based on retry status
    system_prompt = RESPONDER_SYSTEM_PROMPT
    if state.get("retry_count", 0) > 0:
        system_prompt += (
            "\n\n**IMPORTANT: SELF-CORRECTION MODE**\n"
            "Your previous response was rated low quality. Please focus more on accuracy, groundedness, "
            "and addressing the user's question directly from the provided context."
        )

    messages = [
        SystemMessage(content=system_prompt),
        *history_messages,
        HumanMessage(content=(
            f"RETRIEVED CONTEXT:\n{context}\n\n"
            f"USER QUESTION: {state['user_query']}\n\n"
            f"Please provide a helpful, accurate answer based ONLY on the context above."
        )),
    ]

    try:
        response = await llm.ainvoke(messages)
        final_response = response.content + low_confidence_note
        logger.info(f"[RESPONDER] Generated {len(final_response)} char response")

        return {
            **state,
            "response": final_response,
            "disclaimer_added": "Medical Disclaimer" in final_response,
            "agent_trace": [f"RESPONDER: {len(final_response)} chars | confidence={confidence:.2f}"],
        }
    except Exception as e:
        logger.error(f"[RESPONDER] Failed: {e}")
        return {
            **state,
            "response": "I apologize, but I encountered an error generating a response. Please try again.",
            "disclaimer_added": False,
            "agent_trace": [f"RESPONDER: error - {e}"],
            "error": str(e),
        }


# ─── Agent 4: Evaluator ───────────────────────────────────────────────────────

EVALUATOR_SYSTEM_PROMPT = """You are a medical AI response quality evaluator.

Evaluate the assistant's response and return ONLY a JSON object:
{
  "quality_score": <0.0-1.0>,
  "hallucination_risk": "<low|medium|high>",
  "has_disclaimer": <true|false>,
  "is_grounded": <true|false>,
  "notes": "<brief evaluation notes>",
  "decision": "<FINISH|RETRY>"
}

Note: If quality_score < 0.7 AND retry_count < 1, set decision to 'RETRY'. Otherwise set to 'FINISH'.

Evaluation criteria:
- quality_score: 0.0 (poor) to 1.0 (excellent)
  - Accuracy: Is the response consistent with the context?
  - Completeness: Does it address the question fully?
  - Safety: Does it recommend professional care appropriately?
  - Clarity: Is it easy to understand?
- hallucination_risk: Does the response contain claims NOT supported by the context?
- is_grounded: Is the response based on the provided context only?

Respond ONLY with valid JSON."""


async def evaluator_agent(state: AgentState) -> AgentState:
    """
    Agent 4: Quality control — scores response, flags hallucination risks.
    """
    logger.info("[EVALUATOR] Evaluating response quality...")

    # Skip evaluation for direct responses
    if state.get("is_emergency") or state.get("intent") in [
        QueryIntent.GENERAL_GREETING, QueryIntent.OUT_OF_SCOPE
    ]:
        return {
            **state,
            "quality_score": 1.0,
            "hallucination_risk": "low",
            "evaluation_notes": "Direct response — evaluation skipped.",
            "agent_trace": ["EVALUATOR: skipped (direct response)"],
        }

    llm = get_llm(temperature=0.0)

    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"CONTEXT PROVIDED TO ASSISTANT:\n{state.get('context', '')[:1000]}\n\n"
            f"USER QUESTION: {state['user_query']}\n\n"
            f"ASSISTANT RESPONSE:\n{state.get('response', '')[:1500]}"
        )),
    ]

    try:
        import json
        eval_response = await llm.ainvoke(messages)
        cleaned_content = eval_response.content.strip()
        eval_data = json.loads(cleaned_content)
        
        quality_score = eval_data.get("quality_score", 0.0)
        decision = eval_data.get("decision", "FINISH")
        
        # Enforce max 1 retry via logic
        if state.get("retry_count", 0) >= 1:
            decision = "FINISH"

        logger.info(f"[EVALUATOR] Score: {quality_score:.2f} | Decision: {decision}")

        return {
            **state,
            "quality_score": quality_score,
            "hallucination_risk": eval_data.get("hallucination_risk", "high"),
            "evaluation_notes": eval_data.get("notes", ""),
            "agent_trace": [f"EVALUATOR: score={quality_score:.2f} | decision={decision}"],
            "retry_count": state.get("retry_count", 0) + (1 if decision == "RETRY" else 0)
        }
    except Exception as e:
        logger.error(f"[EVALUATOR] Failed: {e}")
        return {
            **state,
            "quality_score": 0.5,
            "hallucination_risk": "unknown",
            "evaluation_notes": f"Evaluation error: {e}",
            "agent_trace": [f"EVALUATOR: error - {e}"],
            "error": str(e),
        }


# ─── Routing Logic ────────────────────────────────────────────────────────────

def route_after_router(state: AgentState) -> str:
    """Conditional edge: decide which agent to call after the router."""
    if state.get("is_emergency"):
        return "responder"  # Skip retrieval for emergencies
    intent = state.get("intent", QueryIntent.MEDICAL_FAQ)
    if intent == QueryIntent.WEB_SEARCH:
        return "web_search"
    if intent in [QueryIntent.GENERAL_GREETING, QueryIntent.OUT_OF_SCOPE]:
        return "responder"  # Skip retrieval for non-medical queries
    return "retriever"

def route_after_evaluator(state: AgentState) -> str:
    """Reflective loop: decide whether to finish or retry responder."""
    # We use agent_trace to check for RETRY decision parsed in evaluator_agent
    trace = state.get("agent_trace", [])
    if any("decision=RETRY" in t for t in trace):
        logger.warning(f"[GRAHP] Triggering self-correction (retry {state.get('retry_count', 0)})")
        return "retry"
    return "finish"


# ─── Graph Builder ────────────────────────────────────────────────────────────

def build_rag_graph() -> StateGraph:
    """Build and compile the LangGraph multi-agent pipeline."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", router_agent)
    workflow.add_node("retriever", retriever_agent)
    workflow.add_node("web_search", web_search_agent)
    workflow.add_node("responder", responder_agent)
    workflow.add_node("evaluator", evaluator_agent)

    # Define edges
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "retriever": "retriever",
            "web_search": "web_search",
            "responder": "responder",
        }
    )
    workflow.add_edge("retriever", "responder")
    workflow.add_edge("web_search", "responder")
    
    # Conditional edge from Evaluator (Self-Correction Loop)
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "retry": "responder",
            "finish": END,
        }
    )
    workflow.add_edge("evaluator", END)

    return workflow.compile()


# ─── Main Pipeline Interface ──────────────────────────────────────────────────

class HealthcareRAGPipeline:
    """High-level interface for running the multi-agent RAG pipeline."""

    def __init__(self):
        logger.info("Initializing HealthcareRAGPipeline...")
        config.validate()
        self.graph = build_rag_graph()
        self.conversation_history = []
        logger.success("Pipeline ready.")

    def _get_initial_state(self, query: str, history: List[dict] = None) -> AgentState:
        """Helper to create the standardized initial state."""
        return {
            "user_query": query,
            "conversation_history": history or [],
            "agent_trace": [],
            "retry_count": 0,
            "error": "",
            "intent": "",
            "is_emergency": False,
            "reformulated_query": "",
            "retrieved_chunks": [],
            "context": "",
            "retrieval_confidence": 0.0,
            "response": "",
            "disclaimer_added": False,
            "quality_score": 0.0,
            "hallucination_risk": "low",
            "evaluation_notes": ""
        }

    async def run(self, user_query: str) -> dict:
        """Run a query through the full multi-agent pipeline."""
        initial_state = self._get_initial_state(user_query)
        result = await self.graph.ainvoke(initial_state)

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return {
            "response": result["response"],
            "intent": result.get("intent"),
            "is_emergency": result.get("is_emergency", False),
            "retrieval_confidence": result.get("retrieval_confidence", 0.0),
            "quality_score": result.get("quality_score", 0.0),
            "hallucination_risk": result.get("hallucination_risk", "unknown"),
            "evaluation_notes": result.get("evaluation_notes", ""),
            "agent_trace": result.get("agent_trace", []),
            "sources": result.get("retrieved_chunks", []),
        }

    async def astream(self, user_query: str):
        """
        Stream the response token-by-token.
        Yields tokens for the response, and finally a metadata object for UI sync.
        """
        initial_state = self._get_initial_state(user_query)
        final_state = initial_state.copy()
        full_response = ""

        async for event in self.graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            
            # Update state tracker as nodes finish (important for capturing final metadata)
            if kind == "on_chain_end":
                if "output" in event["data"] and isinstance(event["data"]["output"], dict):
                    final_state.update(event["data"]["output"])

            # Stream tokens
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    full_response += content
                    yield content

        # Update conversation history with the full gathered response
        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": full_response})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        # Yield final metadata for UI sidebars
        yield {
            "type": "metadata",
            "content": {
                "intent": final_state.get("intent", "medical_faq"),
                "is_emergency": final_state.get("is_emergency", False),
                "retrieved_chunks": [
                    {"text": c.text, "metadata": c.metadata, "score": c.score} 
                    for c in final_state.get("retrieved_chunks", [])
                    if hasattr(c, "text")
                ],
                "quality_score": final_state.get("quality_score", 0.0),
                "hallucination_risk": final_state.get("hallucination_risk", "unknown"),
                "agent_trace": final_state.get("agent_trace", []),
            }
        }

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared.")
