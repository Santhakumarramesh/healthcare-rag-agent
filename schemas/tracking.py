"""
Pydantic schemas for health tracking endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SymptomLogCreate(BaseModel):
    """Create symptom log request"""
    symptoms: List[Dict[str, Any]]  # [{name, severity, notes}, ...]
    overall: Optional[int] = None
    notes: Optional[str] = None


class SymptomLogResponse(BaseModel):
    """Symptom log response"""
    id: int
    user_id: str
    symptoms: List[Dict[str, Any]]
    overall: Optional[int] = None
    notes: Optional[str] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class MedicationLogCreate(BaseModel):
    """Create medication log request"""
    prescription_id: Optional[str] = None
    medication_name: str
    dosage: str
    taken: bool
    taken_at: Optional[datetime] = None
    skipped_reason: Optional[str] = None


class MedicationLogResponse(BaseModel):
    """Medication log response"""
    id: int
    user_id: str
    medication_name: str
    dosage: str
    taken: bool
    taken_at: Optional[datetime] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class HydrationLogCreate(BaseModel):
    """Create hydration log request"""
    amount_ml: int


class HydrationLogResponse(BaseModel):
    """Hydration log response"""
    id: int
    user_id: str
    amount_ml: int
    logged_at: datetime

    class Config:
        from_attributes = True


class ActivityLogCreate(BaseModel):
    """Create activity log request"""
    steps: Optional[int] = None
    calories: Optional[float] = None
    active_min: Optional[int] = None
    activity_type: Optional[str] = None


class ActivityLogResponse(BaseModel):
    """Activity log response"""
    id: int
    user_id: str
    steps: Optional[int] = None
    calories: Optional[float] = None
    active_min: Optional[int] = None
    activity_type: Optional[str] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class VitalsLogCreate(BaseModel):
    """Create vitals log request"""
    heart_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    temperature_c: Optional[float] = None
    blood_glucose: Optional[float] = None
    spo2: Optional[float] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None


class VitalsLogResponse(BaseModel):
    """Vitals log response"""
    id: int
    user_id: str
    heart_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    temperature_c: Optional[float] = None
    blood_glucose: Optional[float] = None
    spo2: Optional[float] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class SleepLogCreate(BaseModel):
    """Create sleep log request"""
    duration_min: int
    quality: Optional[int] = None  # 1-5 scale
    sleep_time: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    notes: Optional[str] = None


class SleepLogResponse(BaseModel):
    """Sleep log response"""
    id: int
    user_id: str
    duration_min: int
    quality: Optional[int] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class NutritionLogCreate(BaseModel):
    """Create nutrition log request"""
    meal_type: str  # breakfast, lunch, dinner, snack
    items: List[Dict[str, Any]]
    total_cal: Optional[float] = None
    notes: Optional[str] = None


class NutritionLogResponse(BaseModel):
    """Nutrition log response"""
    id: int
    user_id: str
    meal_type: str
    items: List[Dict[str, Any]]
    total_cal: Optional[float] = None
    logged_at: datetime

    class Config:
        from_attributes = True


class TrackingSummaryResponse(BaseModel):
    """Weekly tracking summary"""
    week_start: datetime
    medication_adherence: Optional[float] = None
    average_heart_rate: Optional[float] = None
    average_bp: Optional[Dict[str, float]] = None
    total_steps: Optional[int] = None
    total_hydration_ml: Optional[int] = None
    average_sleep_min: Optional[float] = None
    average_mood: Optional[int] = None
    total_meals_logged: Optional[int] = None

    class Config:
        from_attributes = True
