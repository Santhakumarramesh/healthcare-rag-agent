"""
Medical Records API Router.

Endpoints for the personal Medical Record Summarizer feature:
  POST /records/upload   — ingest a PDF or text file into the session store
  POST /records/analyze  — run structured extraction on all uploaded records
  POST /records/query    — answer a question grounded in personal records
  GET  /records/files/{session_id} — list uploaded files
  DELETE /records/clear/{session_id} — wipe all records for a session
"""
import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from vectorstore.personal_store import personal_store
from agents.records_agent import extract_record_structure, answer_record_question

router = APIRouter(prefix="/records", tags=["Medical Records"])

_ALLOWED_EXTENSIONS = {".pdf", ".txt", ".text"}
_MAX_FILE_MB = 10


# ── Request / Response models ──────────────────────────────────────────────────

class RecordQueryRequest(BaseModel):
    session_id: str
    question: str


class RecordQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    latency_ms: float


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_record(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a PDF or plain-text medical record and index it for the session.
    The content is never persisted to disk — only held in-memory.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Please upload a PDF or .txt file.",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > _MAX_FILE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File is {size_mb:.1f} MB — maximum allowed is {_MAX_FILE_MB} MB.",
        )

    try:
        if suffix == ".pdf":
            chunks_stored = personal_store.add_pdf(session_id, content, file.filename)
        else:
            text = content.decode("utf-8", errors="replace")
            chunks_stored = personal_store.add_text(session_id, text, file.filename)

        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_stored": chunks_stored,
            "total_files": len(personal_store.list_files(session_id)),
            "total_chunks": personal_store.chunk_count(session_id),
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"[Records] Upload error for session {session_id[:8]}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")


@router.post("/analyze")
async def analyze_records(session_id: str = Form(...)):
    """
    Run structured extraction on all records uploaded in this session.
    Returns a JSON object with diagnoses, lab values, medications, etc.
    """
    full_text = personal_store.get_full_text(session_id)
    if not full_text:
        raise HTTPException(
            status_code=404,
            detail="No records found for this session. Please upload a file first.",
        )

    start = time.time()
    result = await extract_record_structure(full_text)
    latency_ms = (time.time() - start) * 1000

    return {**result, "latency_ms": round(latency_ms, 2)}


@router.post("/query", response_model=RecordQueryResponse)
async def query_records(request: RecordQueryRequest):
    """
    Answer a question grounded in the personal records uploaded for this session.
    """
    if personal_store.chunk_count(request.session_id) == 0:
        raise HTTPException(
            status_code=404,
            detail="No records found for this session. Please upload a file first.",
        )

    start = time.time()
    chunks = personal_store.query(request.session_id, request.question, top_k=5)
    answer = await answer_record_question(request.question, chunks)
    latency_ms = (time.time() - start) * 1000

    return RecordQueryResponse(
        answer=answer,
        sources=[
            {"source": c.metadata.get("source", "record"), "score": round(c.score, 3)}
            for c in chunks
        ],
        latency_ms=round(latency_ms, 2),
    )


@router.get("/files/{session_id}")
async def list_files(session_id: str):
    """List the files uploaded for a session and how many chunks are indexed."""
    return {
        "files": personal_store.list_files(session_id),
        "chunk_count": personal_store.chunk_count(session_id),
    }


@router.delete("/clear/{session_id}")
async def clear_records(session_id: str):
    """Wipe all in-memory records for a session."""
    personal_store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
