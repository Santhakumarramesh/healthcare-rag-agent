"""
Simple token bucket rate limiter to prevent API abuse.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from loguru import logger


class RateLimiter:
    """
    Token bucket rate limiter.
    Limits requests per IP/session to prevent abuse.
    """
    
    def __init__(self, requests_per_minute: int = 20, requests_per_hour: int = 100):
        """
        Args:
            requests_per_minute: Max requests per minute per client
            requests_per_hour: Max requests per hour per client
        """
        self.rpm_limit = requests_per_minute
        self.rph_limit = requests_per_hour
        
        # Track requests: client_id -> list of timestamps
        self._requests: Dict[str, list] = defaultdict(list)
        
        logger.info(f"RateLimiter initialized: {requests_per_minute} req/min, {requests_per_hour} req/hour")
    
    def is_allowed(self, client_id: str) -> Tuple[bool, str]:
        """
        Check if client is allowed to make a request.
        
        Args:
            client_id: Unique identifier (IP, session ID, etc.)
            
        Returns:
            (allowed: bool, reason: str)
        """
        now = time.time()
        
        # Clean up old requests
        self._requests[client_id] = [
            ts for ts in self._requests[client_id]
            if now - ts < 3600  # Keep last hour
        ]
        
        requests = self._requests[client_id]
        
        # Check per-minute limit
        recent_minute = [ts for ts in requests if now - ts < 60]
        if len(recent_minute) >= self.rpm_limit:
            logger.warning(f"Rate limit exceeded (RPM) for client={client_id}")
            return False, f"Rate limit exceeded: {self.rpm_limit} requests per minute"
        
        # Check per-hour limit
        recent_hour = [ts for ts in requests if now - ts < 3600]
        if len(recent_hour) >= self.rph_limit:
            logger.warning(f"Rate limit exceeded (RPH) for client={client_id}")
            return False, f"Rate limit exceeded: {self.rph_limit} requests per hour"
        
        # Allow request
        self._requests[client_id].append(now)
        return True, ""
    
    def reset(self, client_id: str):
        """Reset rate limit for a specific client."""
        if client_id in self._requests:
            del self._requests[client_id]
            logger.info(f"Rate limit reset for client={client_id}")
    
    def stats(self) -> Dict[str, int]:
        """Get rate limiter statistics."""
        now = time.time()
        active_clients = sum(
            1 for requests in self._requests.values()
            if any(now - ts < 3600 for ts in requests)
        )
        
        return {
            "total_clients": len(self._requests),
            "active_clients_last_hour": active_clients,
            "rpm_limit": self.rpm_limit,
            "rph_limit": self.rph_limit,
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=20, requests_per_hour=100)
