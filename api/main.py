"""
FastAPI REST API for the Healthcare RAG Multi-Agent System.
"""
import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List

import json
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response, StreamingResponse
import json

sys.path.append(str(Path(__file__).parent.parent))
from agents.rag_pipeline import HealthcareRAGPipeline
from api.records import router as records_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    logger.info("Starting Healthcare RAG API...")

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
        logger.success("Pipeline loaded successfully!")
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


class HealthResponse(BaseModel):
    status: str
    pipeline_loaded: bool
    model: str
    vector_store: str


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy" if pipeline else "degraded",
        pipeline_loaded=pipeline is not None,
        model=config.OPENAI_MODEL,
        vector_store=config.VECTOR_STORE_TYPE,
    )


@app.get("/metrics", tags=["System"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse, tags=["RAG"])
async def chat(request: ChatRequest):
    if not pipeline:
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
        result = await pipeline.run(request.query)
        latency_ms = (time.time() - start_time) * 1000

        # Run hallucination detection if we have context
        hallucination_score = 0.0
        if result.get("context") and config.OPENAI_API_KEY:
            hall_result = await detect_hallucination(
                context=result.get("context", ""),
                response=result.get("response", ""),
                api_key=config.OPENAI_API_KEY
            )
            hallucination_score = hall_result.get("score", 0.0)
            # Override risk level if hallucination detected
            if hall_result.get("risk_level") == "high":
                result["hallucination_risk"] = "high"

        REQUEST_COUNT.labels(intent=result.get("intent", "unknown")).inc()
        REQUEST_LATENCY.observe(latency_ms / 1000)
        if result.get("is_emergency"):
            EMERGENCY_COUNT.inc()
        QUALITY_SCORE_HIST.observe(result.get("quality_score", 0.5))

        logger.info(
            f"Query: '{request.query[:40]}...' | "
            f"Intent: {result.get('intent')} | "
            f"Latency: {latency_ms:.0f}ms | "
            f"Hallucination: {hallucination_score:.2f}"
        )

        response_data = {
            "response": result["response"],
            "intent": result.get("intent", "unknown"),
            "is_emergency": result.get("is_emergency", False),
            "retrieval_confidence": result.get("retrieval_confidence", 0.0),
            "quality_score": result.get("quality_score", 0.0),
            "hallucination_risk": result.get("hallucination_risk", "unknown"),
            "evaluation_notes": result.get("evaluation_notes", ""),
            "agent_trace": result.get("agent_trace", []),
            "sources": result.get("sources", []),
            "latency_ms": round(latency_ms, 2),
        }

        # Cache the response
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
