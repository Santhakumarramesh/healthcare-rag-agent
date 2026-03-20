"""
AI Insights Service
Generates proactive, specific health insights based on patient data.
Every insight must include: what_changed, why_it_matters, what_to_do
"""
from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger


class AIInsightsService:

    def generate_insights(self, user_id: str, patient_data: dict) -> List[dict]:
        """
        Generate actionable insights from patient's current health data.
        Returns list of insight dicts.
        """
        insights = []

        # Refill running low
        for rx in patient_data.get("prescriptions", []):
            days_supply_left = self._days_supply_remaining(rx)
            if days_supply_left is not None and days_supply_left <= 7:
                insights.append({
                    "category": "refill",
                    "title": f"{rx['medication_name']} refill due soon",
                    "what_changed": f"You have approximately {days_supply_left} days of {rx['medication_name']} remaining.",
                    "why_it_matters": "Running out of medication without a refill can disrupt your treatment.",
                    "what_to_do": "Request a refill now to avoid a gap in your medication.",
                    "severity": "medium" if days_supply_left > 3 else "high",
                })

        # Unresolved report flags
        for report in patient_data.get("reports", []):
            if report.get("has_flags") and not report.get("flags_reviewed"):
                insights.append({
                    "category": "follow_up",
                    "title": "Unresolved findings in recent report",
                    "what_changed": f"Your {report.get('report_type', 'recent')} report still has unreviewed abnormal values.",
                    "why_it_matters": "Unresolved findings may indicate a condition that needs attention.",
                    "what_to_do": "Book a consultation to discuss these findings with a doctor.",
                    "severity": "high",
                })

        # Activity drop
        activity = patient_data.get("activity_trend", {})
        if activity.get("drop_pct", 0) >= 30:
            insights.append({
                "category": "activity",
                "title": "Significant drop in physical activity",
                "what_changed": f"Your activity level dropped by {activity['drop_pct']}% compared to last week.",
                "why_it_matters": "Reduced activity can worsen chronic conditions and impact mental health.",
                "what_to_do": "Try to add a short 15-minute walk to your day, even if you don't feel well.",
                "severity": "medium",
            })

        return insights

    def _days_supply_remaining(self, rx: dict) -> int | None:
        expiry = rx.get("expiry_date")
        if not expiry:
            return None
        try:
            expiry_dt = datetime.fromisoformat(str(expiry))
            return max(0, (expiry_dt - datetime.utcnow()).days)
        except Exception:
            return None


ai_insights_service = AIInsightsService()
