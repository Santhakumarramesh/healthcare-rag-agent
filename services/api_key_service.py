"""
API Key Management Service - External API access control.

Features:
- API key generation
- Key validation
- Rate limiting per key
- Usage tracking
"""
import secrets
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger


class APIKeyService:
    """
    Manages API keys for external integrations.

    Features:
    - Generate secure API keys
    - Validate keys
    - Track usage
    - Rate limiting
    """

    def __init__(self):
        """Initialize API key service"""
        # API key storage: key -> metadata
        self.keys: Dict[str, Dict] = {}

        # Usage tracking: key -> list of timestamps
        self.usage: Dict[str, List[datetime]] = defaultdict(list)

        logger.info("[APIKeyService] Initialized")

    def generate_key(
        self,
        user_id: str,
        name: str,
        rate_limit: int = 1000,  # requests per hour
        expires_days: Optional[int] = None
    ) -> Dict:
        """
        Generate new API key.

        Args:
            user_id: User ID owning the key
            name: Descriptive name for the key
            rate_limit: Max requests per hour
            expires_days: Days until expiration (None = never expires)

        Returns:
            API key metadata with the key
        """
        # Generate secure key
        api_key = f"hc_{secrets.token_urlsafe(32)}"

        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()

        # Store key metadata
        self.keys[api_key] = {
            "key": api_key,
            "user_id": user_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "rate_limit": rate_limit,
            "total_requests": 0,
            "last_used": None,
            "active": True
        }

        logger.success(f"[APIKeyService] Generated key for user {user_id}: {name}")

        return self.keys[api_key].copy()

    def validate_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate API key.

        Args:
            api_key: API key to validate

        Returns:
            Key metadata if valid, None otherwise
        """
        key_data = self.keys.get(api_key)

        if not key_data:
            logger.warning("[APIKeyService] Invalid API key")
            return None

        if not key_data["active"]:
            logger.warning(f"[APIKeyService] Inactive API key: {key_data['name']}")
            return None

        # Check expiration
        if key_data["expires_at"]:
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"[APIKeyService] Expired API key: {key_data['name']}")
                return None

        # Check rate limit
        if not self._check_rate_limit(api_key, key_data["rate_limit"]):
            logger.warning(f"[APIKeyService] Rate limit exceeded: {key_data['name']}")
            return None

        # Update usage
        self._record_usage(api_key)

        return key_data.copy()

    def _check_rate_limit(self, api_key: str, rate_limit: int) -> bool:
        """
        Check if key is within rate limit.

        Args:
            api_key: API key
            rate_limit: Max requests per hour

        Returns:
            True if within limit, False otherwise
        """
        # Get usage in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_usage = [
            ts for ts in self.usage[api_key]
            if ts > one_hour_ago
        ]

        return len(recent_usage) < rate_limit

    def _record_usage(self, api_key: str):
        """Record API key usage"""
        now = datetime.now()

        # Add to usage log
        self.usage[api_key].append(now)

        # Keep only last 24 hours
        one_day_ago = now - timedelta(days=1)
        self.usage[api_key] = [
            ts for ts in self.usage[api_key]
            if ts > one_day_ago
        ]

        # Update key metadata
        self.keys[api_key]["total_requests"] += 1
        self.keys[api_key]["last_used"] = now.isoformat()

    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke API key.

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked, False if not found
        """
        if api_key not in self.keys:
            return False

        self.keys[api_key]["active"] = False
        logger.info(f"[APIKeyService] Revoked key: {self.keys[api_key]['name']}")

        return True

    def list_keys(self, user_id: str) -> List[Dict]:
        """
        List all keys for a user.

        Args:
            user_id: User ID

        Returns:
            List of key metadata (without actual keys)
        """
        user_keys = []

        for key_data in self.keys.values():
            if key_data["user_id"] == user_id:
                # Return metadata without the actual key
                safe_data = key_data.copy()
                safe_data["key"] = f"{safe_data['key'][:10]}..."
                user_keys.append(safe_data)

        return user_keys

    def get_usage_stats(self, api_key: str) -> Dict:
        """
        Get usage statistics for a key.

        Args:
            api_key: API key

        Returns:
            Usage statistics
        """
        if api_key not in self.keys:
            return {}

        key_data = self.keys[api_key]

        # Calculate usage in different time windows
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)

        usage_last_hour = len([ts for ts in self.usage[api_key] if ts > one_hour_ago])
        usage_last_day = len([ts for ts in self.usage[api_key] if ts > one_day_ago])

        return {
            "key_name": key_data["name"],
            "total_requests": key_data["total_requests"],
            "last_used": key_data["last_used"],
            "usage_last_hour": usage_last_hour,
            "usage_last_day": usage_last_day,
            "rate_limit": key_data["rate_limit"],
            "remaining_hourly": key_data["rate_limit"] - usage_last_hour,
            "active": key_data["active"]
        }


# Singleton instance
api_key_service = APIKeyService()
