"""
Consultation booking and management endpoints.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import Consultation, ConsultationMessage, ConsultationSummary, DoctorAvailability
from schemas.consultation import (
    BookConsultationRequest, ConsultationResponse, ConsultationSummaryCreate,
    ConsultationMessageCreate, ConsultationMessageResponse, ConsultationListResponse
)

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post("/book", response_model=ConsultationResponse)
def book_consultation(
    request: BookConsultationRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Book a consultation with a doctor.
    """
    # Create consultation
    consultation = Consultation(
        consultation_id=str(uuid.uuid4()),
        patient_user_id=user["user_id"],
        doctor_user_id=request.doctor_user_id,
        status="scheduled",
        scheduled_at=request.scheduled_at,
        type=request.type,
        reason=request.reason,
        report_ids=request.report_ids,
        insurance_used=request.insurance_id
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return consultation


@router.get("/", response_model=list[ConsultationListResponse])
def list_consultations(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List consultations for current user.

    Patients see their consultations, doctors see theirs.
    """
    # Check user role
    consultations = db.query(Consultation).filter(
        (Consultation.patient_user_id == user["user_id"]) |
        (Consultation.doctor_user_id == user["user_id"])
    ).order_by(Consultation.scheduled_at.desc()).all()

    return consultations


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get consultation details.
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    # Verify access
    if consultation.patient_user_id != user["user_id"] and consultation.doctor_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this consultation"
        )

    return consultation


@router.post("/{consultation_id}/complete")
def complete_consultation(
    consultation_id: str,
    request: ConsultationSummaryCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark consultation as complete and create summary (doctor only).
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if consultation.doctor_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctor can complete consultation"
        )

    # Update consultation status
    consultation.status = "completed"
    consultation.updated_at = datetime.utcnow()

    # Create summary
    summary = ConsultationSummary(
        consultation_id=consultation.id,
        diagnosis=request.diagnosis,
        treatment_plan=request.treatment_plan,
        prescription_ids=request.prescription_ids,
        follow_up_date=request.follow_up_date,
        follow_up_notes=request.follow_up_notes,
        doctor_notes=request.doctor_notes
    )

    db.add(summary)
    db.commit()

    return {"message": "Consultation completed"}


@router.post("/{consultation_id}/cancel")
def cancel_consultation(
    consultation_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a consultation.
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if consultation.patient_user_id != user["user_id"] and consultation.doctor_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this consultation"
        )

    consultation.status = "cancelled"
    consultation.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Consultation cancelled"}


@router.get("/{consultation_id}/messages", response_model=list[ConsultationMessageResponse])
def get_consultation_messages(
    consultation_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat messages for a consultation.
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    # Verify access
    if consultation.patient_user_id != user["user_id"] and consultation.doctor_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view messages"
        )

    messages = db.query(ConsultationMessage).filter(
        ConsultationMessage.consultation_id == consultation.id
    ).order_by(ConsultationMessage.sent_at).all()

    return messages


@router.post("/{consultation_id}/messages", response_model=ConsultationMessageResponse)
def send_consultation_message(
    consultation_id: str,
    request: ConsultationMessageCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message during consultation.
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    # Verify access
    if consultation.patient_user_id != user["user_id"] and consultation.doctor_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send messages"
        )

    message = ConsultationMessage(
        consultation_id=consultation.id,
        sender_user_id=user["user_id"],
        content=request.content,
        message_type=request.message_type,
        attachment_url=request.attachment_url,
        sent_at=datetime.utcnow()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message
