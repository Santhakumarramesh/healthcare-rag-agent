"""
Simple in-memory response cache to reduce API costs.
Caches responses for identical queries within a session.
"""
import hashlib
import time
from typing import Optional, Dict, Any
from loguru import logger


class ResponseCache:
    """
    Thread-safe in-memory cache for RAG responses.
    Uses query hash as key, expires after TTL.
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Args:
            ttl_seconds: Time-to-live for cached entries (default 1 hour)
            max_size: Maximum number of entries (default 1000)
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"ResponseCache initialized: TTL={ttl_seconds}s, max_size={max_size}")

    def _hash_query(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response for query.

        Returns:
            Cached response dict or None if not found/expired
        """
        key = self._hash_query(query)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        age = time.time() - entry["timestamp"]

        if age > self.ttl_seconds:
            # Expired
            del self._cache[key]
            logger.debug(f"Cache expired for key={key}")
            return None

        logger.info(f"Cache HIT for key={key} (age={age:.1f}s)")
        return entry["response"]

    def set(self, query: str, response: Dict[str, Any]):
        """
        Store response in cache.

        Args:
            query: User query
            response: Full response dict from RAG pipeline
        """
        key = self._hash_query(query)

        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
            logger.debug(f"Cache evicted oldest entry: {oldest_key}")

        self._cache[key] = {
            "response": response,
            "timestamp": time.time(),
            "query": query[:100],  # Store truncated query for debugging
        }

        logger.info(f"Cache SET for key={key} (size={len(self._cache)})")

    def clear(self):
        """Clear all cached entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        valid_entries = sum(
            1 for entry in self._cache.values()
            if (now - entry["timestamp"]) <= self.ttl_seconds
        )

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }


# Global cache instance
response_cache = ResponseCache(ttl_seconds=1800, max_size=500)  # 30 min TTL, 500 entries
