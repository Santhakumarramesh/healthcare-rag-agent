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
from fastapi import FastAPI, HTTPException
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

    start_time = time.time()
    try:
        result = await pipeline.run(request.query)
        latency_ms = (time.time() - start_time) * 1000

        REQUEST_COUNT.labels(intent=result.get("intent", "unknown")).inc()
        REQUEST_LATENCY.observe(latency_ms / 1000)
        if result.get("is_emergency"):
            EMERGENCY_COUNT.inc()
        QUALITY_SCORE_HIST.observe(result.get("quality_score", 0.5))

        logger.info(
            f"Query: '{request.query[:40]}...' | "
            f"Intent: {result.get('intent')} | "
            f"Latency: {latency_ms:.0f}ms"
        )

        return ChatResponse(
            response=result["response"],
            intent=result.get("intent", "unknown"),
            is_emergency=result.get("is_emergency", False),
            retrieval_confidence=result.get("retrieval_confidence", 0.0),
            quality_score=result.get("quality_score", 0.0),
            hallucination_risk=result.get("hallucination_risk", "unknown"),
            evaluation_notes=result.get("evaluation_notes", ""),
            agent_trace=result.get("agent_trace", []),
            sources=result.get("sources", []),
            latency_ms=round(latency_ms, 2),
        )
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT,
                reload=config.APP_ENV == "development")
