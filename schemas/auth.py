"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    role: str = Field(default="patient")
    phone: Optional[str] = None

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


class AuthResponse(BaseModel):
    """Authentication response"""
    user_id: str
    email: str
    name: str
    role: str
    access_token: str
    refresh_token: str
    expires_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User profile response"""
    user_id: str
    email: str
    name: str
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
