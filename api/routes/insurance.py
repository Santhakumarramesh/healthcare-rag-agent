"""
Insurance management endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import InsuranceProfile, InsuranceVerification
from schemas.insurance import (
    InsuranceCreate, InsuranceUpdate, InsuranceResponse,
    InsuranceSnapshotResponse, InsuranceVerificationResponse
)

router = APIRouter(prefix="/insurance", tags=["Insurance"])


@router.get("/", response_model=list[InsuranceResponse])
def list_insurance_profiles(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List insurance profiles for current user.
    """
    profiles = db.query(InsuranceProfile).filter(
        InsuranceProfile.user_id == user["user_id"]
    ).all()

    return profiles


@router.post("/", response_model=InsuranceResponse)
def add_insurance(
    request: InsuranceCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add new insurance profile.
    """
    insurance = InsuranceProfile(
        insurance_id=str(uuid.uuid4()),
        user_id=user["user_id"],
        provider_name=request.provider_name,
        plan_name=request.plan_name,
        member_id=request.member_id,
        group_number=request.group_number,
        insurance_type=request.insurance_type,
        deductible=request.deductible,
        copay=request.copay,
        effective_date=request.effective_date,
        expiry_date=request.expiry_date,
        status="active"
    )

    db.add(insurance)
    db.commit()
    db.refresh(insurance)

    return insurance


@router.put("/{insurance_id}", response_model=InsuranceResponse)
def update_insurance(
    insurance_id: str,
    request: InsuranceUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update insurance profile.
    """
    insurance = db.query(InsuranceProfile).filter(
        InsuranceProfile.insurance_id == insurance_id,
        InsuranceProfile.user_id == user["user_id"]
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(insurance, field, value)

    db.commit()
    db.refresh(insurance)

    return insurance


@router.post("/{insurance_id}/upload-card")
def upload_insurance_card(
    insurance_id: str,
    card_front_url: str,
    card_back_url: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload insurance card images (front and back).
    """
    insurance = db.query(InsuranceProfile).filter(
        InsuranceProfile.insurance_id == insurance_id,
        InsuranceProfile.user_id == user["user_id"]
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found"
        )

    insurance.card_front_url = card_front_url
    insurance.card_back_url = card_back_url

    db.commit()

    return {"message": "Insurance card uploaded successfully"}


@router.get("/{insurance_id}/verify", response_model=InsuranceVerificationResponse)
def verify_insurance(
    insurance_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger insurance verification.
    """
    insurance = db.query(InsuranceProfile).filter(
        InsuranceProfile.insurance_id == insurance_id,
        InsuranceProfile.user_id == user["user_id"]
    ).first()

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found"
        )

    # Create verification record
    verification = InsuranceVerification(
        insurance_id=insurance.id,
        verification_type="auto_verify",
        status="pending"
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    # TODO: Call insurance verification API

    return {
        "insurance_id": insurance.insurance_id,
        "verification_type": verification.verification_type,
        "status": verification.status,
        "verified_at": verification.verified_at
    }


@router.get("/snapshot")
def get_insurance_snapshot(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick insurance summary for consultation booking.
    """
    profiles = db.query(InsuranceProfile).filter(
        InsuranceProfile.user_id == user["user_id"],
        InsuranceProfile.status == "active"
    ).all()

    snapshots = []
    for profile in profiles:
        snapshots.append({
            "insurance_id": profile.insurance_id,
            "provider_name": profile.provider_name,
            "plan_name": profile.plan_name,
            "copay": profile.copay,
            "status": profile.status
        })

    return {"insurance_profiles": snapshots}
