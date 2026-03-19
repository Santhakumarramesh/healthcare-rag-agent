"""
Authentication API Router - User authentication endpoints.
"""
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from services.auth_service import auth_service, UserRole
from services.audit_service import audit_service, AuditEventType

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.PATIENT


class AuthResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    token: str
    expires_at: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    created_at: str


# Dependency for authentication
async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to get current authenticated user from token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


# Dependency for role checking
def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: dict = Depends(require_role(UserRole.ADMIN))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role")
        
        # Admin has all permissions
        if user_role == UserRole.ADMIN:
            return user
        
        # Clinician has patient permissions
        if user_role == UserRole.CLINICIAN and required_role == UserRole.PATIENT:
            return user
        
        # Exact role match
        if user_role == required_role:
            return user
        
        # Permission denied
        audit_service.log_permission_denied(
            user_id=user.get("user_id"),
            user_email=user.get("email"),
            user_role=user_role,
            attempted_action=f"Access {required_role} endpoint",
            required_role=required_role
        )
        
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required role: {required_role}"
        )
    
    return role_checker


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Demo credentials:
    - admin@healthcare.ai / admin123 (Admin)
    - doctor@healthcare.ai / doctor123 (Clinician)
    - patient@healthcare.ai / patient123 (Patient)
    """
    result = auth_service.authenticate(request.email, request.password)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Log successful login
    audit_service.log_login(
        user_id=result["user_id"],
        user_email=result["email"],
        user_role=result["role"]
    )
    
    return AuthResponse(**result)


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    result = auth_service.register_user(
        email=request.email,
        password=request.password,
        name=request.name,
        role=request.role
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Log registration
    audit_service.log_event(
        event_type=AuditEventType.USER_REGISTER,
        user_id=result["user_id"],
        user_email=result["email"],
        user_role=result["role"],
        action=f"User registered: {result['name']}",
        success=True
    )
    
    return UserResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user information"""
    user_data = auth_service.get_user_by_id(user["user_id"])
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user_data)


@router.get("/users", response_model=list[UserResponse])
async def list_users(user: dict = Depends(require_role(UserRole.ADMIN))):
    """List all users (admin only)"""
    users = auth_service.list_users()
    return [UserResponse(**u) for u in users]


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """Logout user (invalidate token on client side)"""
    audit_service.log_event(
        event_type=AuditEventType.USER_LOGOUT,
        user_id=user["user_id"],
        user_email=user["email"],
        user_role=user["role"],
        action="User logged out",
        success=True
    )
    
    return {"message": "Logged out successfully"}
