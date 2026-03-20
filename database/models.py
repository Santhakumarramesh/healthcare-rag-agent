"""
Database Models - SQLAlchemy ORM models for HealthCopilot persistent storage.

Complete schema with 42 tables covering:
- Authentication & Sessions
- User Profiles (Patient, Doctor, Caregiver)
- Consultations & Prescriptions
- Medical Records & Analysis
- Insurance & Billing
- Health Tracking & Wellness
- Marketplace & Orders
- Support & Admin
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON,
    UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Enums
class UserRole(str, Enum):
    """User role enumeration"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    CAREGIVER = "caregiver"
    SUPPORT = "support"
    PHARMACIST = "pharmacist"
    SUPERADMIN = "superadmin"


class VerificationStatus(str, Enum):
    """Verification status for documents"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ConsultationStatus(str, Enum):
    """Consultation status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PrescriptionStatus(str, Enum):
    """Prescription status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    FILLED = "filled"
    PENDING = "pending"


class RefillStatus(str, Enum):
    """Refill request status"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    FILLED = "filled"
    CANCELLED = "cancelled"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class InsuranceStatus(str, Enum):
    """Insurance status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class SeverityLevel(str, Enum):
    """Alert severity level"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class JobStatus(str, Enum):
    """Processing job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


# ============================================================================
# AUTHENTICATION & SESSION TABLES
# ============================================================================

class User(Base):
    """User accounts with authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    otp_tokens = relationship("OTPToken", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    caregiver_links = relationship("CaregiverLink", back_populates="caregiver", foreign_keys="CaregiverLink.caregiver_user_id")
    patient_links = relationship("CaregiverLink", back_populates="patient", foreign_keys="CaregiverLink.patient_user_id")
    reports = relationship("Report", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")
    insights = relationship("AIInsight", back_populates="user")
    consultations_patient = relationship("Consultation", back_populates="patient", foreign_keys="Consultation.patient_user_id")
    consultations_doctor = relationship("Consultation", back_populates="doctor", foreign_keys="Consultation.doctor_user_id")
    prescriptions_patient = relationship("Prescription", back_populates="patient", foreign_keys="Prescription.patient_user_id")
    prescriptions_doctor = relationship("Prescription", back_populates="doctor", foreign_keys="Prescription.doctor_user_id")
    refill_requests = relationship("RefillRequest", back_populates="patient")
    insurance_profiles = relationship("InsuranceProfile", back_populates="user")
    symptom_logs = relationship("SymptomLog", back_populates="user")
    medication_logs = relationship("MedicationLog", back_populates="user")
    hydration_logs = relationship("HydrationLog", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    vitals_logs = relationship("VitalsLog", back_populates="user")
    sleep_logs = relationship("SleepLog", back_populates="user")
    nutrition_logs = relationship("NutritionLog", back_populates="user")
    care_scores = relationship("CareScore", back_populates="user")
    care_plans_patient = relationship("CarePlan", back_populates="patient", foreign_keys="CarePlan.patient_id")
    care_plans_doctor = relationship("CarePlan", back_populates="doctor", foreign_keys="CarePlan.doctor_id")
    visit_preparations = relationship("VisitPreparation", back_populates="patient")
    orders = relationship("Order", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    doctor_approvals = relationship("DoctorApproval", back_populates="doctor", foreign_keys="DoctorApproval.doctor_id")
    doctor_approvals_admin = relationship("DoctorApproval", back_populates="admin", foreign_keys="DoctorApproval.admin_id")


class UserSession(Base):
    """User sessions and device tracking"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class OTPToken(Base):
    """One-time password tokens"""
    __tablename__ = "otp_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    token = Column(String(100), unique=True, index=True, nullable=False)
    purpose = Column(String(50), nullable=False)  # verify_email, verify_phone, password_reset, login
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="otp_tokens")


class APIKey(Base):
    """API keys for external access"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=1000)
    total_requests = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


# ============================================================================
# USER PROFILE TABLES
# ============================================================================

class PatientProfile(Base):
    """Patient health profile"""
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(50), nullable=True)
    blood_type = Column(String(10), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    allergies = Column(JSON, nullable=True)
    chronic_conditions = Column(JSON, nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    address = Column(JSON, nullable=True)
    timezone = Column(String(50), nullable=True)
    preferred_lang = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient_profile")


class DoctorProfile(Base):
    """Doctor professional profile"""
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    license_number = Column(String(100), nullable=True)
    npi_number = Column(String(100), nullable=True)
    specialties = Column(JSON, nullable=True)
    languages_spoken = Column(JSON, nullable=True)
    jurisdictions = Column(JSON, nullable=True)
    years_experience = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Float, nullable=True)
    consultation_duration_min = Column(Integer, nullable=True)
    accepts_insurance = Column(Boolean, default=False)
    accepted_insurances = Column(JSON, nullable=True)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    verification_status = Column(String(50), default=VerificationStatus.PENDING)
    is_available_online = Column(Boolean, default=False)
    profile_photo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    availabilities = relationship("DoctorAvailability", back_populates="doctor")
    care_plans = relationship("CarePlan", back_populates="doctor", foreign_keys="CarePlan.doctor_id")


class CaregiverLink(Base):
    """Caregiver-Patient relationship"""
    __tablename__ = "caregiver_links"

    id = Column(Integer, primary_key=True, index=True)
    caregiver_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    patient_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)
    permissions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    caregiver = relationship("User", back_populates="caregiver_links", foreign_keys=[caregiver_user_id])
    patient = relationship("User", back_populates="patient_links", foreign_keys=[patient_user_id])


# ============================================================================
# MEDICAL RECORDS & ANALYSIS TABLES
# ============================================================================

class Report(Base):
    """Uploaded medical reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    session_id = Column(String(100), ForeignKey("user_sessions.session_id"), nullable=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    report_type = Column(String(100), nullable=True)
    report_date = Column(DateTime, nullable=True)
    lab_name = Column(String(255), nullable=True)
    doctor_name = Column(String(255), nullable=True)
    extracted_data = Column(JSON, nullable=True)
    has_flags = Column(Boolean, default=False)
    flag_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    session = relationship("UserSession")
    analyses = relationship("ReportAnalysis", back_populates="report", cascade="all, delete-orphan")
    comparisons_new = relationship("ReportComparison", back_populates="report_new", foreign_keys="ReportComparison.report_id_new")
    comparisons_old = relationship("ReportComparison", back_populates="report_old", foreign_keys="ReportComparison.report_id_old")


class ReportAnalysis(Base):
    """AI analysis of medical reports"""
    __tablename__ = "report_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(100), unique=True, index=True, nullable=False)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    findings = Column(JSON, nullable=True)
    risk_level = Column(String(20), nullable=True)
    recommendations = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    report = relationship("Report", back_populates="analyses")


class ReportComparison(Base):
    """Comparison between reports"""
    __tablename__ = "report_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    report_id_new = Column(Integer, ForeignKey("reports.id"), nullable=False)
    report_id_old = Column(Integer, ForeignKey("reports.id"), nullable=False)
    delta = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report_new = relationship("Report", back_populates="comparisons_new", foreign_keys=[report_id_new])
    report_old = relationship("Report", back_populates="comparisons_old", foreign_keys=[report_id_old])


class AIConversation(Base):
    """AI conversation sessions"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), nullable=False, index=True)
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)


class Interaction(Base):
    """Query-response interactions"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("user_sessions.session_id"), nullable=True)
    conversation_id = Column(String(100), ForeignKey("ai_conversations.conversation_id"), nullable=True)
    user_id = Column(String(50), nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    query_type = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    sources_count = Column(Integer, default=0)
    has_alerts = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    sources = Column(JSON, nullable=True)
    reasoning_steps = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="interactions")


class AIInsight(Base):
    """AI-generated health insights"""
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    what_changed = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=False)
    what_to_do = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True)
    is_read = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="insights")


# ============================================================================
# CONSULTATION TABLES
# ============================================================================

class DoctorAvailability(Base):
    """Doctor availability slots"""
    __tablename__ = "doctor_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    slot_minutes = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    timezone = Column(String(50), nullable=True)

    # Relationships
    doctor = relationship("DoctorProfile", back_populates="availabilities")


class Consultation(Base):
    """Doctor-patient consultations"""
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(String(100), unique=True, index=True, nullable=False)
    patient_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    doctor_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    status = Column(String(50), default=ConsultationStatus.SCHEDULED)
    scheduled_at = Column(DateTime, nullable=False)
    duration_min = Column(Integer, nullable=True)
    type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    report_ids = Column(JSON, nullable=True)
    fee = Column(Float, nullable=True)
    insurance_used = Column(String(100), nullable=True)
    payment_status = Column(String(50), nullable=True)
    payment_intent = Column(String(100), nullable=True)
    meeting_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="consultations_patient", foreign_keys=[patient_user_id])
    doctor = relationship("User", back_populates="consultations_doctor", foreign_keys=[doctor_user_id])
    messages = relationship("ConsultationMessage", back_populates="consultation", cascade="all, delete-orphan")
    summary = relationship("ConsultationSummary", back_populates="consultation", uselist=False)


class ConsultationMessage(Base):
    """Messages during consultation"""
    __tablename__ = "consultation_messages"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False, index=True)
    sender_user_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)
    attachment_url = Column(String(500), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    consultation = relationship("Consultation", back_populates="messages")


class ConsultationSummary(Base):
    """Consultation summary/notes"""
    __tablename__ = "consultation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), unique=True, nullable=False)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    prescription_ids = Column(JSON, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    consultation = relationship("Consultation", back_populates="summary")


# ============================================================================
# PRESCRIPTION & MEDICATION TABLES
# ============================================================================

class Prescription(Base):
    """Medication prescriptions"""
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(String(100), unique=True, index=True, nullable=False)
    patient_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    doctor_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=True)
    medication_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    refills_allowed = Column(Integer, default=0)
    refills_used = Column(Integer, default=0)
    status = Column(String(50), default=PrescriptionStatus.ACTIVE)
    prescribed_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    is_controlled = Column(Boolean, default=False)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="prescriptions_patient", foreign_keys=[patient_user_id])
    doctor = relationship("User", back_populates="prescriptions_doctor", foreign_keys=[doctor_user_id])
    refill_requests = relationship("RefillRequest", back_populates="prescription")
    safety_flags = relationship("MedicationSafetyFlag", back_populates="prescription", cascade="all, delete-orphan")
    medication_logs = relationship("MedicationLog", back_populates="prescription")


class RefillRequest(Base):
    """Medication refill requests"""
    __tablename__ = "refill_requests"

    id = Column(Integer, primary_key=True, index=True)
    refill_id = Column(String(100), unique=True, index=True, nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    patient_user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    status = Column(String(50), default=RefillStatus.PENDING)
    quantity = Column(Integer, nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(String(50), nullable=True)
    denial_reason = Column(Text, nullable=True)
    delivery_address = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    prescription = relationship("Prescription", back_populates="refill_requests")
    patient = relationship("User", back_populates="refill_requests")
    medication_orders = relationship("MedicationOrder", back_populates="refill_request")


class MedicationSafetyFlag(Base):
    """Safety flags for medications"""
    __tablename__ = "medication_safety_flags"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    flag_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    requires_review = Column(Boolean, default=True)
    reviewed = Column(Boolean, default=False)
    reviewer_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prescription = relationship("Prescription", back_populates="safety_flags")


class MedicationOrder(Base):
    """Medication fulfillment orders"""
    __tablename__ = "medication_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True, nullable=False)
    refill_id = Column(Integer, ForeignKey("refill_requests.id"), nullable=True)
    patient_id = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default=OrderStatus.PENDING)
    pharmacy = Column(String(255), nullable=True)
    tracking_num = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    refill_request = relationship("RefillRequest", back_populates="medication_orders")
    tracking_updates = relationship("DeliveryTracking", back_populates="order", cascade="all, delete-orphan")


class DeliveryTracking(Base):
    """Delivery tracking updates"""
    __tablename__ = "delivery_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("medication_orders.id"), nullable=False, index=True)
    status = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("MedicationOrder", back_populates="tracking_updates")


# ============================================================================
# INSURANCE TABLES
# ============================================================================

class InsuranceProfile(Base):
    """Insurance profiles"""
    __tablename__ = "insurance_profiles"

    id = Column(Integer, primary_key=True, index=True)
    insurance_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    provider_name = Column(String(255), nullable=False)
    plan_name = Column(String(255), nullable=False)
    member_id = Column(String(100), nullable=False)
    group_number = Column(String(100), nullable=True)
    insurance_type = Column(String(50), nullable=False)
    deductible = Column(Float, nullable=True)
    deductible_met = Column(Float, nullable=True)
    copay = Column(Float, nullable=True)
    out_of_pocket_max = Column(Float, nullable=True)
    status = Column(String(50), default=InsuranceStatus.ACTIVE)
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    card_front_url = Column(String(500), nullable=True)
    card_back_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="insurance_profiles")
    verifications = relationship("InsuranceVerification", back_populates="insurance", cascade="all, delete-orphan")


class InsuranceVerification(Base):
    """Insurance verification records"""
    __tablename__ = "insurance_verifications"

    id = Column(Integer, primary_key=True, index=True)
    insurance_id = Column(Integer, ForeignKey("insurance_profiles.id"), nullable=False, index=True)
    verification_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    result = Column(JSON, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    insurance = relationship("InsuranceProfile", back_populates="verifications")


# ============================================================================
# HEALTH TRACKING TABLES
# ============================================================================

class SymptomLog(Base):
    """Symptom tracking logs"""
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    symptoms = Column(JSON, nullable=False)
    overall = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="symptom_logs")


class MedicationLog(Base):
    """Medication adherence tracking"""
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    taken = Column(Boolean, default=False)
    taken_at = Column(DateTime, nullable=True)
    skipped_reason = Column(String(255), nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="medication_logs")
    prescription = relationship("Prescription", back_populates="medication_logs")


class HydrationLog(Base):
    """Hydration tracking"""
    __tablename__ = "hydration_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="hydration_logs")


class ActivityLog(Base):
    """Physical activity tracking"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    steps = Column(Integer, nullable=True)
    calories = Column(Float, nullable=True)
    active_min = Column(Integer, nullable=True)
    activity_type = Column(String(100), nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="activity_logs")


class VitalsLog(Base):
    """Vital signs tracking"""
    __tablename__ = "vitals_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    heart_rate = Column(Integer, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    temperature_c = Column(Float, nullable=True)
    blood_glucose = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="vitals_logs")


class SleepLog(Base):
    """Sleep tracking"""
    __tablename__ = "sleep_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    duration_min = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=True)
    sleep_time = Column(DateTime, nullable=True)
    wake_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="sleep_logs")


class NutritionLog(Base):
    """Nutrition tracking"""
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    meal_type = Column(String(100), nullable=False)
    items = Column(JSON, nullable=False)
    total_cal = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="nutrition_logs")


class CareScore(Base):
    """Weekly care quality score"""
    __tablename__ = "care_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    week_start = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False)
    breakdown = Column(JSON, nullable=True)
    trend = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="care_scores")


# ============================================================================
# CARE PLANNING TABLES
# ============================================================================

class CarePlan(Base):
    """Patient care plans"""
    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(100), unique=True, index=True, nullable=False)
    patient_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    doctor_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    goals = Column(JSON, nullable=True)
    medications = Column(JSON, nullable=True)
    lifestyle = Column(JSON, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="care_plans_patient", foreign_keys=[patient_id])
    doctor = relationship("User", back_populates="care_plans_doctor", foreign_keys=[doctor_id])


class VisitPreparation(Base):
    """Pre-consultation preparation"""
    __tablename__ = "visit_preparations"

    id = Column(Integer, primary_key=True, index=True)
    prep_id = Column(String(100), unique=True, index=True, nullable=False)
    patient_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=True)
    questions = Column(JSON, nullable=True)
    symptoms_summary = Column(Text, nullable=True)
    medications_list = Column(JSON, nullable=True)
    concerns = Column(Text, nullable=True)
    shared_with_doctor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="visit_preparations")


# ============================================================================
# MARKETPLACE TABLES
# ============================================================================

class Product(Base):
    """Marketplace products"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True)
    conditions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    """Marketplace orders"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    status = Column(String(50), default=OrderStatus.PENDING)
    total = Column(Float, nullable=False)
    shipping_address = Column(JSON, nullable=True)
    payment_status = Column(String(50), nullable=True)
    payment_intent = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Order line items"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ============================================================================
# AUDIT & ALERT TABLES
# ============================================================================

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
    details = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Alert(Base):
    """Clinical alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(100), nullable=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    action = Column(Text, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(50), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")


class ProcessingJob(Base):
    """Background processing jobs"""
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    job_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(String(50), default=JobStatus.PENDING)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# DOCTOR APPROVAL & SUPPORT TABLES
# ============================================================================

class DoctorApproval(Base):
    """Doctor account approval workflow"""
    __tablename__ = "doctor_approvals"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    admin_id = Column(String(50), ForeignKey("users.user_id"), nullable=True)
    status = Column(String(50), default=VerificationStatus.PENDING)
    submitted_docs = Column(JSON, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    doctor = relationship("User", back_populates="doctor_approvals", foreign_keys=[doctor_id])
    admin = relationship("User", back_populates="doctor_approvals_admin", foreign_keys=[admin_id])


class SupportTicket(Base):
    """Support tickets"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), default="open")
    assigned_to = Column(String(50), nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="support_tickets")
