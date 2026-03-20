"""
Pydantic schemas for doctor endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DoctorProfileCreate(BaseModel):
    """Create doctor profile request"""
    license_number: str
    npi_number: Optional[str] = None
    specialties: List[str]
    languages_spoken: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    years_experience: int
    bio: Optional[str] = None
    consultation_fee: float
    consultation_duration_min: int = 30
    accepts_insurance: bool = False
    accepted_insurances: Optional[List[str]] = None


class DoctorProfileUpdate(BaseModel):
    """Update doctor profile request"""
    specialties: Optional[List[str]] = None
    languages_spoken: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    years_experience: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    consultation_duration_min: Optional[int] = None
    accepts_insurance: Optional[bool] = None
    accepted_insurances: Optional[List[str]] = None
    is_available_online: Optional[bool] = None
    profile_photo_url: Optional[str] = None


class DoctorProfileResponse(BaseModel):
    """Doctor profile response"""
    user_id: str
    license_number: str
    npi_number: Optional[str] = None
    specialties: List[str]
    languages_spoken: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    years_experience: int
    bio: Optional[str] = None
    consultation_fee: float
    consultation_duration_min: int
    accepts_insurance: bool
    accepted_insurances: Optional[List[str]] = None
    rating: float
    total_reviews: int
    verification_status: str
    is_available_online: bool
    profile_photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoctorSearchQuery(BaseModel):
    """Doctor search query"""
    specialty: Optional[str] = None
    language: Optional[str] = None
    insurance: Optional[str] = None
    availability_date: Optional[datetime] = None
    min_rating: Optional[float] = None
    page: int = 1
    per_page: int = 10


class DoctorListResponse(BaseModel):
    """Doctor list response"""
    user_id: str
    name: str
    specialties: List[str]
    rating: float
    total_reviews: int
    consultation_fee: float
    is_available_online: bool
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True
