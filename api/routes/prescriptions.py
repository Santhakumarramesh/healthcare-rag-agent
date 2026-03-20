"""
Prescription and medication management endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import (
    Prescription, RefillRequest, MedicationOrder, DeliveryTracking,
    MedicationSafetyFlag
)
from schemas.prescription import (
    PrescriptionResponse, RefillRequestCreate, RefillRequestResponse,
    RefillApprovalRequest, MedicationOrderResponse, DeliveryTrackingResponse,
    SafetyFlagResponse
)

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.get("/", response_model=list[PrescriptionResponse])
def list_prescriptions(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List prescriptions for current patient.
    """
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_user_id == user["user_id"],
        Prescription.status != "expired"
    ).all()

    results = []
    for rx in prescriptions:
        safety_flags = db.query(MedicationSafetyFlag).filter(
            MedicationSafetyFlag.prescription_id == rx.id
        ).count()

        results.append({
            "prescription_id": rx.prescription_id,
            "patient_user_id": rx.patient_user_id,
            "doctor_user_id": rx.doctor_user_id,
            "medication_name": rx.medication_name,
            "generic_name": rx.generic_name,
            "dosage": rx.dosage,
            "frequency": rx.frequency,
            "duration_days": rx.duration_days,
            "instructions": rx.instructions,
            "quantity": rx.quantity,
            "refills_allowed": rx.refills_allowed,
            "refills_used": rx.refills_used,
            "status": rx.status,
            "prescribed_date": rx.prescribed_date,
            "expiry_date": rx.expiry_date,
            "is_controlled": rx.is_controlled,
            "auto_renew": rx.auto_renew,
            "safety_flags_count": safety_flags,
            "created_at": rx.created_at
        })

    return results


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get prescription details.
    """
    rx = db.query(Prescription).filter(
        Prescription.prescription_id == prescription_id
    ).first()

    if not rx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    if rx.patient_user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this prescription"
        )

    safety_flags = db.query(MedicationSafetyFlag).filter(
        MedicationSafetyFlag.prescription_id == rx.id
    ).count()

    return {
        "prescription_id": rx.prescription_id,
        "patient_user_id": rx.patient_user_id,
        "doctor_user_id": rx.doctor_user_id,
        "medication_name": rx.medication_name,
        "generic_name": rx.generic_name,
        "dosage": rx.dosage,
        "frequency": rx.frequency,
        "duration_days": rx.duration_days,
        "instructions": rx.instructions,
        "quantity": rx.quantity,
        "refills_allowed": rx.refills_allowed,
        "refills_used": rx.refills_used,
        "status": rx.status,
        "prescribed_date": rx.prescribed_date,
        "expiry_date": rx.expiry_date,
        "is_controlled": rx.is_controlled,
        "auto_renew": rx.auto_renew,
        "safety_flags_count": safety_flags,
        "created_at": rx.created_at
    }


@router.get("/{prescription_id}/safety-check", response_model=list[SafetyFlagResponse])
def get_safety_flags(
    prescription_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get safety flags for a prescription.
    """
    rx = db.query(Prescription).filter(
        Prescription.prescription_id == prescription_id
    ).first()

    if not rx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    flags = db.query(MedicationSafetyFlag).filter(
        MedicationSafetyFlag.prescription_id == rx.id
    ).all()

    return flags


@router.post("/refill-request", response_model=RefillRequestResponse)
def create_refill_request(
    request: RefillRequestCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a medication refill request.
    """
    rx = db.query(Prescription).filter(
        Prescription.prescription_id == request.prescription_id,
        Prescription.patient_user_id == user["user_id"]
    ).first()

    if not rx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    if rx.refills_used >= rx.refills_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refills remaining"
        )

    refill = RefillRequest(
        refill_id=str(uuid.uuid4()),
        prescription_id=rx.id,
        patient_user_id=user["user_id"],
        status="pending",
        quantity=request.quantity,
        delivery_address=request.delivery_address,
        notes=request.notes
    )

    db.add(refill)
    db.commit()
    db.refresh(refill)

    return {
        "refill_id": refill.refill_id,
        "prescription_id": refill.prescription_id,
        "patient_user_id": refill.patient_user_id,
        "status": refill.status,
        "quantity": refill.quantity,
        "requested_at": refill.requested_at,
        "reviewed_at": refill.reviewed_at,
        "denial_reason": refill.denial_reason,
        "medication_name": rx.medication_name,
        "dosage": rx.dosage
    }


@router.get("/refill-requests")
def list_refill_requests(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List refill requests for current patient.
    """
    refills = db.query(RefillRequest).filter(
        RefillRequest.patient_user_id == user["user_id"]
    ).order_by(RefillRequest.requested_at.desc()).all()

    return {"refill_requests": refills}


@router.post("/refill-requests/{refill_id}/approve")
def approve_refill(
    refill_id: str,
    request: RefillApprovalRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or deny refill request (doctor/pharmacist only).
    """
    refill = db.query(RefillRequest).filter(
        RefillRequest.refill_id == refill_id
    ).first()

    if not refill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refill request not found"
        )

    if request.approved:
        refill.status = "approved"
        # Create medication order
        order = MedicationOrder(
            order_id=str(uuid.uuid4()),
            refill_id=refill.id,
            patient_id=refill.patient_user_id,
            status="pending"
        )
        db.add(order)
    else:
        refill.status = "denied"
        refill.denial_reason = request.denial_reason

    refill.reviewed_at = __import__("datetime").datetime.utcnow()
    refill.reviewer_id = user["user_id"]

    db.commit()

    return {"message": f"Refill request {refill.status}"}


@router.post("/refill-requests/{refill_id}/deny")
def deny_refill(
    refill_id: str,
    request: RefillApprovalRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deny refill request with reason.
    """
    refill = db.query(RefillRequest).filter(
        RefillRequest.refill_id == refill_id
    ).first()

    if not refill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refill request not found"
        )

    refill.status = "denied"
    refill.denial_reason = request.denial_reason
    refill.reviewed_at = __import__("datetime").datetime.utcnow()
    refill.reviewer_id = user["user_id"]

    db.commit()

    return {"message": "Refill request denied"}


@router.get("/orders", response_model=list[MedicationOrderResponse])
def list_orders(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List medication orders for current patient.
    """
    orders = db.query(MedicationOrder).filter(
        MedicationOrder.patient_id == user["user_id"]
    ).order_by(MedicationOrder.created_at.desc()).all()

    return orders


@router.get("/orders/{order_id}/tracking", response_model=list[DeliveryTrackingResponse])
def get_order_tracking(
    order_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get delivery tracking for medication order.
    """
    order = db.query(MedicationOrder).filter(
        MedicationOrder.order_id == order_id,
        MedicationOrder.patient_id == user["user_id"]
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    tracking = db.query(DeliveryTracking).filter(
        DeliveryTracking.order_id == order.id
    ).order_by(DeliveryTracking.timestamp).all()

    return tracking
