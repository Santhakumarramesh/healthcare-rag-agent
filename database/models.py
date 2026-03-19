"""
Database Models - SQLAlchemy ORM models for persistent storage.

Tables:
- users: User accounts
- sessions: User sessions and conversation history
- interactions: Individual query/response pairs
- reports: Uploaded medical reports
- api_keys: API keys for external access
- audit_logs: Audit trail for compliance
- alerts: Clinical alerts triggered
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User accounts"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # patient, clinician, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """User sessions and conversation history"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    interactions = relationship("Interaction", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="session", cascade="all, delete-orphan")


class Interaction(Base):
    """Individual query/response pairs"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    latency_ms = Column(Float, nullable=False)
    sources_count = Column(Integer, default=0)
    has_alerts = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Store sources and reasoning as JSON
    sources = Column(JSON, nullable=True)
    reasoning_steps = Column(JSON, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="interactions")


class Report(Base):
    """Uploaded medical reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, image, text
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Extracted data as JSON
    extracted_data = Column(JSON, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="reports")


class APIKey(Base):
    """API keys for external access"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=1000)
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(String(50), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(String(500), nullable=False)
    resource = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Additional details as JSON
    details = Column(JSON, nullable=True)


class Alert(Base):
    """Clinical alerts triggered"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(50), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    message = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged = Column(Boolean, default=False)

    # Alert details as JSON
    details = Column(JSON, nullable=True)
