"""
Doctor profile and availability endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_roles, get_db
from database.models import User, DoctorProfile, DoctorAvailability, Consultation
from schemas.doctor import (
    DoctorProfileCreate, DoctorProfileUpdate, DoctorProfileResponse,
    DoctorSearchQuery, DoctorListResponse
)

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/search", response_model=list[DoctorListResponse])
@router.get("/", response_model=list[DoctorListResponse])
def search_doctors(
    query: DoctorSearchQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    Search and list doctors with filtering.

    Filter by:
    - specialty
    - language
    - insurance
    - availability_date
    - min_rating
    """
    q = db.query(User, DoctorProfile).join(
        DoctorProfile, User.user_id == DoctorProfile.user_id
    ).filter(User.role == "doctor")

    # Apply filters
    if query.specialty:
        q = q.filter(DoctorProfile.specialties.contains([query.specialty]))

    if query.language:
        q = q.filter(DoctorProfile.languages_spoken.contains([query.language]))

    if query.insurance:
        q = q.filter(DoctorProfile.accepted_insurances.contains([query.insurance]))

    if query.min_rating:
        q = q.filter(DoctorProfile.rating >= query.min_rating)

    # Pagination
    offset = (query.page - 1) * query.per_page
    doctors = q.offset(offset).limit(query.per_page).all()

    results = []
    for user, profile in doctors:
        results.append({
            "user_id": user.user_id,
            "name": user.name,
            "specialties": profile.specialties or [],
            "rating": profile.rating,
            "total_reviews": profile.total_reviews,
            "consultation_fee": profile.consultation_fee,
            "is_available_online": profile.is_available_online,
            "profile_photo_url": profile.profile_photo_url
        })

    return results


@router.get("/{doctor_id}", response_model=DoctorProfileResponse)
def get_doctor_profile(
    doctor_id: str,
    db: Session = Depends(get_db)
):
    """
    Get doctor profile details.
    """
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == doctor_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return profile


@router.post("/register")
def register_as_doctor(
    request: DoctorProfileCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register user as a doctor (creates pending DoctorProfile).
    """
    # Check if already a doctor
    existing = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == user["user_id"]
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered as doctor"
        )

    # Create doctor profile
    profile = DoctorProfile(
        user_id=user["user_id"],
        license_number=request.license_number,
        npi_number=request.npi_number,
        specialties=request.specialties,
        languages_spoken=request.languages_spoken,
        jurisdictions=request.jurisdictions,
        years_experience=request.years_experience,
        bio=request.bio,
        consultation_fee=request.consultation_fee,
        consultation_duration_min=request.consultation_duration_min,
        accepts_insurance=request.accepts_insurance,
        accepted_insurances=request.accepted_insurances,
        verification_status="pending"
    )

    db.add(profile)
    db.commit()

    return {"message": "Doctor registration submitted for approval"}


@router.put("/profile", response_model=DoctorProfileResponse)
def update_doctor_profile(
    request: DoctorProfileUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update doctor's profile (requires doctor role).
    """
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == user["user_id"]
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


@router.get("/availability/list")
@router.get("/availability")
def get_doctor_availability(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor's availability slots.
    """
    slots = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == user["user_id"]
    ).all()

    return {
        "doctor_id": user["user_id"],
        "availability_slots": slots
    }


@router.post("/availability/set")
@router.post("/availability")
def set_doctor_availability(
    day_of_week: int,
    start_time: str,
    end_time: str,
    slot_minutes: int = 30,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set doctor availability slots.
    """
    slot = DoctorAvailability(
        doctor_id=user["user_id"],
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        slot_minutes=slot_minutes,
        is_available=True
    )

    db.add(slot)
    db.commit()

    return {"message": "Availability slot created"}


@router.get("/patients/queue")
def get_patient_queue(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor's patient queue (upcoming consultations).
    """
    consultations = db.query(Consultation).filter(
        Consultation.doctor_user_id == user["user_id"],
        Consultation.status == "scheduled",
        Consultation.scheduled_at > datetime.utcnow()
    ).order_by(Consultation.scheduled_at).all()

    return {
        "doctor_id": user["user_id"],
        "patient_queue": [
            {
                "consultation_id": c.consultation_id,
                "patient_id": c.patient_user_id,
                "scheduled_at": c.scheduled_at,
                "type": c.type,
                "reason": c.reason
            }
            for c in consultations
        ]
    }


@router.get("/patients/{patient_id}")
def get_patient_details(
    patient_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient detail for doctor view.

    Only accessible to doctor if they have active consultation.
    """
    # Check if doctor has active consultation with patient
    consultation = db.query(Consultation).filter(
        Consultation.doctor_user_id == user["user_id"],
        Consultation.patient_user_id == patient_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active consultation with this patient"
        )

    patient = db.query(User).filter(User.user_id == patient_id).first()

    return {
        "user_id": patient.user_id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone
        # TODO: Include patient profile, recent reports, medications, etc.
    }
