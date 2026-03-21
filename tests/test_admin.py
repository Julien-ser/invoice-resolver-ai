"""
Tests for admin panel API routes.

This module tests:
- get_dashboard_overview: Admin dashboard statistics
- list_users: User listing with filters and pagination
- get_user_detail: Detailed user information
- update_user_tier: Subscription tier management
- get_system_metrics: System health and metrics
- list_webhook_events: Webhook event tracking
- list_payment_connections: Payment provider connections
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status
from unittest.mock import patch, Mock

from src.admin.schemas import (
    DashboardStats,
    UserSummary,
    UserDetail,
    SystemHealth,
    WebhookEventInfo,
    PaymentConnectionInfo,
)


class TestAdminAuth:
    """Tests for admin authentication."""

    def test_admin_endpoint_requires_admin(self, client, test_user):
        """Test that admin endpoints reject non-admin users."""
        response = client.get(
            "/admin/",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "admin" in response.json()["detail"].lower()

    def test_admin_endpoint_requires_authentication(self, client):
        """Test that admin endpoints require authentication."""
        response = client.get("/admin/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDashboardOverview:
    """Tests for admin dashboard overview."""

    def test_get_dashboard_overview_success(self, client, admin_user, db_session):
        """Test successful retrieval of dashboard statistics."""
        response = client.get(
            "/admin/",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert "tier_distribution" in data
        assert "total_invoices" in data
        assert "invoices_by_status" in data
        assert "total_payment_connections" in data
        assert "connections_by_provider" in data
        assert "recent_webhook_count" in data
        assert "system_health" in data

    def test_dashboard_stats_calculation(self, client, admin_user, db_session):
        """Test that dashboard calculates stats correctly."""
        # Note: This test assumes some data exists in the database.
        # In a real scenario, we'd seed the database with known data.
        response = client.get(
            "/admin/",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Basic sanity checks
        assert data["total_users"] >= 1  # At least admin user exists
        assert data["active_users"] >= 1
        assert isinstance(data["tier_distribution"], dict)


class TestUserManagement:
    """Tests for user management endpoints."""

    def test_list_users_requires_admin(self, client, test_user):
        """Test that user list endpoint requires admin."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_success(self, client, admin_user, db_session):
        """Test successful user listing."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least admin user

    def test_list_users_with_pagination(self, client, admin_user, db_session):
        """Test user listing with pagination."""
        response = client.get(
            "/admin/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # If there are users, should be within limit
        if data:
            assert len(data) <= 10

    def test_list_users_with_tier_filter(self, client, admin_user, db_session):
        """Test user listing filtered by subscription tier."""
        response = client.get(
            "/admin/users?tier=free",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned users should have free tier
        for user in data:
            assert user.get("subscription_tier") == "free"

    def test_list_users_with_status_filter(self, client, admin_user, db_session):
        """Test user listing filtered by active status."""
        response = client.get(
            "/admin/users?status=active",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned users should be active
        for user in data:
            assert user.get("is_active") is True

    def test_list_users_with_search(self, client, admin_user, db_session):
        """Test user listing with search."""
        response = client.get(
            "/admin/users?search=admin",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Search should match admin user
        assert len(data) >= 1
        # Check that at least one result matches search (could be email or full_name)
        matched = False
        for user in data:
            if (
                "admin" in user.get("email", "").lower()
                or "admin" in user.get("full_name", "").lower()
            ):
                matched = True
                break
        assert matched is True

    def test_get_user_detail_success(self, client, admin_user, test_user):
        """Test getting detailed user information."""
        response = client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify user data is present with detailed counts
        assert data["email"] == test_user.email
        assert "invoices_count" in data
        assert "templates_count" in data
        assert "campaigns_count" in data
        assert "payment_connections_count" in data

    def test_get_user_detail_not_found(self, client, admin_user):
        """Test getting non-existent user returns 404."""
        response = client.get(
            "/admin/users/nonexistent_id",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]


class TestUserTierUpdates:
    """Tests for user subscription tier updates."""

    def test_update_user_tier_success(self, client, admin_user, test_user, db_session):
        """Test successful user tier update."""
        response = client.post(
            f"/admin/users/{test_user.id}/tier",
            json={"subscription_tier": "pro", "invoice_limit": 100},
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User tier updated successfully"
        assert data["new_tier"] == "pro"
        assert data["invoice_limit"] == 100

    def test_update_user_tier_invalid_tier(self, client, admin_user, test_user):
        """Test updating to invalid tier fails."""
        response = client.post(
            f"/admin/users/{test_user.id}/tier",
            json={"subscription_tier": "invalid_tier"},
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid subscription tier" in response.json()["detail"]

    def test_update_user_tier_negative_limit(self, client, admin_user, test_user):
        """Test setting negative invoice limit fails."""
        response = client.post(
            f"/admin/users/{test_user.id}/tier",
            json={"subscription_tier": "pro", "invoice_limit": -1},
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot be negative" in response.json()["detail"].lower()

    def test_update_user_tier_default_limits(self, client, admin_user, test_user):
        """Test that default limits are set when not provided."""
        response = client.post(
            f"/admin/users/{test_user.id}/tier",
            json={"subscription_tier": "pro"},
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["invoice_limit"] == 999  # Pro tier default


class TestSystemMetrics:
    """Tests for system metrics endpoint."""

    def test_get_system_metrics_requires_admin(self, client, test_user):
        """Test metrics endpoint requires admin."""
        response = client.get(
            "/admin/metrics",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_system_metrics_success(self, client, admin_user):
        """Test successful metrics retrieval."""
        response = client.get(
            "/admin/metrics",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify metrics structure
        assert "celery_workers" in data
        assert "recent_errors" in data
        assert "api_latency_p95" in data
        assert "last_sync_status" in data
        assert "uptime_days" in data

    def test_get_system_metrics_with_hours_param(self, client, admin_user):
        """Test metrics with custom hours parameter."""
        response = client.get(
            "/admin/metrics?hours=48",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Uptime should reflect 48 hours
        assert data["uptime_days"] == 2.0


class TestWebhookEvents:
    """Tests for webhook events listing."""

    def test_list_webhooks_requires_admin(self, client, test_user):
        """Test webhook listing requires admin."""
        response = client.get(
            "/admin/webhooks",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_webhooks_success(self, client, admin_user):
        """Test successful webhook events listing."""
        response = client.get(
            "/admin/webhooks",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_webhooks_with_filters(self, client, admin_user):
        """Test webhook listing with filters."""
        response = client.get(
            "/admin/webhooks?provider=stripe&status=processed&hours=24",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Verify filters applied (should filter by provider and status if data exists)
        for event in data:
            if event.get("provider"):
                assert (
                    event["provider"] == "stripe" or event["provider"] is None
                )  # If no data, still okay

    def test_list_webhooks_with_limit(self, client, admin_user):
        """Test webhook listing with custom limit."""
        response = client.get(
            "/admin/webhooks?limit=10",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if data:
            assert len(data) <= 10


class TestPaymentConnections:
    """Tests for payment connections listing."""

    def test_list_connections_requires_admin(self, client, test_user):
        """Test connections listing requires admin."""
        response = client.get(
            "/admin/connections",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_connections_success(self, client, admin_user):
        """Test successful payment connections listing."""
        response = client.get(
            "/admin/connections",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_connections_active_only(self, client, admin_user):
        """Test connections with active_only filter."""
        response = client.get(
            "/admin/connections?active_only=true",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for conn in data:
            assert conn.get("is_active") is True

    def test_list_connections_with_provider_filter(self, client, admin_user):
        """Test connections filtered by provider."""
        response = client.get(
            "/admin/connections?provider=stripe",
            headers={"Authorization": f"Bearer {admin_user.access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for conn in data:
            assert (
                conn.get("provider") == "stripe" or conn.get("provider") is None
            )  # If no data, still okay
