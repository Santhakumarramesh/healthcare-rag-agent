"""
Feedback Service - Continuous Learning from User Feedback

Collects user feedback on responses to improve the system over time.
Persists all feedback to SQLite so data survives restarts.
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


# ── SQLite path ───────────────────────────────────────────────────────────────
_DB_PATH = os.getenv("FEEDBACK_DB_PATH", "./data/feedback.db")


@contextmanager
def _db_conn():
    """Thread-safe SQLite context manager."""
    os.makedirs(os.path.dirname(_DB_PATH) if os.path.dirname(_DB_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_db():
    """Create table if it doesn't exist."""
    with _db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                interaction_id TEXT PRIMARY KEY,
                user_id        TEXT,
                query          TEXT NOT NULL,
                response       TEXT,
                rating         TEXT NOT NULL,
                quality_score  INTEGER,
                comment        TEXT,
                correction     TEXT,
                timestamp      TEXT NOT NULL
            )
        """)


class FeedbackService:
    """
    Collects and analyses user feedback for continuous improvement.

    Features:
    - Thumbs up/down on responses
    - Quality ratings (1–5)
    - Correction suggestions
    - Feedback analytics
    - SQLite-backed persistence (falls back to in-memory on DB error)
    """

    def __init__(self):
        try:
            _init_db()
            logger.info(f"[FeedbackService] SQLite persistence enabled at {_DB_PATH}")
        except Exception as exc:
            logger.warning(f"[FeedbackService] SQLite unavailable ({exc}); using in-memory")
        # In-memory fallback
        self._fallback: Dict = {}
        logger.info("[FeedbackService] Initialized")

    # ── Write ─────────────────────────────────────────────────────────────────

    def add_feedback(
        self,
        interaction_id: str,
        user_id: Optional[str],
        query: str,
        response: str,
        rating: str,            # "positive" | "negative"
        quality_score: Optional[int] = None,   # 1–5
        comment: Optional[str] = None,
        correction: Optional[str] = None,
    ):
        """Record user feedback on a response."""
        ts = datetime.now().isoformat()
        try:
            with _db_conn() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO feedback
                         (interaction_id, user_id, query, response, rating,
                          quality_score, comment, correction, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        interaction_id,
                        user_id,
                        query,
                        response[:500] if response else "",
                        rating,
                        quality_score,
                        comment,
                        correction,
                        ts,
                    ),
                )
        except Exception as exc:
            logger.warning(f"[FeedbackService] SQLite write failed: {exc} — using in-memory")
            self._fallback[interaction_id] = {
                "interaction_id": interaction_id,
                "user_id": user_id,
                "query": query,
                "response": (response or "")[:500],
                "rating": rating,
                "quality_score": quality_score,
                "comment": comment,
                "correction": correction,
                "timestamp": ts,
            }

        logger.info(f"[FeedbackService] Recorded {rating} feedback for {interaction_id}")

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_feedback_stats(self) -> Dict:
        """Return aggregate feedback statistics."""
        try:
            with _db_conn() as conn:
                row = conn.execute(
                    """SELECT
                         COUNT(*)                                      AS total,
                         SUM(CASE WHEN rating='positive' THEN 1 END)  AS positive,
                         SUM(CASE WHEN rating='negative' THEN 1 END)  AS negative,
                         AVG(CAST(quality_score AS REAL))              AS avg_rating
                       FROM feedback"""
                ).fetchone()
            total    = row["total"] or 0
            positive = row["positive"] or 0
            negative = row["negative"] or 0
            avg_r    = round(float(row["avg_rating"] or 0), 2)
        except Exception:
            # Fallback stats from in-memory dict
            items    = list(self._fallback.values())
            total    = len(items)
            positive = sum(1 for i in items if i["rating"] == "positive")
            negative = total - positive
            scores   = [i["quality_score"] for i in items if i.get("quality_score")]
            avg_r    = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "total_feedback":  total,
            "positive_count":  positive,
            "negative_count":  negative,
            "positive_rate":   round(positive / total, 3) if total else 0,
            "negative_rate":   round(negative / total, 3) if total else 0,
            "avg_rating":      avg_r,
        }

    def get_improvement_suggestions(self, limit: int = 10) -> List[Dict]:
        """Return the most-recent negative feedback entries."""
        try:
            with _db_conn() as conn:
                rows = conn.execute(
                    """SELECT query, response, comment FROM feedback
                       WHERE rating='negative' ORDER BY timestamp DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            items = [i for i in self._fallback.values() if i["rating"] == "negative"]
            return items[-limit:]

    def export_feedback_for_training(self) -> List[Dict]:
        """Export positive / corrected pairs for fine-tuning."""
        try:
            with _db_conn() as conn:
                rows = conn.execute(
                    """SELECT query, response, correction, quality_score, rating
                       FROM feedback
                       WHERE rating='positive' OR quality_score >= 4 OR correction IS NOT NULL"""
                ).fetchall()
            items = [dict(r) for r in rows]
        except Exception:
            items = list(self._fallback.values())

        training_data = []
        for fb in items:
            if fb.get("rating") == "positive" or (fb.get("quality_score") or 0) >= 4:
                training_data.append({
                    "query":    fb["query"],
                    "response": fb["response"],
                    "quality":  "good",
                    "score":    fb.get("quality_score") or 5,
                })
            elif fb.get("correction"):
                training_data.append({
                    "query":              fb["query"],
                    "response":           fb["response"],
                    "corrected_response": fb["correction"],
                    "quality":            "needs_improvement",
                    "score":              fb.get("quality_score") or 2,
                })
        return training_data


# Singleton instance
feedback_service = FeedbackService()
