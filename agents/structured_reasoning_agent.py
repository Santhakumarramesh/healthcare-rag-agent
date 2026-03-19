"""
Structured Reasoning Agent for Healthcare RAG.

Provides multi-step reasoning with evidence grounding, confidence scoring,
and structured output format.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from loguru import logger


@dataclass
class RetrievedChunk:
    """Retrieved document chunk with metadata."""
    source: str
    content: str
    score: float
    category: Optional[str] = None


@dataclass
class ReasoningResult:
    """Structured reasoning output."""
    answer: str
    key_insights: List[str]
    possible_considerations: List[str]
    next_steps: List[str]
    safety_note: str
    confidence: float
    grounded_sources: List[Dict[str, Any]]
    route: str


class StructuredReasoningAgent:
    """
    Structured reasoning layer on top of retrieval.
    Designed for healthcare assistant workflows:
    - grounded answers
    - no direct diagnosis claims
    - safe next-step guidance
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        logger.info("[StructuredReasoningAgent] Initialized")

    def _build_context(self, chunks: List[RetrievedChunk], top_k: int = 5) -> str:
        """Build formatted context from retrieved chunks."""
        selected = sorted(chunks, key=lambda x: x.score, reverse=True)[:top_k]
        context_parts = []

        for i, chunk in enumerate(selected, start=1):
            context_parts.append(
                f"[Source {i}]\n"
                f"Name: {chunk.source}\n"
                f"Score: {chunk.score:.3f}\n"
                f"Category: {chunk.category or 'unknown'}\n"
                f"Content:\n{chunk.content}\n"
            )

        return "\n".join(context_parts)

    def _compute_confidence(self, chunks: List[RetrievedChunk], grounded_count: int) -> float:
        """Compute confidence score based on retrieval and grounding."""
        if not chunks:
            return 0.15

        avg_retrieval = sum(c.score for c in chunks[:5]) / min(len(chunks[:5]), 5)
        grounding_component = min(grounded_count / 5.0, 1.0)

        # Simple weighted confidence heuristic
        confidence = (0.7 * avg_retrieval) + (0.3 * grounding_component)

        # Clamp
        confidence = max(0.10, min(confidence, 0.98))
        return round(confidence, 2)

    def _build_prompt(self, query: str, route: str, context: str) -> str:
        """Build reasoning prompt."""
        return f"""
You are a healthcare reasoning assistant.

Your job:
1. Use ONLY the retrieved evidence below.
2. Do NOT invent medical facts.
3. Do NOT present a diagnosis as certain.
4. Give safe, structured, evidence-grounded guidance.
5. If the question suggests urgent risk, clearly recommend urgent medical attention.
6. Keep the answer understandable for a non-expert.
7. Output strict JSON only.

User query:
{query}

Route:
{route}

Retrieved evidence:
{context}

Return JSON with this exact schema:
{{
  "answer": "short grounded explanation",
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "possible_considerations": ["consideration 1", "consideration 2"],
  "next_steps": ["step 1", "step 2"],
  "safety_note": "brief safety note",
  "grounded_source_ids": [1, 2, 3]
}}

Rules:
- Use only grounded evidence.
- No markdown.
- No extra text outside JSON.
- If evidence is weak, say so.
"""

    def run(
        self,
        query: str,
        route: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> ReasoningResult:
        """
        Run structured reasoning on query and retrieved evidence.

        Args:
            query: User query
            route: Query route type
            retrieved_chunks: Retrieved document chunks

        Returns:
            Structured reasoning result
        """
        if not retrieved_chunks:
            logger.warning("[StructuredReasoningAgent] No chunks provided")
            return ReasoningResult(
                answer="I could not find enough grounded information to answer this safely.",
                key_insights=["No reliable source context was retrieved."],
                possible_considerations=[],
                next_steps=[
                    "Try rephrasing the question.",
                    "Upload a relevant report or provide more context.",
                    "Consult a qualified healthcare professional for urgent concerns."
                ],
                safety_note="This assistant does not replace professional medical advice.",
                confidence=0.15,
                grounded_sources=[],
                route=route
            )

        context = self._build_context(retrieved_chunks)
        prompt = self._build_prompt(query=query, route=route, context=context)

        try:
            raw = self.llm_client.generate(prompt)
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"[StructuredReasoningAgent] JSON parse error: {e}")
            return ReasoningResult(
                answer="I found relevant information, but I could not format the response reliably.",
                key_insights=["Retrieved evidence exists but response formatting failed."],
                possible_considerations=[],
                next_steps=[
                    "Please try again.",
                    "Consult the cited sources directly if available."
                ],
                safety_note="This assistant does not replace professional medical advice.",
                confidence=0.35,
                grounded_sources=[],
                route=route
            )
        except Exception as e:
            logger.error(f"[StructuredReasoningAgent] Generation error: {e}")
            return ReasoningResult(
                answer="An error occurred during reasoning.",
                key_insights=[],
                possible_considerations=[],
                next_steps=["Please try again."],
                safety_note="This assistant does not replace professional medical advice.",
                confidence=0.20,
                grounded_sources=[],
                route=route
            )

        grounded_ids = parsed.get("grounded_source_ids", [])
        grounded_sources = []

        for idx in grounded_ids:
            if isinstance(idx, int) and 1 <= idx <= len(retrieved_chunks[:5]):
                chunk = sorted(retrieved_chunks, key=lambda x: x.score, reverse=True)[:5][idx - 1]
                grounded_sources.append({
                    "source": chunk.source,
                    "score": round(chunk.score, 3),
                    "category": chunk.category or "unknown",
                    "preview": chunk.content[:220].strip()
                })

        confidence = self._compute_confidence(retrieved_chunks, len(grounded_sources))

        return ReasoningResult(
            answer=parsed.get("answer", ""),
            key_insights=parsed.get("key_insights", []),
            possible_considerations=parsed.get("possible_considerations", []),
            next_steps=parsed.get("next_steps", []),
            safety_note=parsed.get(
                "safety_note",
                "This assistant does not replace professional medical advice."
            ),
            confidence=confidence,
            grounded_sources=grounded_sources,
            route=route
        )


# Singleton instance (lazy-loaded)
_structured_reasoning_agent: Optional[StructuredReasoningAgent] = None


def get_structured_reasoning_agent(api_key: str, model: str = "gpt-4o-mini") -> StructuredReasoningAgent:
    """
    Get or create structured reasoning agent singleton.

    This is lazy-loaded to avoid startup delays.
    """
    global _structured_reasoning_agent

    if _structured_reasoning_agent is None:
        try:
            from models.llm_client import OpenAILLMClient
            llm = OpenAILLMClient(api_key=api_key, model=model)
            _structured_reasoning_agent = StructuredReasoningAgent(llm_client=llm)
            logger.info("[StructuredReasoningAgent] Singleton created")
        except Exception as e:
            logger.error(f"[StructuredReasoningAgent] Failed to create: {e}")
            raise

    return _structured_reasoning_agent
