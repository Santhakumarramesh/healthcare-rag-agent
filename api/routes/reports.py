"""
Report Analysis API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from api.schemas.report import (
    ReportTextRequest,
    ReportAnalysisResponse,
    ReportAnalysisJobStartResponse,
    ReportAnalysisJobResponse,
)
from services.report_service import ReportService
from models.report_llm import ReportLLM
from loguru import logger

import os
import io
from uuid import uuid4
from threading import Lock

router = APIRouter(prefix="/reports", tags=["Reports"])

_JOB_LOCK = Lock()
_JOBS: dict[str, dict] = {}


def extract_text_from_upload(upload: UploadFile) -> str:
    """Extract text from uploaded file (PDF, TXT, or image)."""
    content = upload.file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    filename = (upload.filename or "").lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if not text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
            return text
        except ImportError:
            raise HTTPException(status_code=500, detail="pypdf is not installed.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    if filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            from PIL import Image
            try:
                import pytesseract
            except ImportError:
                raise HTTPException(
                    status_code=400,
                    detail="Image OCR is not available on this server. Please paste the report text or upload a PDF/TXT file."
                )
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            if not text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from image. Try pasting the text or uploading a PDF.")
            return text
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Use PDF, TXT, PNG, JPG, or JPEG."
    )


def get_report_service() -> ReportService:
    """Get report service instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "placeholder" in api_key.lower():
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")

    llm = ReportLLM(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return ReportService(llm=llm)


@router.post("/analyze", response_model=ReportAnalysisResponse)
async def analyze_uploaded_report(file: UploadFile = File(...)):
    """
    Analyze uploaded medical report (PDF, image, or text).

    Extracts structured values, generates summary, flags abnormal results.
    """
    logger.info(f"[ReportsAPI] Analyzing uploaded file: {file.filename}")

    try:
        text = extract_text_from_upload(file)
        service = get_report_service()
        result = service.analyze(text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ReportsAPI] Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-text", response_model=ReportAnalysisResponse)
async def analyze_text_report(payload: ReportTextRequest):
    """
    Analyze pasted medical report text.

    Extracts structured values, generates summary, flags abnormal results.
    """
    logger.info(f"[ReportsAPI] Analyzing pasted text ({len(payload.text)} chars)")

    try:
        service = get_report_service()
        result = service.analyze(payload.text)
        return result
    except Exception as e:
        logger.error(f"[ReportsAPI] Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _set_job(job_id: str, *, status: str, result: dict | None = None, error: str | None = None) -> None:
    with _JOB_LOCK:
        job = _JOBS.get(job_id)
        if not job:
            return
        job["status"] = status
        job["result"] = result
        job["error"] = error


def _run_analyze_text_job(job_id: str, text: str) -> None:
    """Run report analysis in the background (in-process job registry)."""
    _set_job(job_id, status="processing")
    try:
        service = get_report_service()
        result = service.analyze(text)
        _set_job(job_id, status="completed", result=result)
        logger.success(f"[ReportsAPI] Async job completed: {job_id}")
    except Exception as e:
        logger.error(f"[ReportsAPI] Async job failed: {job_id} ({e})")
        _set_job(job_id, status="failed", error=str(e))


@router.post("/analyze-text-async", response_model=ReportAnalysisJobStartResponse)
async def analyze_text_report_async(payload: ReportTextRequest, background_tasks: BackgroundTasks):
    """
    Async variant of `/reports/analyze-text`.
    Returns immediately with a `job_id`; clients can poll `GET /reports/jobs/{job_id}`.
    """
    job_id = str(uuid4())
    with _JOB_LOCK:
        _JOBS[job_id] = {"status": "pending", "result": None, "error": None}

    background_tasks.add_task(_run_analyze_text_job, job_id, payload.text)
    return ReportAnalysisJobStartResponse(job_id=job_id)


@router.get("/jobs/{job_id}", response_model=ReportAnalysisJobResponse)
async def get_analysis_job(job_id: str):
    with _JOB_LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return ReportAnalysisJobResponse(
            job_id=job_id,
            status=job["status"],
            result=job.get("result"),
            error=job.get("error"),
        )
