"""Database configuration and session management for worker."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Database connection string
DATABASE_URL = "postgresql://admin:admin@db/yantra_db"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """
    Context manager for database sessions in worker.
    Automatically commits on success or rolls back on error.

    Usage:
        with get_db_session() as db:
            compiler = db.query(Compiler).filter(...).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
