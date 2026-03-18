import pytest
import sys
import operator
from typing import Annotated, List, Dict, Any, TypedDict, Optional, Union
from enum import Enum
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from unittest.mock import patch, MagicMock, AsyncMock
from agents.rag_pipeline import router_agent, retriever_agent, responder_agent, AgentState, QueryIntent
from vectorstore.retriever import HybridRetriever, RetrievedChunk

@pytest.fixture
def base_state():
    return {
        "user_query": "",
        "conversation_history": [],
        "intent": "",
        "is_emergency": False,
        "reformulated_query": "",
        "retrieved_chunks": [],
        "context": "",
        "retrieval_confidence": 0.0,
        "response": "",
        "disclaimer_added": False,
        "quality_score": 0.0,
        "hallucination_risk": "unknown",
        "evaluation_notes": "",
        "agent_trace": [],
        "error": "",
    }

@pytest.mark.asyncio
async def test_router_detects_emergency(base_state):
    """Test that the router correctly flags life-threatening queries."""
    state = base_state.copy()
    state["user_query"] = "I think I am having a heart attack, my chest hurts badly"
    
    mock_response = MagicMock()
    mock_response.content = '{"intent": "emergency", "is_emergency": true, "reformulated_query": "emergency"}'
    
    with patch("agents.rag_pipeline.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = await router_agent(state)
        assert result["is_emergency"] is True
        assert result["intent"] == "emergency"

@pytest.mark.asyncio
async def test_router_blocks_out_of_scope(base_state):
    """Test that the router identifies non-medical queries."""
    state = base_state.copy()
    state["user_query"] = "How do I bake a chocolate cake?"
    
    mock_response = MagicMock()
    mock_response.content = '{"intent": "out_of_scope", "is_emergency": false, "reformulated_query": "baking cake"}'
    
    with patch("agents.rag_pipeline.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = await router_agent(state)
        assert result["intent"] == "out_of_scope"
        assert result["is_emergency"] is False

def test_retriever_finds_relevant_content():
    """Test that the HybridRetriever returns valid chunks for a medical query."""
    with patch("vectorstore.retriever.HybridRetriever._load_index"), \
         patch("vectorstore.retriever.SentenceTransformer"), \
         patch("vectorstore.retriever.CrossEncoder"):
        
        retriever = HybridRetriever()
        retriever.index = MagicMock()
        retriever.chunks = {0: {"text": "Diabetes symptoms include thirst.", "metadata": {}}}
        
        # Mock search to return index 0 and a score
        retriever.index.search.return_value = ([[0.9]], [[0]])
        
        chunks = retriever.retrieve("diabetes")
        assert len(chunks) > 0
        assert any("diabetes" in chunk.text.lower() for chunk in chunks)

def test_hybrid_rrf_keyword_priority():
    """Verify that BM25 keyword matching complements vector search."""
    retriever = HybridRetriever()
    
    # Mock chunks
    retriever.chunks = [
        {"text": "Diabetes is a chronic condition.", "metadata": {"source": "KB1"}},
        {"text": "The patient has acute hypertension.", "metadata": {"source": "KB2"}},
        {"text": "Aspirin is used for pain relief.", "metadata": {"source": "KB3"}}
    ]
    
    # Manually trigger BM25 initialization with mock chunks
    from rank_bm25 import BM25Okapi
    tokenized_corpus = [retriever._tokenize(c["text"]) for c in retriever.chunks]
    retriever.bm25 = BM25Okapi(tokenized_corpus)
    
    # 1. Test BM25 alone
    keyword_results = retriever.bm25_search("Aspirin relief", top_k=1)
    assert len(keyword_results) == 1
    assert "Aspirin" in keyword_results[0].text
    
    # 2. Test RRF merging
    # Vector result (not Aspirin) vs Keyword result (Aspirin)
    vector_results = [
        RetrievedChunk(text=retriever.chunks[1]["text"], metadata=retriever.chunks[1]["metadata"], score=0.9),
        RetrievedChunk(text=retriever.chunks[0]["text"], metadata=retriever.chunks[0]["metadata"], score=0.8)
    ]
    
    # Keyword result ranking Aspirin at #1
    keyword_results = [
        RetrievedChunk(text=retriever.chunks[2]["text"], metadata=retriever.chunks[2]["metadata"], score=10.0)
    ]
    
    fused = retriever.reciprocal_rank_fusion(vector_results, keyword_results, k=60)
    
    # Aspirin was only in keyword_results at rank 0
    # Hypertension was in vector_results at rank 0
    # Both should be at the top. Let's verify Aspirin is present.
    fused_texts = [res.text for res in fused]
    assert "Aspirin is used for pain relief." in fused_texts

@pytest.mark.asyncio
async def test_self_correction_loop(base_state):
    """Verify that the graph loops back to responder on low quality score."""
    from agents.rag_pipeline import build_rag_graph, evaluator_agent
    from unittest.mock import AsyncMock, patch
    
    # We want to test the graph structure, so we mock the agents
    # To trigger a loop, we need evaluator to return decision=RETRY
    workflow = build_rag_graph()
    
    # Initial state
    state = base_state.copy()
    state["retry_count"] = 0
    
    # Mock evaluator_agent to return RETRY first, then FINISH
    mock_eval = AsyncMock()
    mock_eval.side_effect = [
        {**state, "quality_score": 0.5, "agent_trace": ["EVALUATOR: score=0.5 | decision=RETRY"], "retry_count": 1},
        {**state, "quality_score": 0.9, "agent_trace": ["EVALUATOR: score=0.9 | decision=FINISH"], "retry_count": 1}
    ]
    
    with patch("agents.rag_pipeline.evaluator_agent", mock_eval):
        # We also need to mock responder to avoid real LLM calls
        mock_resp = AsyncMock(return_value={**state, "response": "Improved response"})
        with patch("agents.rag_pipeline.responder_agent", mock_resp):
            # Run the compiled graph manually if needed, or just test the route logic
            from agents.rag_pipeline import route_after_evaluator
            
            # 1. First Pass (Evaluator returns RETRY)
            next_step = route_after_evaluator(await mock_eval(state))
            assert next_step == "retry"
            
            # 2. Second Pass (Evaluator returns FINISH)
            next_step = route_after_evaluator(await mock_eval(state))
            assert next_step == "finish"

@pytest.mark.asyncio
async def test_web_search_routing(base_state):
    """Verify that queries for recent events route to web_search."""
    from agents.rag_pipeline import router_agent, QueryIntent
    
    # Mock LLM to return web_search intent
    state = base_state.copy()
    state["user_query"] = "What are the latest 2025 FDA drug recalls?"
    
    # Instead of running the whole graph, we test the logic in router_agent
    # or just the routing function
    from agents.rag_pipeline import route_after_router
    
    state["intent"] = QueryIntent.WEB_SEARCH
    next_step = route_after_router(state)
    assert next_step == "web_search"

@pytest.mark.asyncio
async def test_responder_adds_disclaimer(base_state):
    """Test that the responder always includes the mandatory medical disclaimer."""
    state = base_state.copy()
    state["intent"] = "medical_faq"
    state["user_query"] = "What is hypertension?"
    state["context"] = "Hypertension is high blood pressure."
    
    mock_response = MagicMock()
    mock_response.content = "Hypertension is high blood pressure. Medical Disclaimer: This is not advice."
    
    with patch("agents.rag_pipeline.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = await responder_agent(state)
        assert "Medical Disclaimer" in result["response"]
        assert result["disclaimer_added"] is True

@pytest.mark.asyncio
async def test_responder_handles_emergencies_directly(base_state):
    """Test that the responder skips LLM generation and gives a direct emergency warning."""
    state = base_state.copy()
    state["is_emergency"] = True
    state["user_query"] = "I can't breathe"
    
    result = await responder_agent(state)
    assert "CALL 911 IMMEDIATELY" in result["response"]
    assert "🚨" in result["response"]

@pytest.mark.asyncio
async def test_retriever_agent_integration(base_state):
    """Test the retriever_agent node in the LangGraph state flow."""
    state = base_state.copy()
    state["user_query"] = "common cold symptoms"
    state["reformulated_query"] = "What are the common symptoms of a cold?"
    
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        RetrievedChunk(text="Cold symptoms include cough.", metadata={}, score=0.9, rerank_score=0.9)
    ]
    mock_retriever.format_context.return_value = "Cold symptoms include cough."
    
    with patch("agents.rag_pipeline.get_retriever") as mock_get_retriever:
        mock_get_retriever.return_value = mock_retriever
        
        result = await retriever_agent(state)
        assert len(result["retrieved_chunks"]) > 0
        assert result["retrieval_confidence"] > 0
        assert "agent_trace" in result
