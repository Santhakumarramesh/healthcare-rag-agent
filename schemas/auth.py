"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """User registration request — accepts both 'name' and 'full_name' from frontend."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    # Accept 'full_name' (frontend field) with 'name' as fallback alias
    full_name: Optional[str] = None
    name: Optional[str] = None
    role: str = Field(default="patient")
    phone: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Return the user's name regardless of which field was sent."""
        return self.full_name or self.name or "User"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    """OTP verification request"""
    user_id: str
    token: str
    purpose: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset request"""
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User profile response — matches frontend UserResponse interface."""
    id: str
    full_name: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response — matches frontend AuthResponse interface."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        from_attributes = True
