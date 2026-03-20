"""
Pydantic schemas for patient endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PatientProfileCreate(BaseModel):
    """Create patient profile request"""
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    address: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    preferred_lang: Optional[str] = None


class PatientProfileUpdate(BaseModel):
    """Update patient profile request"""
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    address: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    preferred_lang: Optional[str] = None


class PatientProfileResponse(BaseModel):
    """Patient profile response"""
    user_id: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    address: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    preferred_lang: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthProfileUpdate(BaseModel):
    """Quick health profile update"""
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    chronic_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class PatientDashboardResponse(BaseModel):
    """Patient dashboard summary"""
    recent_reports_count: int
    pending_refills_count: int
    upcoming_consultations_count: int
    active_alerts_count: int
    care_score: Optional[int] = None
    last_vital_check: Optional[datetime] = None

    class Config:
        from_attributes = True
