"""
FastAPI dependency injectors — auth, RBAC, DB session.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from core.security import decode_token
from database.database import get_db_session


# ── DB ────────────────────────────────────────────────────────────────────────

def get_db() -> Session:
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


# ── Auth ──────────────────────────────────────────────────────────────────────

async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


# ── RBAC ──────────────────────────────────────────────────────────────────────

ROLE_HIERARCHY = {
    "superadmin": 100,
    "admin": 80,
    "doctor": 60,
    "pharmacist": 50,
    "support": 40,
    "caregiver": 30,
    "patient": 20,
}


def require_roles(*roles: str):
    """
    Usage:
        @router.get("/admin")
        async def admin_route(user = Depends(require_roles("admin", "superadmin"))):
    """
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}"
            )
        return user
    return _check


def require_patient():
    return require_roles("patient", "admin", "superadmin")


def require_doctor():
    return require_roles("doctor", "admin", "superadmin")


def require_admin():
    return require_roles("admin", "superadmin")
