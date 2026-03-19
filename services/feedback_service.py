"""
Feedback Service - Continuous Learning from User Feedback

Collects user feedback on responses to improve the system over time.
"""
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
from loguru import logger


class FeedbackService:
    """
    Collects and analyzes user feedback for continuous improvement.
    
    Features:
    - Thumbs up/down on responses
    - Quality ratings
    - Correction suggestions
    - Feedback analytics
    """
    
    def __init__(self):
        """Initialize feedback service"""
        # Store feedback: interaction_id -> feedback data
        self.feedback = {}
        
        # Analytics
        self.feedback_stats = {
            "total_feedback": 0,
            "positive": 0,
            "negative": 0,
            "avg_rating": 0.0
        }
        
        # Track problematic queries for improvement
        self.low_quality_queries = []
        
        logger.info("[FeedbackService] Initialized")
    
    def add_feedback(
        self,
        interaction_id: str,
        user_id: Optional[str],
        query: str,
        response: str,
        rating: str,  # "positive" or "negative"
        quality_score: Optional[int] = None,  # 1-5
        comment: Optional[str] = None,
        correction: Optional[str] = None
    ):
        """
        Record user feedback on a response.
        
        Args:
            interaction_id: Unique ID for the interaction
            user_id: User providing feedback
            query: Original query
            response: AI response
            rating: "positive" or "negative"
            quality_score: 1-5 rating (optional)
            comment: User comment (optional)
            correction: User's correction (optional)
        """
        feedback_data = {
            "interaction_id": interaction_id,
            "user_id": user_id,
            "query": query,
            "response": response,
            "rating": rating,
            "quality_score": quality_score,
            "comment": comment,
            "correction": correction,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback[interaction_id] = feedback_data
        
        # Update stats
        self.feedback_stats["total_feedback"] += 1
        if rating == "positive":
            self.feedback_stats["positive"] += 1
        else:
            self.feedback_stats["negative"] += 1
            # Track for improvement
            self.low_quality_queries.append({
                "query": query,
                "response": response,
                "reason": comment or "No reason provided"
            })
        
        # Update average rating
        if quality_score:
            total_rated = sum(1 for f in self.feedback.values() if f.get("quality_score"))
            sum_ratings = sum(f.get("quality_score", 0) for f in self.feedback.values())
            self.feedback_stats["avg_rating"] = sum_ratings / total_rated if total_rated > 0 else 0
        
        logger.info(f"[FeedbackService] Recorded {rating} feedback for interaction {interaction_id}")
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        total = self.feedback_stats["total_feedback"]
        positive = self.feedback_stats["positive"]
        negative = self.feedback_stats["negative"]
        
        return {
            "total_feedback": total,
            "positive_count": positive,
            "negative_count": negative,
            "positive_rate": positive / total if total > 0 else 0,
            "negative_rate": negative / total if total > 0 else 0,
            "avg_rating": round(self.feedback_stats["avg_rating"], 2),
            "low_quality_count": len(self.low_quality_queries)
        }
    
    def get_improvement_suggestions(self, limit: int = 10) -> List[Dict]:
        """
        Get queries that need improvement based on negative feedback.
        
        Returns list of problematic queries with reasons.
        """
        return self.low_quality_queries[-limit:]
    
    def get_feedback_by_query_type(self) -> Dict:
        """Analyze feedback by query type"""
        # This would integrate with the router to categorize feedback
        # For now, return basic stats
        return self.get_feedback_stats()
    
    def export_feedback_for_training(self) -> List[Dict]:
        """
        Export feedback data for model fine-tuning.
        
        Returns list of query-response pairs with quality labels.
        """
        training_data = []
        
        for feedback in self.feedback.values():
            if feedback.get("rating") == "positive" or feedback.get("quality_score", 0) >= 4:
                training_data.append({
                    "query": feedback["query"],
                    "response": feedback["response"],
                    "quality": "good",
                    "score": feedback.get("quality_score", 5)
                })
            elif feedback.get("correction"):
                training_data.append({
                    "query": feedback["query"],
                    "response": feedback["response"],
                    "corrected_response": feedback["correction"],
                    "quality": "needs_improvement",
                    "score": feedback.get("quality_score", 2)
                })
        
        return training_data


# Singleton instance
feedback_service = FeedbackService()
