"""
Pydantic schemas for insurance endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InsuranceCreate(BaseModel):
    """Create insurance profile request"""
    provider_name: str
    plan_name: str
    member_id: str
    group_number: Optional[str] = None
    insurance_type: str  # primary, secondary
    deductible: Optional[float] = None
    copay: Optional[float] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class InsuranceUpdate(BaseModel):
    """Update insurance profile request"""
    provider_name: Optional[str] = None
    plan_name: Optional[str] = None
    member_id: Optional[str] = None
    group_number: Optional[str] = None
    insurance_type: Optional[str] = None
    deductible: Optional[float] = None
    copay: Optional[float] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class InsuranceResponse(BaseModel):
    """Insurance profile response"""
    insurance_id: str
    user_id: str
    provider_name: str
    plan_name: str
    member_id: str
    group_number: Optional[str] = None
    insurance_type: str
    deductible: Optional[float] = None
    deductible_met: Optional[float] = None
    copay: Optional[float] = None
    out_of_pocket_max: Optional[float] = None
    status: str
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    card_front_url: Optional[str] = None
    card_back_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InsuranceSnapshotResponse(BaseModel):
    """Insurance snapshot for consultation booking"""
    insurance_id: str
    provider_name: str
    plan_name: str
    copay: Optional[float] = None
    status: str

    class Config:
        from_attributes = True


class InsuranceVerificationResponse(BaseModel):
    """Insurance verification response"""
    insurance_id: str
    verification_type: str
    status: str
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True
