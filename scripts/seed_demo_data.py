"""
Seed demo data for HealthCopilot.

Creates:
- Admin user
- Doctor user with verified profile
- Patient user with profile
- Caregiver user with link to patient
- Sample products
- Sample prescription

Run with: python scripts/seed_demo_data.py
"""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import (
    Base, User, PatientProfile, DoctorProfile, CaregiverLink,
    Prescription, Product, DoctorAvailability,
    Report, Consultation, Alert, CareScore,
    HydrationLog, SleepLog, ActivityLog, VitalsLog,
)
from core.security import hash_password


def seed_database():
    """Seed database with demo data."""
    # Create database connection
    # TODO: Use actual database URL from config
    DATABASE_URL = "sqlite:///./healthcopilot.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    # Create tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing demo users
        db.query(User).filter(User.email.in_([
            "admin@healthcopilot.ai",
            "doctor@healthcopilot.ai",
            "patient@healthcopilot.ai",
            "caregiver@healthcopilot.ai"
        ])).delete()
        db.commit()

        # 1. Create admin user
        admin = User(
            user_id="admin_001",
            email="admin@healthcopilot.ai",
            phone="+1234567890",
            password_hash=hash_password("admin123"),
            name="Admin User",
            role="admin",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(admin)
        db.flush()
        print("Created admin user: admin@healthcopilot.ai")

        # 2. Create doctor user
        doctor = User(
            user_id="doctor_001",
            email="doctor@healthcopilot.ai",
            phone="+1987654321",
            password_hash=hash_password("doctor123"),
            name="Dr. Sarah Johnson",
            role="doctor",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(doctor)
        db.flush()
        print("Created doctor user: doctor@healthcopilot.ai")

        # Create doctor profile
        doctor_profile = DoctorProfile(
            user_id=doctor.user_id,
            license_number="MD123456",
            npi_number="1234567890",
            specialties=["Cardiology", "Internal Medicine"],
            languages_spoken=["English", "Spanish"],
            jurisdictions=["California", "Nevada"],
            years_experience=15,
            bio="Experienced cardiologist specializing in preventive care.",
            consultation_fee=150.0,
            consultation_duration_min=30,
            accepts_insurance=True,
            accepted_insurances=["Blue Cross", "Aetna", "UnitedHealth"],
            rating=4.8,
            total_reviews=42,
            verification_status="verified",
            is_available_online=True,
            profile_photo_url="https://example.com/doctor.jpg",
            created_at=datetime.utcnow()
        )
        db.add(doctor_profile)
        db.flush()
        print("Created doctor profile for Dr. Sarah Johnson")

        # Create doctor availability
        for day in range(5):  # Monday to Friday
            for hour in [9, 14]:  # 9am and 2pm slots
                slot = DoctorAvailability(
                    doctor_id=doctor.user_id,
                    day_of_week=day,
                    start_time=f"{hour:02d}:00",
                    end_time=f"{hour+1:02d}:00",
                    slot_minutes=30,
                    is_available=True,
                    timezone="America/Los_Angeles"
                )
                db.add(slot)
        db.flush()
        print("Created availability slots for doctor")

        # 3. Create patient user
        patient = User(
            user_id="patient_001",
            email="patient@healthcopilot.ai",
            phone="+1555555555",
            password_hash=hash_password("patient123"),
            name="John Smith",
            role="patient",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(patient)
        db.flush()
        print("Created patient user: patient@healthcopilot.ai")

        # Create patient profile
        patient_profile = PatientProfile(
            user_id=patient.user_id,
            date_of_birth=datetime(1985, 6, 15),
            gender="Male",
            blood_type="O+",
            height_cm=180.0,
            weight_kg=85.0,
            allergies=["Penicillin"],
            chronic_conditions=["Hypertension", "Type 2 Diabetes"],
            emergency_contact={
                "name": "Jane Smith",
                "phone": "+1555555556",
                "relationship": "Spouse"
            },
            address={
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102",
                "country": "USA"
            },
            timezone="America/Los_Angeles",
            preferred_lang="en",
            created_at=datetime.utcnow()
        )
        db.add(patient_profile)
        db.flush()
        print("Created patient profile for John Smith")

        # 4. Create caregiver user
        caregiver = User(
            user_id="caregiver_001",
            email="caregiver@healthcopilot.ai",
            phone="+1777777777",
            password_hash=hash_password("care123"),
            name="Jane Smith",
            role="caregiver",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(caregiver)
        db.flush()
        print("Created caregiver user: caregiver@healthcopilot.ai")

        # Link caregiver to patient
        caregiver_link = CaregiverLink(
            caregiver_user_id=caregiver.user_id,
            patient_user_id=patient.user_id,
            relationship_type="Spouse",
            permissions=["view_reports", "view_medications", "view_alerts"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(caregiver_link)
        db.flush()
        print("Created caregiver link for Jane Smith -> John Smith")

        # 5. Create sample products
        products = [
            Product(
                product_id=str(uuid.uuid4()),
                name="Blood Pressure Monitor",
                description="Digital blood pressure monitor with Bluetooth connectivity",
                category="Medical Devices",
                price=79.99,
                image_url="https://example.com/bp-monitor.jpg",
                tags=["hypertension", "monitoring", "home-care"],
                conditions=["Hypertension", "Cardiovascular Disease"],
                is_active=True,
                stock=50,
                created_at=datetime.utcnow()
            ),
            Product(
                product_id=str(uuid.uuid4()),
                name="Glucose Meter Kit",
                description="Complete glucose meter kit with 50 test strips",
                category="Diabetes Care",
                price=49.99,
                image_url="https://example.com/glucose-meter.jpg",
                tags=["diabetes", "monitoring", "glucose"],
                conditions=["Type 2 Diabetes", "Type 1 Diabetes"],
                is_active=True,
                stock=75,
                created_at=datetime.utcnow()
            )
        ]

        for product in products:
            db.add(product)
        db.flush()
        print("Created 2 sample products")

        # 6. Create sample prescription
        prescription = Prescription(
            prescription_id=str(uuid.uuid4()),
            patient_user_id=patient.user_id,
            doctor_user_id=doctor.user_id,
            medication_name="Lisinopril",
            generic_name="lisinopril",
            dosage="10mg",
            frequency="Once daily",
            duration_days=90,
            instructions="Take once daily in the morning with or without food",
            quantity=30,
            refills_allowed=3,
            refills_used=0,
            status="active",
            prescribed_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365),
            is_controlled=False,
            auto_renew=True,
            created_at=datetime.utcnow()
        )
        db.add(prescription)
        db.flush()
        print("Created sample prescription for patient")

        # 7. Sample reports for patient
        report_data = [
            ("Blood Panel - CBC", "cbc_results.pdf", "analyzed", -5),
            ("HbA1c Test", "hba1c_march.pdf", "analyzed", -12),
            ("Chest X-Ray", "chest_xray.pdf", "processing", -1),
            ("Lipid Profile", "lipid_panel.pdf", "analyzed", -20),
        ]
        for rtype, fname, status, days_ago in report_data:
            db.add(Report(
                report_id=str(uuid.uuid4()),
                user_id=patient.user_id,
                file_name=fname,
                report_type=rtype,
                status=status,
                created_at=datetime.utcnow() + timedelta(days=days_ago),
            ))
        db.flush()
        print("Created 4 sample reports")

        # 8. Upcoming consultation
        db.add(Consultation(
            consultation_id=str(uuid.uuid4()),
            patient_user_id=patient.user_id,
            doctor_user_id=doctor.user_id,
            type="video",
            reason="Follow-up on HbA1c results and medication review",
            status="scheduled",
            scheduled_at=datetime.utcnow() + timedelta(days=2),
            created_at=datetime.utcnow(),
        ))
        db.flush()
        print("Created upcoming consultation")

        # 9. Active alert
        db.add(Alert(
            alert_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            message="HbA1c of 7.8% is above target. Consider dietary adjustments.",
            severity="high",
            alert_type="lab_result",
            is_acknowledged=False,
            created_at=datetime.utcnow() - timedelta(hours=3),
        ))
        db.flush()
        print("Created health alert for patient")

        # 10. Care score
        db.add(CareScore(
            score_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            score=72,
            medication_adherence=85,
            activity_score=65,
            nutrition_score=68,
            week_start=datetime.utcnow() - timedelta(days=7),
            created_at=datetime.utcnow(),
        ))
        db.flush()
        print("Created care score for patient")

        # 11. Today's tracking data
        db.add(HydrationLog(
            log_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            amount_ml=1200,
            logged_at=datetime.utcnow(),
        ))
        db.add(ActivityLog(
            log_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            steps=4200,
            duration_min=35,
            activity_type="walking",
            logged_at=datetime.utcnow(),
        ))
        db.add(SleepLog(
            log_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            duration_hours=7.5,
            quality_score=80,
            sleep_date=datetime.utcnow().date(),
            created_at=datetime.utcnow(),
        ))
        db.add(VitalsLog(
            log_id=str(uuid.uuid4()),
            user_id=patient.user_id,
            systolic_bp=128,
            diastolic_bp=82,
            heart_rate=74,
            blood_glucose=142,
            logged_at=datetime.utcnow() - timedelta(hours=2),
        ))
        db.flush()
        print("Created today's tracking data")

        # Commit all changes
        db.commit()
        print("\n✓ Demo data seeded successfully!")
        print("\nLogin credentials:")
        print("  Admin:    admin@healthcopilot.ai / admin123")
        print("  Doctor:   doctor@healthcopilot.ai / doctor123")
        print("  Patient:  patient@healthcopilot.ai / patient123")
        print("  Caregiver: caregiver@healthcopilot.ai / care123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
