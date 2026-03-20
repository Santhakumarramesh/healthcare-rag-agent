"""
Patient profile and dashboard endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_roles, get_db
from database.models import User, PatientProfile, Report, RefillRequest, Consultation, Alert, CareScore
from schemas.patient import (
    PatientProfileCreate, PatientProfileUpdate, PatientProfileResponse,
    HealthProfileUpdate, PatientDashboardResponse
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/profile", response_model=PatientProfileResponse)
def get_patient_profile(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's health profile.
    """
    patient = db.query(PatientProfile).filter(
        PatientProfile.user_id == user["user_id"]
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    return patient


@router.put("/profile", response_model=PatientProfileResponse)
def update_patient_profile(
    request: PatientProfileUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update patient's health profile.
    """
    patient = db.query(PatientProfile).filter(
        PatientProfile.user_id == user["user_id"]
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient


@router.post("/health-profile")
def quick_health_profile_setup(
    request: HealthProfileUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick health profile setup for new patients.
    """
    patient = db.query(PatientProfile).filter(
        PatientProfile.user_id == user["user_id"]
    ).first()

    if not patient:
        # Create new profile
        patient = PatientProfile(
            user_id=user["user_id"]
        )
        db.add(patient)

    # Update with provided data
    if request.weight_kg:
        patient.weight_kg = request.weight_kg
    if request.height_cm:
        patient.height_cm = request.height_cm
    if request.chronic_conditions:
        patient.chronic_conditions = request.chronic_conditions
    if request.allergies:
        patient.allergies = request.allergies

    db.commit()

    return {"message": "Health profile updated successfully"}


@router.get("/dashboard", response_model=PatientDashboardResponse)
def get_patient_dashboard(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient dashboard summary with key metrics.

    Returns:
    - Recent reports count
    - Pending refills
    - Upcoming consultations
    - Active alerts
    - Care score
    - Last vital check
    """
    user_id = user["user_id"]

    # Count recent reports (last 30 days)
    recent_reports = db.query(Report).filter(
        Report.user_id == user_id
    ).count()

    # Count pending refills
    pending_refills = db.query(RefillRequest).filter(
        RefillRequest.patient_user_id == user_id,
        RefillRequest.status == "pending"
    ).count()

    # Count upcoming consultations
    from datetime import datetime
    upcoming_consultations = db.query(Consultation).filter(
        Consultation.patient_user_id == user_id,
        Consultation.status == "scheduled",
        Consultation.scheduled_at > datetime.utcnow()
    ).count()

    # Count active alerts
    active_alerts = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_acknowledged == False
    ).count()

    # Get latest care score
    care_score = db.query(CareScore).filter(
        CareScore.user_id == user_id
    ).order_by(CareScore.week_start.desc()).first()

    return {
        "recent_reports_count": recent_reports,
        "pending_refills_count": pending_refills,
        "upcoming_consultations_count": upcoming_consultations,
        "active_alerts_count": active_alerts,
        "care_score": care_score.score if care_score else None,
        "last_vital_check": None  # TODO: Get from vitals_logs
    }
