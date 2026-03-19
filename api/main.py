"""
FastAPI REST API for the Healthcare RAG Multi-Agent System.
"""
import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

import json
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response, StreamingResponse

sys.path.append(str(Path(__file__).parent.parent))
from agents.rag_pipeline import HealthcareRAGPipeline
from agents.router_agent import RouterAgent, QueryType
from agents.reasoning_agent import reasoning_agent
from api.records import router as records_router
from api.auth import router as auth_router
from api.admin import router as admin_router
from services.memory_service import memory_service
from services.citation_service import citation_service
from services.monitoring_service import monitoring_service
from services.alert_service import alert_engine
from services.audit_service import audit_service
from database.database import init_db
from utils.config import config
from utils.cache import response_cache
from utils.rate_limiter import rate_limiter
from utils.hallucination_detector import detect_hallucination

REQUEST_COUNT = Counter("rag_requests_total", "Total RAG requests", ["intent"])
REQUEST_LATENCY = Histogram("rag_request_latency_seconds", "Request latency")
EMERGENCY_COUNT = Counter("rag_emergency_queries_total", "Emergency queries detected")
QUALITY_SCORE_HIST = Histogram("rag_quality_score", "Response quality scores",
                                buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0])

pipeline: Optional[HealthcareRAGPipeline] = None
router_agent: Optional[RouterAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, router_agent
    logger.info("Starting Healthcare RAG API...")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Run ingest at startup if FAISS index doesn't exist yet.
    # This handles Render deployments where ingest is not run as a build step.
    # No local knowledge base — system relies on OpenAI's knowledge + user-uploaded documents
    index_path = Path(config.FAISS_INDEX_PATH)
    if not (index_path / "index.faiss").exists():
        logger.info("FAISS index not found — running ingest now...")
        try:
            from vectorstore.ingest import DocumentIngestionPipeline
            pipeline_ingest = DocumentIngestionPipeline()
            # Empty index — will be populated by user uploads only
            pipeline_ingest.run(extra_paths=[], force_rebuild=True)
            logger.success("Ingest complete.")
        except Exception as e:
            logger.error(f"Ingest failed: {e} — continuing without pre-built index.")

    try:
        pipeline = HealthcareRAGPipeline()
        router_agent = RouterAgent()
        logger.success("Pipeline and Router loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Healthcare RAG Multi-Agent API",
    description="Production-grade Healthcare FAQ assistant powered by LangGraph multi-agent RAG.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(records_router)
app.include_router(auth_router)
app.include_router(admin_router)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000,
                       example="What are the symptoms of Type 2 Diabetes?")
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    intent: str
    is_emergency: bool
    retrieval_confidence: float
    quality_score: float
    hallucination_risk: str
    evaluation_notes: str
    agent_trace: List[str]
    sources: List[dict]
    latency_ms: float
    query_type: Optional[str] = None
    routing_confidence: Optional[float] = None
    citation_summary: Optional[dict] = None
    reasoning_steps: Optional[List[dict]] = None
    clinical_alerts: Optional[List[dict]] = None


class HealthResponse(BaseModel):
    status: str
    pipeline_loaded: bool
    vector_store_ready: bool
    faiss_index_exists: bool
    model: str
    vector_store: str


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint with detailed backend status.
    
    Returns:
        - status: "healthy" if pipeline loaded, "degraded" otherwise
        - pipeline_loaded: whether the RAG pipeline initialized successfully
        - vector_store_ready: whether FAISS index file exists
        - faiss_index_exists: same as vector_store_ready (for UI compatibility)
        - model: configured OpenAI model name
        - vector_store: configured vector store type
    """
    index_path = Path(config.FAISS_INDEX_PATH)
    vs_ready = (index_path / "index.faiss").exists()
    return HealthResponse(
        status="healthy" if pipeline else "degraded",
        pipeline_loaded=pipeline is not None,
        vector_store_ready=vs_ready,
        faiss_index_exists=vs_ready,
        model=config.OPENAI_MODEL,
        vector_store=config.VECTOR_STORE_TYPE,
    )


@app.get("/metrics", tags=["System"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/history/{session_id}", tags=["Memory"])
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    history = memory_service.get_conversation_history(session_id)
    stats = memory_service.get_session_stats(session_id)
    
    return {
        "session_id": session_id,
        "history": history,
        "stats": stats
    }


@app.delete("/history/{session_id}", tags=["Memory"])
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    memory_service.clear_session(session_id)
    return {"message": "Session history cleared", "session_id": session_id}


@app.get("/monitoring/stats", tags=["Monitoring"])
async def get_monitoring_stats():
    """Get real-time system statistics"""
    stats = monitoring_service.get_real_time_stats()
    time_series = monitoring_service.get_time_series_data(hours=24)
    query_type_data = monitoring_service.get_query_type_chart_data()
    
    return {
        "stats": stats,
        "time_series": time_series,
        "query_type_chart": query_type_data,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat", response_model=ChatResponse, tags=["RAG"])
async def chat(request: ChatRequest):
    if not pipeline or not router_agent:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    # Rate limiting
    client_id = request.session_id or "anonymous"
    allowed, reason = rate_limiter.is_allowed(client_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    # Check cache first
    cached_response = response_cache.get(request.query)
    if cached_response:
        logger.info(f"Returning cached response for query: {request.query[:40]}...")
        return ChatResponse(**cached_response)

    start_time = time.time()
    try:
        # 1. ROUTE THE QUERY
        session_stats = memory_service.get_session_stats(client_id)
        route_info = await router_agent.route(
            request.query,
            context={"has_previous_interaction": session_stats.get("interaction_count", 0) > 0}
        )
        
        # 2. HANDLE EMERGENCY
        if route_info["is_urgent"]:
            emergency_response = {
                "response": "⚠️ **EMERGENCY DETECTED**\n\nThis appears to be an urgent medical situation. Please:\n\n1. **Call emergency services (911) immediately**, or\n2. **Go to the nearest emergency room**\n\nDo not wait for online medical advice in emergency situations.",
                "intent": "emergency",
                "is_emergency": True,
                "retrieval_confidence": 1.0,
                "quality_score": 1.0,
                "hallucination_risk": "none",
                "evaluation_notes": "Emergency query detected",
                "agent_trace": ["Emergency detection triggered"],
                "sources": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "query_type": route_info["type"],
                "routing_confidence": route_info["confidence"]
            }
            EMERGENCY_COUNT.inc()
            return ChatResponse(**emergency_response)
        
        # 3. GET CONVERSATION CONTEXT
        conversation_context = memory_service.get_recent_context(client_id, limit=3)
        
        # 4. ENHANCE QUERY WITH CONTEXT
        enhanced_query = request.query
        if conversation_context:
            enhanced_query = f"{conversation_context}\n\nCurrent question: {request.query}"
        
        # 5. RUN RAG PIPELINE
        result = await pipeline.run(enhanced_query)
        latency_ms = (time.time() - start_time) * 1000

        # 6. FORMAT CITATIONS
        raw_sources = result.get("sources", [])
        formatted_citations = citation_service.format_citations(raw_sources, max_sources=5)
        citation_summary = citation_service.get_citation_summary(formatted_citations)

        # 7. RUN HALLUCINATION DETECTION
        hallucination_score = 0.0
        if result.get("context") and config.OPENAI_API_KEY:
            hall_result = await detect_hallucination(
                context=result.get("context", ""),
                response=result.get("response", ""),
                api_key=config.OPENAI_API_KEY
            )
            hallucination_score = hall_result.get("score", 0.0)
            if hall_result.get("risk_level") == "high":
                result["hallucination_risk"] = "high"

        # 8. CALCULATE ENHANCED CONFIDENCE
        retrieval_confidence = result.get("retrieval_confidence", 0.0)
        quality_score = result.get("quality_score", 0.0)
        grounding_score = 1.0 - hallucination_score
        
        enhanced_confidence = (
            0.4 * retrieval_confidence +
            0.4 * grounding_score +
            0.2 * quality_score
        )

        # 9. CHECK FOR CLINICAL ALERTS
        clinical_alerts = alert_engine.check_query(request.query)
        
        # Log alerts if any
        for alert in clinical_alerts:
            audit_service.log_alert(
                user_id=client_id,
                alert_type=alert["type"],
                severity=alert["severity"],
                message=alert["message"]
            )
        
        # 10. APPLY MULTI-STEP REASONING FOR COMPLEX QUERIES
        reasoning_steps = []
        use_reasoning = route_info["type"] in ["symptom_check", "preventive_care"] and len(request.query.split()) > 15
        
        if use_reasoning:
            # Extract evidence text from sources
            evidence_texts = [
                getattr(source, 'page_content', getattr(source, 'text', ''))
                for source in raw_sources[:5]
            ]
            
            # Run reasoning agent
            reasoning_result = await reasoning_agent.reason(
                request.query,
                evidence_texts,
                context=conversation_context
            )
            
            # Use reasoning agent's answer
            result["response"] = reasoning_result["answer"]
            reasoning_steps = reasoning_result["reasoning_steps"]
            
            # Update confidence with reasoning confidence
            enhanced_confidence = (enhanced_confidence + reasoning_result["confidence"]) / 2

        # 11. UPDATE METRICS
        REQUEST_COUNT.labels(intent=route_info["type"]).inc()
        REQUEST_LATENCY.observe(latency_ms / 1000)
        QUALITY_SCORE_HIST.observe(enhanced_confidence)
        
        # Record in monitoring service
        monitoring_service.record_query(
            query_type=route_info["type"],
            latency_ms=latency_ms,
            confidence=enhanced_confidence,
            sources_count=len(formatted_citations),
            success=True
        )
        
        # Log query in audit service
        audit_service.log_query(
            user_id=client_id,
            query=request.query,
            query_type=route_info["type"],
            confidence=enhanced_confidence,
            session_id=client_id
        )

        logger.info(
            f"Query: '{request.query[:40]}...' | "
            f"Type: {route_info['type']} | "
            f"Latency: {latency_ms:.0f}ms | "
            f"Confidence: {enhanced_confidence:.2f} | "
            f"Sources: {len(formatted_citations)} | "
            f"Reasoning: {'Yes' if reasoning_steps else 'No'}"
        )

        response_data = {
            "response": result["response"],
            "intent": route_info["type"],
            "is_emergency": False,
            "retrieval_confidence": round(enhanced_confidence, 3),
            "quality_score": round(quality_score, 3),
            "hallucination_risk": result.get("hallucination_risk", "low"),
            "evaluation_notes": result.get("evaluation_notes", ""),
            "agent_trace": result.get("agent_trace", []) + [f"Routed as: {route_info['type']}"] + ([f"Multi-step reasoning applied ({len(reasoning_steps)} steps)"] if reasoning_steps else []) + ([f"{len(clinical_alerts)} clinical alert(s) detected"] if clinical_alerts else []),
            "sources": formatted_citations,
            "latency_ms": round(latency_ms, 2),
            "query_type": route_info["type"],
            "routing_confidence": route_info["confidence"],
            "citation_summary": citation_summary,
            "reasoning_steps": reasoning_steps if reasoning_steps else None,
            "clinical_alerts": clinical_alerts if clinical_alerts else None
        }

        # 11. STORE IN MEMORY
        memory_service.add_interaction(client_id, {
            "query": request.query,
            "answer": result["response"],
            "query_type": route_info["type"],
            "confidence": enhanced_confidence,
            "sources": formatted_citations
        })

        # 12. CACHE THE RESPONSE
        response_cache.set(request.query, response_data)

        return ChatResponse(**response_data)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream", tags=["RAG"])
async def chat_stream(request: ChatRequest):
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    async def event_generator():
        try:
            async for chunk in pipeline.astream(request.query):
                if isinstance(chunk, str):
                    # Standard token chunk
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                elif isinstance(chunk, dict) and chunk.get("type") == "metadata":
                    # Final metadata chunk
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                await asyncio.sleep(0.01)  # Tiny sleep to ensure smooth streaming
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/reset", tags=["RAG"])
async def reset_conversation():
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    pipeline.reset_conversation()
    return {"message": "Conversation history cleared.", "status": "ok"}


@app.get("/", tags=["System"])
async def root():
    return {"name": "Healthcare RAG Multi-Agent API", "version": "1.0.0", "docs": "/docs"}


# ── Risk Assessment Endpoint ──────────────────────────────────────────────────

class RiskInput(BaseModel):
    age:               float = Field(45,  ge=18,  le=100)
    bmi:               float = Field(25.0, ge=15, le=50)
    systolic_bp:       float = Field(120, ge=80,  le=220)
    glucose:           float = Field(95,  ge=50,  le=400)
    hba1c:             float = Field(5.5, ge=4,   le=15)
    cholesterol:       float = Field(180, ge=100, le=400)
    smoking:           int   = Field(0,   ge=0,   le=1)
    family_history:    int   = Field(0,   ge=0,   le=1)
    physical_activity: int   = Field(1,   ge=0,   le=2)


@app.post("/risk/assess", tags=["Risk Assessment"])
async def assess_risk(inputs: RiskInput):
    """
    ML-based patient risk assessment with LLM explanation.
    Combines rule-based clinical scoring with GPT-4o-mini explanation.
    Returns risk probability, level, top contributing factors, and actionable recommendations.
    """
    from agents.risk_agent import run_risk_assessment
    try:
        result = await run_risk_assessment(inputs.model_dump())
        return result
    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk/factors", tags=["Risk Assessment"])
async def get_risk_factors():
    """Return the schema of input factors for the risk assessment form."""
    from agents.risk_agent import RISK_FACTORS
    return {"factors": RISK_FACTORS}


# ── Knowledge Base Ingestion Endpoints ───────────────────────────────────────

class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=10)
    source_name: str = "custom_document"


class IngestResponse(BaseModel):
    chunks_stored: int
    source: str
    message: str


@app.post("/ingest/text", response_model=IngestResponse, tags=["Knowledge Base"])
async def ingest_text(req: IngestTextRequest):
    """Add raw text to the shared knowledge base vector store."""
    try:
        from vectorstore.ingest import DocumentIngestionPipeline
        pip = DocumentIngestionPipeline()
        from langchain.schema import Document
        doc = Document(page_content=req.text, metadata={"source": req.source_name})
        chunks = pip._add_documents_to_index([doc])
        return IngestResponse(
            chunks_stored=chunks,
            source=req.source_name,
            message=f"Successfully ingested {chunks} chunks from '{req.source_name}'.",
        )
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file", response_model=IngestResponse, tags=["Knowledge Base"])
async def ingest_file(file: UploadFile = File(...)):
    """Upload a PDF or text file to the shared knowledge base."""
    import tempfile, shutil, os
    suffix = Path(file.filename or "upload").suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        from vectorstore.ingest import DocumentIngestionPipeline
        pip = DocumentIngestionPipeline()
        chunks = pip._ingest_file_to_index(tmp_path, source_name=file.filename or "upload")
        return IngestResponse(
            chunks_stored=chunks,
            source=file.filename or "upload",
            message=f"Successfully ingested {chunks} chunks from '{file.filename}'.",
        )
    except Exception as e:
        logger.error(f"File ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.get("/stats", tags=["System"])
async def get_stats():
    """Get system statistics including cache and rate limiter stats."""
    return {
        "cache": response_cache.stats(),
        "rate_limiter": rate_limiter.stats(),
        "pipeline_loaded": pipeline is not None,
    }


# ── Local LLM Management Endpoints ───────────────────────────────────────────

@app.get("/local-model/status", tags=["Local LLM"])
async def local_model_status():
    """Check if local AirLLM model is available and downloaded."""
    try:
        from utils.local_llm import LocalLLM, is_apple_silicon
        if not is_apple_silicon():
            return {"available": False, "reason": "Not Apple Silicon hardware"}
        llm = LocalLLM()
        info = llm.get_model_info()
        return {"available": True, **info, "local_mode_active": config.LOCAL_MODE}
    except ImportError:
        return {"available": False, "reason": "AirLLM not installed. Run: pip install airllm mlx mlx-lm"}


@app.post("/local-model/download", tags=["Local LLM"])
async def download_local_model(background_tasks: BackgroundTasks):
    """
    Trigger download of the local Llama 3 8B model (~4.7GB).
    Download runs in background — check /local-model/status for progress.
    """
    try:
        from utils.local_llm import LocalLLM, is_apple_silicon
        if not is_apple_silicon():
            raise HTTPException(status_code=400, detail="Local model requires Apple Silicon Mac")

        def _download():
            logger.info("[API] Starting model download in background...")
            llm = LocalLLM()
            llm._load()  # This triggers the download
            logger.success("[API] Model download complete.")

        background_tasks.add_task(_download)
        return {
            "status": "download_started",
            "model": config.LOCAL_MODEL_ID,
            "size": "~4.7 GB",
            "message": "Download started in background. Check /local-model/status for progress."
        }
    except ImportError:
        raise HTTPException(status_code=400, detail="AirLLM not installed. Run: pip install airllm mlx mlx-lm")


@app.post("/local-model/toggle", tags=["Local LLM"])
async def toggle_local_mode(enable: bool):
    """
    Toggle between local (privacy) mode and cloud mode at runtime.
    When enabled, all queries use Llama 3 8B on-device — no data sent externally.
    """
    import os
    os.environ["LOCAL_MODE"] = "true" if enable else "false"
    config.LOCAL_MODE = enable

    mode = "LOCAL (AirLLM Llama 3 8B — private, no data leaves device)" if enable else "CLOUD (OpenAI GPT-4o-mini)"
    logger.info(f"[API] Switched to {mode}")
    return {
        "local_mode": enable,
        "active_model": config.LOCAL_MODEL_ID if enable else config.OPENAI_MODEL,
        "message": f"Now using: {mode}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT,
                reload=config.APP_ENV == "development")
