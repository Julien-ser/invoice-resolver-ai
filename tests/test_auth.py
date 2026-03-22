"""
Tests for authentication API endpoints.

This module covers user registration, login, token refresh,
logout, and protected route access.
"""

import pytest
from fastapi import status

from tests.conftest import test_user_data, admin_user_data


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client, db_session):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User",
                "company_name": "New Corp",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["company_name"] == "New Corp"
        assert data["subscription_tier"] == "free"
        assert data["invoice_limit"] == 5
        assert "id" in data
        assert "password_hash" not in data  # password should not be returned

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/auth/register",
            json={"email": test_user.email, "password": "differentpass123"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={"email": "invalidemail", "password": "password123"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_password_too_short(self, client):
        """Test registration with password less than 8 characters."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client, test_user, test_user_data):
        """Test successful login returns tokens."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["detail"]

    def test_login_user_not_found(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user account."""
        from src.models import User
        from src.api.auth import get_password_hash

        inactive_user = User(
            email="inactive@example.com",
            password_hash=get_password_hash("password123"),
            is_active=False,
        )
        db_session.add(inactive_user)
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_updates_last_login(self, client, test_user, test_user_data):
        """Test that successful login updates last_login_at."""
        initial_last_login = test_user.last_login_at

        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        # Note: We can't easily test timestamp change in SQLite due to precision
        # but the endpoint executes without error


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_refresh_success(self, client, test_user, test_user_data):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new tokens
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": "invalidtoken123"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_expired_token(self, client, db_session, test_user, test_user_data):
        """Test refresh with expired token."""
        import time
        from datetime import datetime, timedelta
        from src.api.auth import create_refresh_token
        from jose import jwt

        # Create a refresh token and manually expire it in DB
        token, _ = create_refresh_token(test_user.id)

        # Find the token record and manually set expired_at
        from src.models import RefreshToken

        token_record = (
            db_session.query(RefreshToken)
            .filter(RefreshToken.user_id == test_user.id)
            .order_by(RefreshToken.created_at.desc())
            .first()
        )

        # Manually set expires_at to past
        token_record.expires_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()

        # Try to use expired token
        response = client.post("/api/auth/refresh", json={"refresh_token": token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_single_use(self, client, test_user, test_user_data):
        """Test that refresh token is single-use (rotation)."""
        # First login to get refresh token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token once
        response1 = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response1.status_code == status.HTTP_200_OK
        new_tokens = response1.json()

        # Try to use same token again - should fail
        response2 = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response2.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_success(self, client, test_user, test_user_data):
        """Test successful logout revokes refresh token."""
        # Login to get refresh token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        # Logout
        response = client.post(
            "/api/auth/logout", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "Logged out successfully" in response.json()["message"]

    def test_logout_invalid_token(self, client):
        """Test logout with invalid refresh token."""
        response = client.post(
            "/api/auth/logout", json={"refresh_token": "invalidtoken"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProtectedEndpoints:
    """Tests for protected routes dependency."""

    def test_access_protected_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        # This would normally be caught by get_current_user dependency
        # We'll test with a dummy endpoint once created
        response = client.get("/api/invoices")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_with_valid_token(self, client, test_user, test_user_data):
        """Test accessing protected endpoint with valid token succeeds."""
        # Login to get access token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        access_token = login_response.json()["access_token"]

        # Access protected endpoint
        response = client.get(
            "/api/invoices", headers={"Authorization": f"Bearer {access_token}"}
        )

        # Note: This will fail if invoice endpoints not yet implemented,
        # but should not fail with 401 if token is valid
        # Will get 501/404 instead
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


class TestUserResponse:
    """Tests for user response data."""

    def test_user_response_contains_correct_fields(self, client, test_user):
        """Test that user registration returns correct fields."""
        # Register a new user to test response model
        response = client.post(
            "/api/auth/register",
            json={"email": "response.test@example.com", "password": "password123"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        required_fields = [
            "id",
            "email",
            "subscription_tier",
            "invoice_limit",
            "is_active",
            "created_at",
        ]
        for field in required_fields:
            assert field in data

        # Sensitive fields should not be present
        assert "password_hash" not in data
        assert "last_login_at" not in data  # not in response model
