"""
Pydantic schemas for prescription endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PrescriptionResponse(BaseModel):
    """Prescription response"""
    prescription_id: str
    patient_user_id: str
    doctor_user_id: str
    medication_name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: str
    duration_days: Optional[int] = None
    instructions: Optional[str] = None
    quantity: int
    refills_allowed: int
    refills_used: int
    status: str
    prescribed_date: datetime
    expiry_date: Optional[datetime] = None
    is_controlled: bool
    auto_renew: bool
    safety_flags_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class RefillRequestCreate(BaseModel):
    """Create refill request"""
    prescription_id: str
    quantity: int
    delivery_address: Optional[dict] = None
    notes: Optional[str] = None


class RefillRequestResponse(BaseModel):
    """Refill request response"""
    refill_id: str
    prescription_id: str
    patient_user_id: str
    status: str
    quantity: int
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    denial_reason: Optional[str] = None
    medication_name: str
    dosage: str

    class Config:
        from_attributes = True


class RefillApprovalRequest(BaseModel):
    """Refill approval request"""
    approved: bool
    denial_reason: Optional[str] = None


class MedicationOrderResponse(BaseModel):
    """Medication order response"""
    order_id: str
    status: str
    pharmacy: Optional[str] = None
    tracking_num: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeliveryTrackingResponse(BaseModel):
    """Delivery tracking response"""
    status: str
    location: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class SafetyFlagResponse(BaseModel):
    """Safety flag response"""
    flag_type: str
    severity: str
    description: str
    requires_review: bool
    reviewed: bool

    class Config:
        from_attributes = True
