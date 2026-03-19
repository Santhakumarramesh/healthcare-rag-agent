"""
Report Analysis API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas.report import ReportTextRequest, ReportAnalysisResponse
from services.report_service import ReportService
from models.report_llm import ReportLLM
from loguru import logger

import os
import io

router = APIRouter(prefix="/reports", tags=["Reports"])


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
            import pytesseract

            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            if not text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from image.")
            return text
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="OCR dependencies missing. Install pillow and pytesseract."
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read image: {e}")

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
