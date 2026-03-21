"""
Database configuration and session management.

This module sets up the SQLAlchemy engine, session factory,
and provides a dependency for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

from src.core.config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """
    Get a database session.

    Yields:
        Session: SQLAlchemy session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Alias for compatibility with code expecting get_db
get_db = get_session


def init_db():
    """Initialize database tables (for development/testing)."""
    from src.models import Base

    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (for testing cleanup)."""
    from src.models import Base

    Base.metadata.drop_all(bind=engine)
