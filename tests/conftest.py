"""
Pytest configuration and shared fixtures.

This module provides fixtures for database session, test client,
and other shared resources for testing.
"""

import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.core.config import Settings
from src.models import Base
from src.main import app as fastapi_app

# Test database URL (SQLite in-memory for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Override settings for testing."""
    settings = Settings()
    settings.database_url = TEST_DATABASE_URL
    settings.debug = True
    settings.secret_key = "test-secret-key-change-in-production"
    return settings


@pytest.fixture(scope="session")
def engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session, test_settings, monkeypatch):
    """Create a test client with overridden dependencies."""

    # Override get_db dependency to use test session
    from src.api.deps import get_db as original_get_db
    from src.core.database import get_session as original_get_session

    def override_get_db():
        """Provide test database session."""
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by fixture

    def override_get_session():
        """Provide test database session for non-Dependency contexts."""
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[original_get_db] = override_get_db
    fastapi_app.dependency_overrides[original_get_session] = override_get_session

    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Clean up
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "company_name": "Test Corp",
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database."""
    from src.models import User
    from src.api.auth import get_password_hash

    user = User(
        email=test_user_data["email"],
        password_hash=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        company_name=test_user_data["company_name"],
        subscription_tier="free",
        invoice_limit=5,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user_data():
    """Sample admin user data."""
    return {
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "company_name": "Admin Corp",
    }


@pytest.fixture
def admin_user(db_session, admin_user_data):
    """Create an admin user in the database."""
    from src.models import User
    from src.api.auth import get_password_hash

    user = User(
        email=admin_user_data["email"],
        password_hash=get_password_hash(admin_user_data["password"]),
        full_name=admin_user_data["full_name"],
        company_name=admin_user_data["company_name"],
        subscription_tier="enterprise",
        invoice_limit=999,
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
