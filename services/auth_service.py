"""
Authentication Service - User authentication and session management.

Features:
- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Session management
- Database-backed user storage
"""
import os
import sys
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum

import jwt
import bcrypt
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from database.database import get_db_session
from database.models import User as UserModel


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

        # Create demo users if they don't exist
        self._create_demo_users()

        logger.info("[AuthService] Initialized with database storage")

    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def _create_demo_users(self):
        """Create demo users if they don't exist"""
        try:
            db = get_db_session()

            demo_users = [
                {
                    "user_id": "admin-001",
                    "email": "admin@healthcare.ai",
                    "password": "admin123",
                    "name": "System Admin",
                    "role": UserRole.ADMIN
                },
                {
                    "user_id": "doc-001",
                    "email": "doctor@healthcare.ai",
                    "password": "doctor123",
                    "name": "Dr. Smith",
                    "role": UserRole.CLINICIAN
                },
                {
                    "user_id": "patient-001",
                    "email": "patient@healthcare.ai",
                    "password": "patient123",
                    "name": "John Doe",
                    "role": UserRole.PATIENT
                }
            ]

            for user_data in demo_users:
                try:
                    # Check if user exists
                    existing = db.query(UserModel).filter(UserModel.email == user_data["email"]).first()
                    if not existing:
                        user = UserModel(
                            user_id=user_data["user_id"],
                            email=user_data["email"],
                            password_hash=self._hash_password(user_data["password"]),
                            name=user_data["name"],
                            role=user_data["role"],
                            active=True
                        )
                        db.add(user)
                        logger.info(f"[AuthService] Created demo user: {user_data['email']}")
                except Exception as e:
                    logger.warning(f"[AuthService] Could not create user {user_data['email']}: {e}")
                    continue

            db.commit()
            logger.success("[AuthService] Demo users initialized")

        except Exception as e:
            logger.error(f"[AuthService] Error creating demo users: {e}")
            logger.warning("[AuthService] Continuing without demo users")
            try:
                db.rollback()
            except:
                pass
        finally:
            try:
                db.close()
            except:
                pass

    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            User data with token if successful, None otherwise
        """
        db = get_db_session()
        try:
            user = db.query(UserModel).filter(UserModel.email == email, UserModel.active == True).first()

            if not user:
                logger.warning(f"[AuthService] Login failed: User not found - {email}")
                return None

            if not self._verify_password(password, user.password_hash):
                logger.warning(f"[AuthService] Login failed: Invalid password - {email}")
                return None

            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()

            # Generate JWT token
            token = self.generate_token(user.user_id, user.email, user.role)

            logger.success(f"[AuthService] Login successful - {email} ({user.role})")

            return {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "token": token,
                "expires_at": (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat()
            }
        finally:
            db.close()

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
        db = get_db_session()
        try:
            # Check if user exists
            existing = db.query(UserModel).filter(UserModel.email == email).first()
            if existing:
                logger.warning(f"[AuthService] Registration failed: Email exists - {email}")
                return None

            user_id = f"{role}-{secrets.token_hex(4)}"

            user = UserModel(
                user_id=user_id,
                email=email,
                password_hash=self._hash_password(password),
                name=name,
                role=role,
                active=True
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.success(f"[AuthService] User registered - {email} ({role})")

            return {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"[AuthService] Registration error: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        db = get_db_session()
        try:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return None

            return {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            }
        finally:
            db.close()

    def list_users(self) -> list:
        """List all users (admin only)"""
        db = get_db_session()
        try:
            users = db.query(UserModel).filter(UserModel.active == True).all()
            return [
                {
                    "user_id": user.user_id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ]
        finally:
            db.close()


# Singleton instance
auth_service = AuthService()
