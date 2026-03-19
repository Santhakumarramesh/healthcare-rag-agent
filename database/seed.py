"""
Seed database with demo users and initial data.

Run this script to populate the database with demo users.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from database.database import init_db, get_db_session
from database.models import User
from services.auth_service import UserRole
import bcrypt
from loguru import logger


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def seed_demo_users():
    """Seed database with demo users"""
    db = get_db_session()
    
    demo_users = [
        {
            "user_id": "admin-001",
            "email": "admin@healthcare.ai",
            "password": "admin123",
            "name": "System Admin",
            "role": UserRole.ADMIN
        },
        {
            "user_id": "doc-001",
            "email": "doctor@healthcare.ai",
            "password": "doctor123",
            "name": "Dr. Smith",
            "role": UserRole.CLINICIAN
        },
        {
            "user_id": "patient-001",
            "email": "patient@healthcare.ai",
            "password": "patient123",
            "name": "John Doe",
            "role": UserRole.PATIENT
        }
    ]
    
    try:
        for user_data in demo_users:
            # Check if user exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                logger.info(f"User already exists: {user_data['email']}")
                continue
            
            user = User(
                user_id=user_data["user_id"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
                active=True
            )
            db.add(user)
            logger.success(f"Created user: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        logger.success("Demo users seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Seeding demo users...")
    seed_demo_users()
    
    logger.info("Database seeding complete!")
