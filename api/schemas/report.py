"""
Report API schemas.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ReportTextRequest(BaseModel):
    """Request for text-based report analysis."""
    text: str = Field(..., min_length=10)


class ExtractedValue(BaseModel):
    """Extracted lab value."""
    name: str
    value: str
    unit: Optional[str] = None
    reference: Optional[str] = None
    flag: Optional[str] = None


class SourceItem(BaseModel):
    """Source citation."""
    title: str
    score: float
    category: Optional[str] = None
    preview: str


class ReportAnalysisResponse(BaseModel):
    """Report analysis response."""
    summary: str
    simple_explanation: str
    potential_concerns: List[str]
    next_steps: List[str]
    confidence: float
    extracted_values: List[ExtractedValue]
    sources: List[SourceItem]
    safety_note: str
    report_type: Optional[str] = "Medical Report"


class ReportAnalysisJobStartResponse(BaseModel):
    """Response returned immediately for async report analysis jobs."""

    job_id: str


class ReportAnalysisJobResponse(BaseModel):
    """Job status/result response for async report analysis."""

    job_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    result: Optional[ReportAnalysisResponse] = None
    error: Optional[str] = None
