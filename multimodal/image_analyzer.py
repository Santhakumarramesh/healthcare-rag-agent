"""
Medical Image Analyzer - Processes medical images using vision models.

Supports:
- Lab report photos
- Prescription images
- Medical document scans
- X-ray/scan images (basic interpretation)
"""
import sys
import base64
from pathlib import Path
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


class MedicalImageAnalyzer:
    """
    Analyzes medical images using GPT-4o vision capabilities.

    Supports:
    - Text extraction from images (OCR)
    - Medical document analysis
    - Basic visual interpretation
    """

    MEDICAL_IMAGE_PROMPT = """You are a medical document analyzer with vision capabilities.

Analyze this medical image and extract ALL visible information.

For lab reports/medical documents:
1. Extract ALL text visible in the image
2. Identify document type (lab report, prescription, discharge summary, etc.)
3. Extract patient information (name, date, provider)
4. Extract all lab values, medications, diagnoses
5. Note any abnormal flags or warnings

For medical images (X-ray, scan, etc.):
1. Describe what type of image it is
2. Note visible anatomical structures
3. Identify any obvious abnormalities
4. State that professional radiologist review is required

IMPORTANT:
- Extract text EXACTLY as written
- Do NOT make diagnoses
- Do NOT interpret clinical significance beyond what's explicitly stated
- Always recommend professional medical review

Format your response clearly with sections."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4o",  # Vision model
            temperature=0
        )
        logger.info("[ImageAnalyzer] Initialized with GPT-4o vision")

    async def analyze_image(
        self,
        image_bytes: bytes,
        query: Optional[str] = None,
        image_type: str = "medical_document"
    ) -> Dict:
        """
        Analyze a medical image.

        Args:
            image_bytes: Image file bytes
            query: Optional specific question about the image
            image_type: Type of image (medical_document, xray, scan, etc.)

        Returns:
            Dict with extracted text and analysis
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Determine image format
            image_format = "jpeg"
            if image_bytes[:4] == b'\x89PNG':
                image_format = "png"
            elif image_bytes[:2] == b'\xff\xd8':
                image_format = "jpeg"

            # Build prompt
            if query:
                prompt = f"{self.MEDICAL_IMAGE_PROMPT}\n\nSpecific question: {query}"
            else:
                prompt = self.MEDICAL_IMAGE_PROMPT

            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{base64_image}",
                            "detail": "high"  # High detail for medical images
                        }
                    }
                ]
            )

            # Call vision model
            response = await self.llm.ainvoke([message])
            extracted_content = response.content.strip()

            logger.info(f"[ImageAnalyzer] Successfully analyzed {image_type} image")

            return {
                "success": True,
                "extracted_text": extracted_content,
                "image_type": image_type,
                "analysis": extracted_content,
                "confidence": 0.85,
                "model": "gpt-4o-vision"
            }

        except Exception as e:
            logger.error(f"[ImageAnalyzer] Analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "analysis": f"Failed to analyze image: {str(e)}",
                "confidence": 0.0
            }

    async def extract_text_only(self, image_bytes: bytes) -> str:
        """
        Extract text from image (OCR).

        Args:
            image_bytes: Image file bytes

        Returns:
            Extracted text
        """
        result = await self.analyze_image(
            image_bytes,
            query="Extract all visible text from this image exactly as written.",
            image_type="text_extraction"
        )
        return result.get("extracted_text", "")


# Singleton instance
image_analyzer = MedicalImageAnalyzer()
