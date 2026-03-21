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


@router.get("/dashboard")
def get_patient_dashboard(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient dashboard summary — rich response for frontend.

    Returns counts, recent reports, alerts, care score, AI insights,
    today's tracking summary, and upcoming consultations.
    """
    from datetime import datetime, date

    user_id = user["user_id"]
    today = date.today()

    # ── Recent reports ────────────────────────────────────────────────────────
    recent_report_rows = (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.created_at.desc())
        .limit(5)
        .all()
    )
    recent_reports = [
        {
            "id": r.report_id,
            "report_type": r.report_type or "Medical Report",
            "file_name": r.file_name or "report.pdf",
            "status": r.status or "uploaded",
            "created_at": r.created_at.isoformat() if r.created_at else datetime.utcnow().isoformat(),
        }
        for r in recent_report_rows
    ]

    # ── Alerts ────────────────────────────────────────────────────────────────
    alert_rows = (
        db.query(Alert)
        .filter(Alert.user_id == user_id, Alert.is_acknowledged == False)
        .order_by(Alert.created_at.desc())
        .limit(5)
        .all()
    )
    alerts = [
        {
            "id": a.alert_id,
            "message": a.message,
            "severity": a.severity or "medium",
        }
        for a in alert_rows
    ]

    # ── AI Insights ───────────────────────────────────────────────────────────
    try:
        from database.models import AIInsight
        insight_rows = (
            db.query(AIInsight)
            .filter(AIInsight.user_id == user_id)
            .order_by(AIInsight.created_at.desc())
            .limit(3)
            .all()
        )
        insights = [
            {
                "id": i.insight_id,
                "title": i.title or "Health Insight",
                "what_changed": i.what_changed or "",
                "why_it_matters": i.why_it_matters or "",
                "what_to_do": i.what_to_do or "",
                "severity": i.severity or "info",
            }
            for i in insight_rows
        ]
    except Exception:
        insights = []

    # ── Care score ────────────────────────────────────────────────────────────
    care_score_row = (
        db.query(CareScore)
        .filter(CareScore.user_id == user_id)
        .order_by(CareScore.week_start.desc())
        .first()
    )
    care_score = care_score_row.score if care_score_row else None
    care_score_breakdown = {
        "adherence": care_score_row.medication_adherence if care_score_row else None,
        "activity": care_score_row.activity_score if care_score_row else None,
        "nutrition": care_score_row.nutrition_score if care_score_row else None,
    } if care_score_row else None

    # ── Upcoming consultations ────────────────────────────────────────────────
    upcoming_rows = (
        db.query(Consultation)
        .filter(
            Consultation.patient_user_id == user_id,
            Consultation.status == "scheduled",
            Consultation.scheduled_at > datetime.utcnow(),
        )
        .order_by(Consultation.scheduled_at)
        .limit(3)
        .all()
    )
    upcoming_consultations = [
        {
            "id": c.consultation_id,
            "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else "",
            "doctor_name": "Dr. " + (
                db.query(User).filter(User.user_id == c.doctor_user_id).first().name
                if c.doctor_user_id else "Assigned Doctor"
            ),
            "consultation_type": c.type or "video",
        }
        for c in upcoming_rows
    ]

    # ── Today's tracking summary ───────────────────────────────────────────────
    try:
        from database.models import HydrationLog, ActivityLog, SleepLog, SymptomLog
        hydration = (
            db.query(HydrationLog)
            .filter(HydrationLog.user_id == user_id)
            .order_by(HydrationLog.logged_at.desc())
            .first()
        )
        activity = (
            db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.logged_at.desc())
            .first()
        )
        sleep = (
            db.query(SleepLog)
            .filter(SleepLog.user_id == user_id)
            .order_by(SleepLog.sleep_date.desc())
            .first()
        )
        today_summary = {
            "hydration": hydration.amount_ml if hydration else None,
            "steps": activity.steps if activity else None,
            "sleep": sleep.duration_hours if sleep else None,
            "mood": None,
        }
        # Remove None values
        today_summary = {k: v for k, v in today_summary.items() if v is not None}
    except Exception:
        today_summary = {}

    # ── Counts ─────────────────────────────────────────────────────────────────
    pending_refills = db.query(RefillRequest).filter(
        RefillRequest.patient_user_id == user_id,
        RefillRequest.status == "pending"
    ).count()

    return {
        "recent_reports": recent_reports,
        "recent_reports_count": len(recent_reports),
        "alerts": alerts,
        "active_alerts_count": len(alerts),
        "insights": insights,
        "care_score": care_score,
        "care_score_breakdown": care_score_breakdown,
        "upcoming_consultations": upcoming_consultations,
        "upcoming_consultations_count": len(upcoming_consultations),
        "pending_refills_count": pending_refills,
        "today_summary": today_summary,
        "summary": "AI Healthcare Copilot — your reports, care, and follow-up in one place.",
    }
