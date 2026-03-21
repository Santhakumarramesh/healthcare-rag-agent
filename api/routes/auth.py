"""
Authentication endpoints for user registration, login, and token management.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, generate_otp
)
from database.models import User, OTPToken, UserSession
from schemas.auth import (
    RegisterRequest, LoginRequest, OTPRequest, ForgotPasswordRequest,
    ResetPasswordRequest, RefreshTokenRequest, AuthResponse, UserResponse
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - Hash password
    - Create user
    - Generate OTP for email verification
    - Return auth tokens
    """
    # Check if user exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        user_id=request.email.split("@")[0],
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        name=request.display_name,
        role=request.role,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate OTP for email verification
    otp_token = generate_otp()
    otp = OTPToken(
        user_id=user.user_id,
        token=otp_token,
        purpose="verify_email",
        expires_at=datetime.utcnow() + timedelta(hours=24),
        used=False
    )
    db.add(otp)
    db.commit()

    # Generate tokens
    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.user_id,
            "full_name": user.name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "created_at": user.created_at or datetime.utcnow(),
        }
    }


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.

    - Verify email and password
    - Create user session
    - Return access and refresh tokens
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate tokens
    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.user_id,
            "full_name": user.name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "created_at": user.created_at or datetime.utcnow(),
        }
    }


@router.post("/send-otp")
def send_otp(user_id: str, purpose: str, db: Session = Depends(get_db)):
    """
    Send OTP to user via email or SMS.

    Purposes: verify_email, verify_phone, password_reset, login
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate OTP
    otp_token = generate_otp()
    otp = OTPToken(
        user_id=user_id,
        token=otp_token,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        used=False
    )
    db.add(otp)
    db.commit()

    # TODO: Send OTP via email/SMS

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
def verify_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """
    Verify OTP token and mark user as verified.
    """
    otp = db.query(OTPToken).filter(
        OTPToken.user_id == request.user_id,
        OTPToken.token == request.token,
        OTPToken.purpose == request.purpose,
        OTPToken.used == False
    ).first()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired"
        )

    # Mark OTP as used
    otp.used = True

    # Update user verification
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if request.purpose == "verify_email":
        user.is_verified = True

    db.commit()

    return {"message": f"{request.purpose} verified successfully"}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send password reset OTP to user email.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate reset OTP
    otp_token = generate_otp()
    otp = OTPToken(
        user_id=user.user_id,
        token=otp_token,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False
    )
    db.add(otp)
    db.commit()

    # TODO: Send reset link via email

    return {"message": "Password reset link sent to email"}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset user password using reset token.
    """
    otp = db.query(OTPToken).filter(
        OTPToken.token == request.token,
        OTPToken.purpose == "password_reset",
        OTPToken.used == False
    ).first()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Update password
    user = db.query(User).filter(User.user_id == otp.user_id).first()
    user.password_hash = hash_password(request.new_password)
    otp.used = True

    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    try:
        payload = decode_token(request.refresh_token)
        user_id = payload.get("user_id")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = create_access_token(user.user_id)
    new_refresh_token = create_refresh_token(user.user_id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.user_id,
            "full_name": user.name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "created_at": user.created_at or datetime.utcnow(),
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return {
        "id": user["user_id"],
        "full_name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "is_verified": user.get("is_verified", False),
        "created_at": user.get("created_at", datetime.utcnow())
    }


@router.post("/logout")
def logout(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating session.
    """
    # TODO: Invalidate session token

    return {"message": "Logged out successfully"}
