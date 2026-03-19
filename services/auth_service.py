"""
Authentication Service - User authentication and session management.

Features:
- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Session management
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum

import jwt
import bcrypt
from loguru import logger


class UserRole(str, Enum):
    """User roles for RBAC"""
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"


class AuthService:
    """
    Authentication service for user management.
    
    Handles:
    - User authentication
    - JWT token generation/validation
    - Password hashing
    - Role-based permissions
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize auth service.
        
        Args:
            secret_key: JWT secret key (defaults to env var or random)
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
        
        # In-memory user store (would be database in production)
        self.users: Dict[str, Dict] = {
            # Demo users
            "admin@healthcare.ai": {
                "user_id": "admin-001",
                "email": "admin@healthcare.ai",
                "password_hash": self._hash_password("admin123"),
                "role": UserRole.ADMIN,
                "name": "System Admin",
                "created_at": datetime.now().isoformat()
            },
            "doctor@healthcare.ai": {
                "user_id": "doc-001",
                "email": "doctor@healthcare.ai",
                "password_hash": self._hash_password("doctor123"),
                "role": UserRole.CLINICIAN,
                "name": "Dr. Smith",
                "created_at": datetime.now().isoformat()
            },
            "patient@healthcare.ai": {
                "user_id": "patient-001",
                "email": "patient@healthcare.ai",
                "password_hash": self._hash_password("patient123"),
                "role": UserRole.PATIENT,
                "name": "John Doe",
                "created_at": datetime.now().isoformat()
            }
        }
        
        logger.info(f"[AuthService] Initialized with {len(self.users)} demo users")
    
    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            User data with token if successful, None otherwise
        """
        user = self.users.get(email)
        
        if not user:
            logger.warning(f"[AuthService] Login failed: User not found - {email}")
            return None
        
        if not self._verify_password(password, user["password_hash"]):
            logger.warning(f"[AuthService] Login failed: Invalid password - {email}")
            return None
        
        # Generate JWT token
        token = self.generate_token(user["user_id"], user["email"], user["role"])
        
        logger.success(f"[AuthService] Login successful - {email} ({user['role']})")
        
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "token": token,
            "expires_at": (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat()
        }
    
    def generate_token(self, user_id: str, email: str, role: UserRole) -> str:
        """
        Generate JWT token.
        
        Args:
            user_id: User ID
            email: User email
            role: User role
        
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("[AuthService] Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"[AuthService] Invalid token: {e}")
            return None
    
    def check_permission(self, token: str, required_role: UserRole) -> bool:
        """
        Check if user has required role.
        
        Args:
            token: JWT token
            required_role: Required role
        
        Returns:
            True if user has permission, False otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return False
        
        user_role = payload.get("role")
        
        # Admin has all permissions
        if user_role == UserRole.ADMIN:
            return True
        
        # Clinician has patient permissions
        if user_role == UserRole.CLINICIAN and required_role == UserRole.PATIENT:
            return True
        
        # Exact role match
        return user_role == required_role
    
    def register_user(
        self,
        email: str,
        password: str,
        name: str,
        role: UserRole = UserRole.PATIENT
    ) -> Optional[Dict]:
        """
        Register new user.
        
        Args:
            email: User email
            password: User password
            name: User name
            role: User role (default: patient)
        
        Returns:
            User data if successful, None if email exists
        """
        if email in self.users:
            logger.warning(f"[AuthService] Registration failed: Email exists - {email}")
            return None
        
        user_id = f"{role}-{secrets.token_hex(4)}"
        
        self.users[email] = {
            "user_id": user_id,
            "email": email,
            "password_hash": self._hash_password(password),
            "role": role,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        logger.success(f"[AuthService] User registered - {email} ({role})")
        
        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "role": role
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        for user in self.users.values():
            if user["user_id"] == user_id:
                return {
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "created_at": user["created_at"]
                }
        return None
    
    def list_users(self) -> list:
        """List all users (admin only)"""
        return [
            {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "created_at": user["created_at"]
            }
            for user in self.users.values()
        ]


# Singleton instance
auth_service = AuthService()
