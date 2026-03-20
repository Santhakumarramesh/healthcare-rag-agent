"""
Health tracking and wellness log endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db
from database.models import (
    SymptomLog, MedicationLog, HydrationLog, ActivityLog, VitalsLog,
    SleepLog, NutritionLog, CareScore
)
from schemas.tracking import (
    SymptomLogCreate, SymptomLogResponse, MedicationLogCreate, MedicationLogResponse,
    HydrationLogCreate, HydrationLogResponse, ActivityLogCreate, ActivityLogResponse,
    VitalsLogCreate, VitalsLogResponse, SleepLogCreate, SleepLogResponse,
    NutritionLogCreate, NutritionLogResponse, TrackingSummaryResponse
)

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/symptoms", response_model=SymptomLogResponse)
def log_symptoms(
    request: SymptomLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log symptoms.
    """
    log = SymptomLog(
        user_id=user["user_id"],
        symptoms=request.symptoms,
        overall=request.overall,
        notes=request.notes,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/medications", response_model=MedicationLogResponse)
def log_medication(
    request: MedicationLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log medication taken or skipped.
    """
    log = MedicationLog(
        user_id=user["user_id"],
        medication_name=request.medication_name,
        dosage=request.dosage,
        taken=request.taken,
        taken_at=request.taken_at,
        skipped_reason=request.skipped_reason,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/hydration", response_model=HydrationLogResponse)
def log_hydration(
    request: HydrationLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log water intake.
    """
    log = HydrationLog(
        user_id=user["user_id"],
        amount_ml=request.amount_ml,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/activity", response_model=ActivityLogResponse)
def log_activity(
    request: ActivityLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log physical activity.
    """
    log = ActivityLog(
        user_id=user["user_id"],
        steps=request.steps,
        calories=request.calories,
        active_min=request.active_min,
        activity_type=request.activity_type,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/vitals", response_model=VitalsLogResponse)
def log_vitals(
    request: VitalsLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log vital signs.
    """
    log = VitalsLog(
        user_id=user["user_id"],
        heart_rate=request.heart_rate,
        systolic_bp=request.systolic_bp,
        diastolic_bp=request.diastolic_bp,
        temperature_c=request.temperature_c,
        blood_glucose=request.blood_glucose,
        spo2=request.spo2,
        weight_kg=request.weight_kg,
        notes=request.notes,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/sleep", response_model=SleepLogResponse)
def log_sleep(
    request: SleepLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log sleep.
    """
    log = SleepLog(
        user_id=user["user_id"],
        duration_min=request.duration_min,
        quality=request.quality,
        sleep_time=request.sleep_time,
        wake_time=request.wake_time,
        notes=request.notes,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.post("/nutrition", response_model=NutritionLogResponse)
def log_nutrition(
    request: NutritionLogCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log nutrition/meals.
    """
    log = NutritionLog(
        user_id=user["user_id"],
        meal_type=request.meal_type,
        items=request.items,
        total_cal=request.total_cal,
        notes=request.notes,
        logged_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.get("/summary", response_model=TrackingSummaryResponse)
def get_tracking_summary(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly aggregated tracking summary across all tracking types.
    """
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Medication adherence
    total_meds = db.query(MedicationLog).filter(
        MedicationLog.user_id == user["user_id"],
        MedicationLog.logged_at >= week_ago
    ).count()
    taken_meds = db.query(MedicationLog).filter(
        MedicationLog.user_id == user["user_id"],
        MedicationLog.logged_at >= week_ago,
        MedicationLog.taken == True
    ).count()
    medication_adherence = (taken_meds / total_meds * 100) if total_meds > 0 else 0

    # Average heart rate
    vitals = db.query(VitalsLog).filter(
        VitalsLog.user_id == user["user_id"],
        VitalsLog.logged_at >= week_ago,
        VitalsLog.heart_rate.isnot(None)
    ).all()
    avg_hr = sum(v.heart_rate for v in vitals) / len(vitals) if vitals else None

    # Average blood pressure
    bp_readings = [(v.systolic_bp, v.diastolic_bp) for v in vitals if v.systolic_bp and v.diastolic_bp]
    avg_bp = {
        "systolic": sum(b[0] for b in bp_readings) / len(bp_readings),
        "diastolic": sum(b[1] for b in bp_readings) / len(bp_readings)
    } if bp_readings else None

    # Total steps
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == user["user_id"],
        ActivityLog.logged_at >= week_ago
    ).all()
    total_steps = sum(a.steps for a in activities if a.steps) if activities else None

    # Total hydration
    hydration = db.query(HydrationLog).filter(
        HydrationLog.user_id == user["user_id"],
        HydrationLog.logged_at >= week_ago
    ).all()
    total_hydration = sum(h.amount_ml for h in hydration) if hydration else None

    # Average sleep
    sleep = db.query(SleepLog).filter(
        SleepLog.user_id == user["user_id"],
        SleepLog.logged_at >= week_ago
    ).all()
    avg_sleep = sum(s.duration_min for s in sleep) / len(sleep) if sleep else None

    # Total meals
    nutrition = db.query(NutritionLog).filter(
        NutritionLog.user_id == user["user_id"],
        NutritionLog.logged_at >= week_ago
    ).count()

    return {
        "week_start": week_ago,
        "medication_adherence": medication_adherence,
        "average_heart_rate": avg_hr,
        "average_bp": avg_bp,
        "total_steps": total_steps,
        "total_hydration_ml": total_hydration,
        "average_sleep_min": avg_sleep,
        "average_mood": None,  # TODO: Calculate from symptom logs
        "total_meals_logged": nutrition
    }


@router.get("/trends")
def get_trend_data(
    metric: str,
    days: int = 30,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend data for a specific metric over time.

    Metrics: heart_rate, blood_pressure, weight, steps, sleep_duration, medication_adherence
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    if metric == "heart_rate":
        data = db.query(VitalsLog).filter(
            VitalsLog.user_id == user["user_id"],
            VitalsLog.logged_at >= start_date,
            VitalsLog.heart_rate.isnot(None)
        ).order_by(VitalsLog.logged_at).all()

        return {
            "metric": metric,
            "data": [
                {"timestamp": v.logged_at, "value": v.heart_rate}
                for v in data
            ]
        }

    elif metric == "blood_pressure":
        data = db.query(VitalsLog).filter(
            VitalsLog.user_id == user["user_id"],
            VitalsLog.logged_at >= start_date,
            VitalsLog.systolic_bp.isnot(None)
        ).order_by(VitalsLog.logged_at).all()

        return {
            "metric": metric,
            "data": [
                {
                    "timestamp": v.logged_at,
                    "systolic": v.systolic_bp,
                    "diastolic": v.diastolic_bp
                }
                for v in data
            ]
        }

    elif metric == "weight":
        data = db.query(VitalsLog).filter(
            VitalsLog.user_id == user["user_id"],
            VitalsLog.logged_at >= start_date,
            VitalsLog.weight_kg.isnot(None)
        ).order_by(VitalsLog.logged_at).all()

        return {
            "metric": metric,
            "data": [
                {"timestamp": v.logged_at, "value": v.weight_kg}
                for v in data
            ]
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported metric: {metric}"
        )
