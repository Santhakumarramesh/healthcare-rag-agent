"""
Report analysis LLM for structured medical report explanation.
"""
from __future__ import annotations

import json
from openai import OpenAI
from typing import List, Dict, Any


class ReportLLM:
    """LLM client for medical report analysis."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_report(
        self,
        raw_text: str,
        extracted_values: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze medical report and generate structured explanation.
        
        Args:
            raw_text: Raw report text
            extracted_values: Extracted lab values
            
        Returns:
            Structured analysis with summary, explanation, concerns, next steps
        """
        prompt = f"""
You are a healthcare report explanation assistant.

Your task:
- Explain the uploaded report in simple, safe language
- Do not give a definitive diagnosis
- Mention possible concerns carefully
- Suggest appropriate next steps
- Use the extracted values when useful
- Return JSON only

Raw report text:
{raw_text[:6000]}

Extracted values:
{json.dumps(extracted_values, indent=2)}

Return JSON with exactly this schema:
{{
  "summary": "brief clinical-style summary",
  "simple_explanation": "easy explanation for a non-expert",
  "potential_concerns": ["item 1", "item 2"],
  "next_steps": ["step 1", "step 2"],
  "safety_note": "brief safety note"
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )

        return json.loads(response.choices[0].message.content)
