"""
Query Router Agent - Routes queries to appropriate handlers.

Classifies incoming queries and determines the best processing path.
"""
import sys
from pathlib import Path
from enum import Enum
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


class QueryType(Enum):
    """Types of medical queries"""
    SYMPTOM_CHECK = "symptom_check"
    REPORT_EXPLANATION = "report_explanation"
    DRUG_INFO = "drug_info"
    EMERGENCY = "emergency"
    GENERAL_QA = "general_qa"
    PREVENTIVE_CARE = "preventive_care"
    FOLLOW_UP = "follow_up"


class RouterAgent:
    """Routes queries to appropriate handlers based on query type and urgency"""

    ROUTER_PROMPT = """You are a medical query classifier. Analyze the user's query and classify it into ONE category.

Categories:
- symptom_check: User describing symptoms or asking about symptoms
- report_explanation: Asking about lab results, medical reports, test results
- drug_info: Questions about medications, drugs, prescriptions
- emergency: Urgent medical situation requiring immediate attention
- general_qa: General medical knowledge questions
- preventive_care: Prevention, lifestyle, wellness, diet questions
- follow_up: Follow-up question based on previous conversation

Respond with ONLY the category name (lowercase, underscore-separated)."""

    EMERGENCY_KEYWORDS = [
        "emergency", "urgent", "severe", "critical", "chest pain",
        "difficulty breathing", "can't breathe", "heart attack",
        "stroke", "seizure", "unconscious", "bleeding heavily",
        "severe pain", "suicide", "overdose"
    ]

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0
        )
        logger.info("[RouterAgent] Initialized")

    async def route(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Route a query to the appropriate handler.

        Args:
            query: User's query text
            context: Optional context (previous queries, patient info, etc.)

        Returns:
            Dict with routing information
        """
        # Quick emergency check
        is_urgent = self._check_emergency(query)

        if is_urgent:
            logger.warning(f"[RouterAgent] EMERGENCY query detected: {query[:100]}")
            return {
                "type": QueryType.EMERGENCY.value,
                "is_urgent": True,
                "confidence": 1.0,
                "reason": "Emergency keywords detected",
                "handler": "emergency_handler"
            }

        # Check if it's a follow-up based on context
        if context and context.get("has_previous_interaction"):
            # Simple heuristic: short queries are likely follow-ups
            if len(query.split()) < 10:
                return {
                    "type": QueryType.FOLLOW_UP.value,
                    "is_urgent": False,
                    "confidence": 0.8,
                    "reason": "Short query with conversation history",
                    "handler": "rag_pipeline"
                }

        # Use LLM for classification
        try:
            messages = [
                SystemMessage(content=self.ROUTER_PROMPT),
                HumanMessage(content=f"Query: {query}")
            ]

            response = await self.llm.ainvoke(messages)
            query_type = response.content.strip().lower().replace(" ", "_")

            # Validate query type
            try:
                QueryType(query_type)
            except ValueError:
                logger.warning(f"[RouterAgent] Invalid query type '{query_type}', defaulting to general_qa")
                query_type = QueryType.GENERAL_QA.value

            # Determine handler
            handler = self._get_handler(query_type)

            logger.info(f"[RouterAgent] Routed query to: {query_type} (handler: {handler})")

            return {
                "type": query_type,
                "is_urgent": False,
                "confidence": 0.85,
                "reason": f"LLM classified as {query_type}",
                "handler": handler
            }

        except Exception as e:
            logger.error(f"[RouterAgent] Routing failed: {e}")
            return {
                "type": QueryType.GENERAL_QA.value,
                "is_urgent": False,
                "confidence": 0.5,
                "reason": f"Routing error, defaulting to general_qa: {str(e)}",
                "handler": "rag_pipeline"
            }

    def _check_emergency(self, query: str) -> bool:
        """Quick check for emergency keywords"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.EMERGENCY_KEYWORDS)

    def _get_handler(self, query_type: str) -> str:
        """Map query type to handler"""
        handler_map = {
            QueryType.SYMPTOM_CHECK.value: "rag_pipeline",
            QueryType.REPORT_EXPLANATION.value: "report_analyzer",
            QueryType.DRUG_INFO.value: "rag_pipeline",
            QueryType.EMERGENCY.value: "emergency_handler",
            QueryType.GENERAL_QA.value: "rag_pipeline",
            QueryType.PREVENTIVE_CARE.value: "rag_pipeline",
            QueryType.FOLLOW_UP.value: "rag_pipeline"
        }
        return handler_map.get(query_type, "rag_pipeline")
