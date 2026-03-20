"""
Caregiver management endpoints.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import CaregiverLink, Consultation, RefillRequest, Report, Alert

router = APIRouter(prefix="/caregiver", tags=["Caregiver"])


@router.post("/link")
def link_caregiver_to_patient(
    patient_email: str,
    relationship_type: str,
    permissions: list = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link caregiver to patient (invite by email).
    """
    # TODO: Find patient by email
    # TODO: Send invite link to patient email

    link = CaregiverLink(
        caregiver_user_id=user["user_id"],
        patient_user_id="patient_id",  # TODO: Use actual patient_id
        relationship_type=relationship_type,
        permissions=permissions or ["view_reports", "view_medications"],
        is_active=False  # Pending patient approval
    )

    db.add(link)
    db.commit()

    return {
        "message": "Caregiver invitation sent",
        "patient_email": patient_email,
        "relationship_type": relationship_type
    }


@router.get("/patient")
def get_patient_summary(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get linked patient's summary (reports, refills, consultations, alerts).
    """
    # Get caregiver link
    link = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_user_id == user["user_id"],
        CaregiverLink.is_active == True
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient link"
        )

    patient_id = link.patient_user_id

    # Get patient data
    recent_reports = db.query(Report).filter(
        Report.user_id == patient_id
    ).order_by(Report.uploaded_at.desc()).limit(5).all()

    pending_refills = db.query(RefillRequest).filter(
        RefillRequest.patient_user_id == patient_id,
        RefillRequest.status == "pending"
    ).all()

    upcoming_consultations = db.query(Consultation).filter(
        Consultation.patient_user_id == patient_id,
        Consultation.status == "scheduled",
        Consultation.scheduled_at > datetime.utcnow()
    ).all()

    active_alerts = db.query(Alert).filter(
        Alert.user_id == patient_id,
        Alert.is_acknowledged == False
    ).all()

    return {
        "patient_id": patient_id,
        "relationship": link.relationship_type,
        "recent_reports_count": len(recent_reports),
        "pending_refills_count": len(pending_refills),
        "upcoming_consultations_count": len(upcoming_consultations),
        "active_alerts_count": len(active_alerts),
        "recent_reports": [
            {
                "report_id": r.report_id,
                "filename": r.filename,
                "report_type": r.report_type,
                "uploaded_at": r.uploaded_at
            }
            for r in recent_reports
        ]
    }


@router.post("/patient/refill-assist")
def assist_with_refill(
    prescription_id: str,
    quantity: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assist patient with refill request as caregiver.
    """
    # Verify caregiver has access
    link = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_user_id == user["user_id"],
        CaregiverLink.is_active == True
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to patient"
        )

    # TODO: Create refill request on behalf of patient

    return {"message": "Refill assistance submitted for patient approval"}


@router.get("/patient/alerts")
def get_patient_alerts(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's active alerts (caregiver view).
    """
    link = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_user_id == user["user_id"],
        CaregiverLink.is_active == True
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient link"
        )

    alerts = db.query(Alert).filter(
        Alert.user_id == link.patient_user_id,
        Alert.is_acknowledged == False
    ).order_by(Alert.created_at.desc()).all()

    return {
        "patient_id": link.patient_user_id,
        "alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at
            }
            for a in alerts
        ]
    }


@router.post("/patient/emergency-escalate")
def create_emergency_alert(
    message: str,
    severity: str = "critical",
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create emergency alert for patient (caregiver escalation).
    """
    link = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_user_id == user["user_id"],
        CaregiverLink.is_active == True
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient link"
        )

    # Create emergency alert
    alert = Alert(
        alert_id=str(uuid.uuid4()),
        user_id=link.patient_user_id,
        alert_type="caregiver_emergency",
        severity=severity,
        message=f"Emergency alert from caregiver: {message}",
        created_at=datetime.utcnow()
    )

    db.add(alert)
    db.commit()

    # TODO: Send notifications to patient and care team

    return {
        "message": "Emergency alert created",
        "alert_id": alert.alert_id,
        "severity": severity
    }
