"""
Pydantic schemas for consultation endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BookConsultationRequest(BaseModel):
    """Book consultation request"""
    doctor_user_id: str
    scheduled_at: datetime
    type: str  # video, phone, in_person
    reason: str
    report_ids: Optional[List[str]] = None
    insurance_id: Optional[str] = None


class ConsultationResponse(BaseModel):
    """Consultation response"""
    consultation_id: str
    patient_user_id: str
    doctor_user_id: str
    status: str
    scheduled_at: datetime
    duration_min: Optional[int] = None
    type: str
    reason: Optional[str] = None
    report_ids: Optional[List[str]] = None
    fee: Optional[float] = None
    insurance_used: Optional[str] = None
    payment_status: Optional[str] = None
    meeting_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsultationSummaryCreate(BaseModel):
    """Create consultation summary"""
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescription_ids: Optional[List[str]] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    doctor_notes: Optional[str] = None


class ConsultationSummaryResponse(BaseModel):
    """Consultation summary response"""
    consultation_id: str
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescription_ids: Optional[List[str]] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConsultationMessageCreate(BaseModel):
    """Create consultation message"""
    content: str
    message_type: str = "text"  # text, file, image
    attachment_url: Optional[str] = None


class ConsultationMessageResponse(BaseModel):
    """Consultation message response"""
    id: int
    consultation_id: int
    sender_user_id: str
    content: str
    message_type: str
    attachment_url: Optional[str] = None
    sent_at: datetime

    class Config:
        from_attributes = True


class ConsultationListResponse(BaseModel):
    """Consultation list response"""
    consultation_id: str
    doctor_user_id: Optional[str] = None
    patient_user_id: Optional[str] = None
    status: str
    scheduled_at: datetime
    type: str
    created_at: datetime

    class Config:
        from_attributes = True
