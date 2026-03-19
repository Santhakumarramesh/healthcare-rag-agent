"""
Admin API Router - System management endpoints.
"""
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.parent))
from services.auth_service import UserRole
from services.audit_service import audit_service, AuditEventType
from services.api_key_service import api_key_service
from api.auth import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


# Request/Response Models
class APIKeyCreateRequest(BaseModel):
    name: str
    rate_limit: int = 1000
    expires_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    key: str
    user_id: str
    name: str
    created_at: str
    expires_at: Optional[str]
    rate_limit: int
    total_requests: int
    last_used: Optional[str]
    active: bool


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    user: dict = Depends(require_role(UserRole.CLINICIAN))
):
    """
    Create new API key.

    Requires: Clinician or Admin role
    """
    key_data = api_key_service.generate_key(
        user_id=user["user_id"],
        name=request.name,
        rate_limit=request.rate_limit,
        expires_days=request.expires_days
    )

    # Log API key creation
    audit_service.log_event(
        event_type=AuditEventType.API_KEY_CREATED,
        user_id=user["user_id"],
        user_email=user["email"],
        user_role=user["role"],
        action=f"API key created: {request.name}",
        details={"key_name": request.name, "rate_limit": request.rate_limit},
        success=True
    )

    return APIKeyResponse(**key_data)


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(user: dict = Depends(require_role(UserRole.CLINICIAN))):
    """
    List user's API keys.

    Requires: Clinician or Admin role
    """
    keys = api_key_service.list_keys(user["user_id"])
    return [APIKeyResponse(**k) for k in keys]


@router.delete("/api-keys/{api_key}")
async def revoke_api_key(
    api_key: str,
    user: dict = Depends(require_role(UserRole.CLINICIAN))
):
    """
    Revoke API key.

    Requires: Clinician or Admin role
    """
    success = api_key_service.revoke_key(api_key)

    if not success:
        return {"message": "API key not found"}

    # Log API key revocation
    audit_service.log_event(
        event_type=AuditEventType.API_KEY_REVOKED,
        user_id=user["user_id"],
        user_email=user["email"],
        user_role=user["role"],
        action="API key revoked",
        details={"api_key_prefix": api_key[:10]},
        success=True
    )

    return {"message": "API key revoked successfully"}


@router.get("/api-keys/{api_key}/usage")
async def get_api_key_usage(
    api_key: str,
    user: dict = Depends(require_role(UserRole.CLINICIAN))
):
    """
    Get API key usage statistics.

    Requires: Clinician or Admin role
    """
    stats = api_key_service.get_usage_stats(api_key)

    if not stats:
        return {"message": "API key not found"}

    return stats


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    event_type: Optional[str] = None,
    user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Get audit logs.

    Requires: Admin role
    """
    logs = audit_service.get_logs(
        event_type=event_type,
        limit=limit
    )

    return {
        "logs": logs,
        "count": len(logs)
    }


@router.get("/audit-logs/user/{user_id}")
async def get_user_audit_logs(
    user_id: str,
    limit: int = 50,
    user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Get audit logs for specific user.

    Requires: Admin role
    """
    logs = audit_service.get_user_activity(user_id, limit=limit)

    return {
        "user_id": user_id,
        "logs": logs,
        "count": len(logs)
    }


@router.get("/audit-logs/security")
async def get_security_logs(
    limit: int = 100,
    user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Get security-related audit logs.

    Requires: Admin role
    """
    logs = audit_service.get_security_events(limit=limit)

    return {
        "logs": logs,
        "count": len(logs)
    }


@router.get("/audit-logs/stats")
async def get_audit_stats(user: dict = Depends(require_role(UserRole.ADMIN))):
    """
    Get audit log statistics.

    Requires: Admin role
    """
    return audit_service.get_statistics()


@router.get("/system/health")
async def get_system_health(user: dict = Depends(require_role(UserRole.ADMIN))):
    """
    Get detailed system health.

    Requires: Admin role
    """
    audit_stats = audit_service.get_statistics()

    return {
        "status": "healthy",
        "audit_logs": {
            "total": audit_stats["total_logs"],
            "recent_activity": audit_stats["recent_activity_count"],
            "unique_users": audit_stats["unique_users"]
        },
        "services": {
            "auth": "active",
            "audit": "active",
            "api_keys": "active",
            "alerts": "active"
        }
    }
