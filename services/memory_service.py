"""
Patient Memory Service - Manages conversation history and patient context.

Stores and retrieves conversation history for contextual responses.
Persists sessions to SQLite so history survives restarts.
"""
import os
import json
import sqlite3
from contextlib import contextmanager
from typing import List, Dict
from datetime import datetime
from loguru import logger


# ── SQLite path (writable on HF Spaces / Docker) ──────────────────────────────
_DB_PATH = os.getenv("MEMORY_DB_PATH", "./data/memory.db")


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
    """Create tables if they don't exist."""
    with _db_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id   TEXT PRIMARY KEY,
                created_at   TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                patient_context TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS interactions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                timestamp    TEXT NOT NULL,
                query        TEXT NOT NULL,
                answer       TEXT,
                query_type   TEXT,
                confidence   REAL,
                sources_count INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);
        """)


class PatientMemoryService:
    """
    Manages session-based conversation memory with SQLite persistence.

    Stores:
    - Conversation history (queries and answers)
    - Patient context (extracted information)
    - Query patterns (for personalization)
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        try:
            _init_db()
            logger.info(f"[MemoryService] SQLite persistence enabled at {_DB_PATH}")
        except Exception as exc:
            logger.warning(f"[MemoryService] SQLite unavailable ({exc}); falling back to in-memory")
        self._fallback: Dict = {}   # used only when SQLite fails

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _ensure_session(self, session_id: str):
        """Insert a new session row if it doesn't already exist."""
        try:
            with _db_conn() as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO sessions (session_id, created_at, last_activity, patient_context)
                       VALUES (?, ?, ?, '{}')""",
                    (session_id, datetime.now().isoformat(), datetime.now().isoformat()),
                )
        except Exception as exc:
            logger.debug(f"[MemoryService] _ensure_session fallback: {exc}")

    # ── Public API ────────────────────────────────────────────────────────────

    def add_interaction(self, session_id: str, interaction: Dict):
        """Store a conversation turn."""
        try:
            self._ensure_session(session_id)
            with _db_conn() as conn:
                conn.execute(
                    """INSERT INTO interactions
                         (session_id, timestamp, query, answer, query_type, confidence, sources_count)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        session_id,
                        datetime.now().isoformat(),
                        interaction.get("query", ""),
                        interaction.get("answer", "")[:500],
                        interaction.get("query_type"),
                        interaction.get("confidence"),
                        len(interaction.get("sources", [])),
                    ),
                )
                conn.execute(
                    "UPDATE sessions SET last_activity = ? WHERE session_id = ?",
                    (datetime.now().isoformat(), session_id),
                )
                # Trim old rows beyond max_history
                conn.execute(
                    """DELETE FROM interactions WHERE id IN (
                         SELECT id FROM interactions WHERE session_id = ?
                         ORDER BY id DESC LIMIT -1 OFFSET ?
                       )""",
                    (session_id, self.max_history),
                )
        except Exception as exc:
            logger.warning(f"[MemoryService] SQLite write failed, using in-memory: {exc}")
            if session_id not in self._fallback:
                self._fallback[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "interactions": [],
                    "patient_context": {},
                }
            self._fallback[session_id]["interactions"].append(interaction)

        logger.debug(f"[MemoryService] Added interaction to session {session_id[:8]}")

    def get_recent_context(self, session_id: str, limit: int = 5) -> str:
        """Get recent conversation for context injection."""
        history = self.get_conversation_history(session_id)[-limit:]
        if not history:
            return ""
        parts = ["Previous conversation:"]
        for i, item in enumerate(history, 1):
            parts.append(f"\nQ{i}: {item.get('query', '')}")
            parts.append(f"A{i}: {str(item.get('answer', ''))[:200]}...")
        return "\n".join(parts)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get full conversation history."""
        try:
            with _db_conn() as conn:
                rows = conn.execute(
                    """SELECT timestamp, query, answer, query_type, confidence, sources_count
                       FROM interactions WHERE session_id = ? ORDER BY id ASC""",
                    (session_id,),
                ).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            logger.debug(f"[MemoryService] get_conversation_history fallback: {exc}")
            return self._fallback.get(session_id, {}).get("interactions", [])

    def update_patient_context(self, session_id: str, key: str, value):
        """Store patient-specific information."""
        try:
            self._ensure_session(session_id)
            with _db_conn() as conn:
                row = conn.execute(
                    "SELECT patient_context FROM sessions WHERE session_id = ?", (session_id,)
                ).fetchone()
                ctx = json.loads(row["patient_context"] if row else "{}")
                ctx[key] = value
                conn.execute(
                    "UPDATE sessions SET patient_context = ? WHERE session_id = ?",
                    (json.dumps(ctx), session_id),
                )
        except Exception as exc:
            logger.debug(f"[MemoryService] update_patient_context fallback: {exc}")
            self._fallback.setdefault(session_id, {}).setdefault("patient_context", {})[key] = value

    def get_patient_context(self, session_id: str) -> Dict:
        """Retrieve patient context."""
        try:
            with _db_conn() as conn:
                row = conn.execute(
                    "SELECT patient_context FROM sessions WHERE session_id = ?", (session_id,)
                ).fetchone()
            return json.loads(row["patient_context"]) if row else {}
        except Exception as exc:
            logger.debug(f"[MemoryService] get_patient_context fallback: {exc}")
            return self._fallback.get(session_id, {}).get("patient_context", {})

    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics."""
        try:
            with _db_conn() as conn:
                row = conn.execute(
                    "SELECT created_at, last_activity FROM sessions WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
                count = conn.execute(
                    "SELECT COUNT(*) as c FROM interactions WHERE session_id = ?",
                    (session_id,),
                ).fetchone()["c"]
            if not row:
                return {"exists": False, "interaction_count": 0, "query_types": {}}
            return {
                "exists": True,
                "created_at": row["created_at"],
                "last_activity": row["last_activity"],
                "interaction_count": count,
                "query_types": {},
            }
        except Exception as exc:
            logger.debug(f"[MemoryService] get_session_stats fallback: {exc}")
            fb = self._fallback.get(session_id)
            if not fb:
                return {"exists": False, "interaction_count": 0, "query_types": {}}
            return {
                "exists": True,
                "created_at": fb.get("created_at", ""),
                "last_activity": fb.get("last_activity", ""),
                "interaction_count": len(fb.get("interactions", [])),
                "query_types": {},
            }

    def clear_session(self, session_id: str):
        """Clear a session's memory."""
        try:
            with _db_conn() as conn:
                conn.execute("DELETE FROM interactions WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        except Exception as exc:
            logger.debug(f"[MemoryService] clear_session fallback: {exc}")
        self._fallback.pop(session_id, None)
        logger.info(f"[MemoryService] Cleared session {session_id[:8]}")

    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        try:
            with _db_conn() as conn:
                rows = conn.execute("SELECT session_id FROM sessions").fetchall()
            return [r["session_id"] for r in rows]
        except Exception:
            return list(self._fallback.keys())


# Singleton instance
memory_service = PatientMemoryService()
