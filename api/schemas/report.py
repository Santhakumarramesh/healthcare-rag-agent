"""
Report API schemas.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


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
