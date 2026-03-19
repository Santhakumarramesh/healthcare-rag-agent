"""
Patient Memory Service - Manages conversation history and patient context.

Stores and retrieves conversation history for contextual responses.
"""
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
from loguru import logger


class PatientMemoryService:
    """
    Manages session-based conversation memory.
    
    Stores:
    - Conversation history (queries and answers)
    - Patient context (extracted information)
    - Query patterns (for personalization)
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize memory service.
        
        Args:
            max_history: Maximum number of interactions to keep per session
        """
        self.sessions = {}  # session_id -> session data
        self.max_history = max_history
        logger.info(f"[MemoryService] Initialized with max_history={max_history}")
    
    def add_interaction(self, session_id: str, interaction: Dict):
        """
        Store a conversation turn.
        
        Args:
            session_id: Unique session identifier
            interaction: Dict with query, answer, metadata
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "interactions": [],
                "patient_context": {},
                "query_types": defaultdict(int)
            }
        
        # Add interaction
        self.sessions[session_id]["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "query": interaction.get("query", ""),
            "answer": interaction.get("answer", "")[:500],  # Truncate long answers
            "query_type": interaction.get("query_type"),
            "confidence": interaction.get("confidence"),
            "sources_count": len(interaction.get("sources", []))
        })
        
        # Update query type counter
        if interaction.get("query_type"):
            self.sessions[session_id]["query_types"][interaction["query_type"]] += 1
        
        # Update last activity
        self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        # Trim history if needed
        if len(self.sessions[session_id]["interactions"]) > self.max_history:
            self.sessions[session_id]["interactions"] = \
                self.sessions[session_id]["interactions"][-self.max_history:]
        
        logger.debug(f"[MemoryService] Added interaction to session {session_id[:8]}")
    
    def get_recent_context(self, session_id: str, limit: int = 5) -> str:
        """
        Get recent conversation for context.
        
        Args:
            session_id: Session identifier
            limit: Number of recent interactions to include
        
        Returns:
            Formatted conversation history
        """
        if session_id not in self.sessions:
            return ""
        
        recent = self.sessions[session_id]["interactions"][-limit:]
        
        if not recent:
            return ""
        
        context_parts = ["Previous conversation:"]
        for i, interaction in enumerate(recent, 1):
            context_parts.append(f"\nQ{i}: {interaction['query']}")
            context_parts.append(f"A{i}: {interaction['answer'][:200]}...")
        
        return "\n".join(context_parts)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get full conversation history for display.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of interaction dictionaries
        """
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]["interactions"]
    
    def update_patient_context(self, session_id: str, key: str, value: any):
        """
        Store patient-specific information.
        
        Args:
            session_id: Session identifier
            key: Context key (e.g., 'age', 'conditions', 'medications')
            value: Context value
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "interactions": [],
                "patient_context": {},
                "query_types": defaultdict(int)
            }
        
        self.sessions[session_id]["patient_context"][key] = value
        logger.debug(f"[MemoryService] Updated context for session {session_id[:8]}: {key}")
    
    def get_patient_context(self, session_id: str) -> Dict:
        """
        Retrieve patient context.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Patient context dictionary
        """
        if session_id in self.sessions:
            return self.sessions[session_id]["patient_context"]
        return {}
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get session statistics.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session statistics
        """
        if session_id not in self.sessions:
            return {
                "exists": False,
                "interaction_count": 0,
                "query_types": {}
            }
        
        session = self.sessions[session_id]
        return {
            "exists": True,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "interaction_count": len(session["interactions"]),
            "query_types": dict(session["query_types"]),
            "has_patient_context": bool(session["patient_context"])
        }
    
    def clear_session(self, session_id: str):
        """
        Clear a session's memory.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"[MemoryService] Cleared session {session_id[:8]}")
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs"""
        return list(self.sessions.keys())


# Singleton instance
memory_service = PatientMemoryService()
