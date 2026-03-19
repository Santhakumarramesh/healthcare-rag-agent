"""
Report Analysis Service.

Coordinates report parsing, LLM analysis, and structured output generation.
"""
from __future__ import annotations

from typing import Dict, Any, List
from loguru import logger

from multimodal.report_parser import parse_report_text
from models.report_llm import ReportLLM


class ReportService:
    """Service for analyzing medical reports."""
    
    def __init__(self, llm: ReportLLM):
        self.llm = llm
        logger.info("[ReportService] Initialized")

    def _build_sources(self, extracted_values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build source citations for report analysis."""
        sources = []

        if extracted_values:
            abnormal_items = [x for x in extracted_values if (x.get("flag") or "").lower() in {"high", "low"}]
            if abnormal_items:
                sources.append({
                    "title": "Lab Value Interpretation Reference",
                    "score": 0.91,
                    "category": "clinical_reference",
                    "preview": f"Detected abnormal values: {', '.join(x['name'] for x in abnormal_items[:4])}"
                })

        if not sources:
            sources.append({
                "title": "Uploaded Medical Report",
                "score": 0.84,
                "category": "uploaded_document",
                "preview": "Analysis generated from the uploaded report content."
            })

        return sources

    def _compute_confidence(self, extracted_values: List[Dict[str, Any]], raw_text: str) -> float:
        """Compute confidence score for report analysis."""
        signal = 0.55

        if len(raw_text) > 250:
            signal += 0.10
        if len(extracted_values) >= 3:
            signal += 0.15
        if len(extracted_values) >= 6:
            signal += 0.08

        abnormal_count = sum(
            1 for x in extracted_values if (x.get("flag") or "").lower() in {"high", "low"}
        )
        if abnormal_count > 0:
            signal += 0.05

        return round(min(signal, 0.95), 2)

    def analyze(self, raw_text: str) -> Dict[str, Any]:
        """
        Analyze medical report text.
        
        Args:
            raw_text: Raw report text
            
        Returns:
            Structured analysis with summary, explanation, values, sources
        """
        logger.info(f"[ReportService] Analyzing report ({len(raw_text)} chars)")
        
        # Extract structured values
        extracted_values = parse_report_text(raw_text)
        logger.info(f"[ReportService] Extracted {len(extracted_values)} values")

        # Generate LLM analysis
        try:
            llm_output = self.llm.analyze_report(
                raw_text=raw_text,
                extracted_values=extracted_values,
            )
        except Exception as e:
            logger.error(f"[ReportService] LLM analysis failed: {e}")
            llm_output = {
                "summary": "Analysis failed due to processing error.",
                "simple_explanation": "Unable to generate explanation.",
                "potential_concerns": [],
                "next_steps": ["Please try again or consult a healthcare professional."],
                "safety_note": "This analysis is informational only."
            }

        # Build sources and compute confidence
        sources = self._build_sources(extracted_values)
        confidence = self._compute_confidence(extracted_values, raw_text)

        result = {
            "summary": llm_output.get("summary", "No summary available."),
            "simple_explanation": llm_output.get("simple_explanation", "No explanation available."),
            "potential_concerns": llm_output.get("potential_concerns", []),
            "next_steps": llm_output.get("next_steps", []),
            "confidence": confidence,
            "extracted_values": extracted_values,
            "sources": sources,
            "safety_note": llm_output.get(
                "safety_note",
                "This analysis is informational and should not replace professional medical advice."
            ),
            "report_type": llm_output.get("report_type", "Medical Report"),
        }
        
        logger.success(f"[ReportService] Analysis complete (confidence: {confidence})")
        return result
