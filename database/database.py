"""
Database Connection and Session Management.

Uses SQLite for easy deployment, but can be switched to PostgreSQL
by changing the DATABASE_URL.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from database.models import Base

# Database configuration
DATABASE_DIR = Path(__file__).parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR}/healthcare_rag.db"
)

# For PostgreSQL, use:
# DATABASE_URL = "postgresql://user:password@localhost/healthcare_rag"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    try:
        logger.info("[Database] Initializing database...")

        # Ensure data directory exists
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)

        # Create tables
        Base.metadata.create_all(bind=engine)

        logger.success(f"[Database] Database initialized at {DATABASE_URL}")

        # Verify connection (SQLAlchemy 2.0 requires text() for raw SQL)
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            logger.success("[Database] Connection verified")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[Database] Initialization failed: {e}")
        logger.warning("[Database] Continuing without database (will use in-memory fallback)")


def get_db() -> Session:
    """
    Get database session.

    Usage:
        db = next(get_db())
        try:
            # Use db
        finally:
            db.close()

    Or with FastAPI dependency injection:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session (direct, not generator)"""
    return SessionLocal()
