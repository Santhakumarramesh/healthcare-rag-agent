"""
LLM Client wrapper for structured reasoning.
"""
from __future__ import annotations
from openai import OpenAI


class OpenAILLMClient:
    """Simple OpenAI client wrapper for structured generation."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate JSON response from prompt."""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
