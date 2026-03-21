"""
Tests for middleware components.

This module tests:
- SubscriptionLimitCheckerMiddleware: Enforces invoice limits for freemium users
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route
from fastapi import Request, HTTPException, status as fastapi_status
from sqlalchemy.orm import Session

from src.middleware import SubscriptionLimitCheckerMiddleware
from src.models import User, Invoice
from src.core.database import get_session


@pytest.fixture
def mock_app():
    """Create a mock ASGI app."""
    app = Mock(spec=ASGIApp)
    return app


@pytest.fixture
def middleware(mock_app):
    """Create middleware instance."""
    return SubscriptionLimitCheckerMiddleware(mock_app)


class TestSubscriptionLimitCheckerMiddleware:
    """Tests for SubscriptionLimitCheckerMiddleware."""

    def test_middleware_initialization(self, mock_app):
        """Test middleware initialization."""
        middleware = SubscriptionLimitCheckerMiddleware(mock_app)
        assert middleware.app == mock_app

    @pytest.mark.asyncio
    async def test_dispatch_non_invoice_endpoint(self, middleware, db_session):
        """Test that non-invoice endpoints bypass the check."""
        # Create a mock request to a non-invoice endpoint
        request = Mock(spec=Request)
        request.url.path = "/api/auth/login"
        request.method = "POST"

        # Mock call_next to return a response
        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        # Should skip check and call next
        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_get_request(self, middleware, db_session):
        """Test that GET requests bypass the check."""
        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "GET"

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_delete_request(self, middleware, db_session):
        """Test that DELETE requests bypass the check."""
        request = Mock(spec=Request)
        request.url.path = "/api/invoices/inv_123"
        request.method = "DELETE"

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_no_user_in_request_state(self, middleware, db_session):
        """Test that request without user proceeds without check."""
        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        # No user attribute
        delattr(request, "user") if hasattr(request, "user") else None

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_admin_user_bypasses_limit_check(
        self, middleware, db_session, admin_user
    ):
        """Test that admin users bypass invoice limit check."""
        # Create mock request with admin user
        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = admin_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_pro_user_bypasses_limit_check(
        self, middleware, db_session, test_user
    ):
        """Test that pro (non-free) users bypass invoice limit check."""
        # Modify test_user to be pro
        test_user.subscription_tier = "pro"
        db_session.commit()
        db_session.refresh(test_user)

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_free_user_under_limit_allowed(
        self, middleware, db_session, test_user
    ):
        """Test that free user under invoice limit is allowed."""
        # Ensure test_user is free with generous limit
        test_user.subscription_tier = "free"
        test_user.invoice_limit = 10
        db_session.commit()
        db_session.refresh(test_user)

        # Create only 1 active invoice for user
        invoice = Invoice(
            user_id=test_user.id,
            invoice_number="INV-001",
            client_name="Test",
            client_email="test@example.com",
            amount=100.00,
            currency="USD",
            due_date=datetime.utcnow() + timedelta(days=30),
            status="sent",
        )
        db_session.add(invoice)
        db_session.commit()

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_free_user_exceeds_limit_denied(
        self, middleware, db_session, test_user
    ):
        """Test that free user exceeding invoice limit is denied."""
        # Set user to free with limit of 2
        test_user.subscription_tier = "free"
        test_user.invoice_limit = 2
        db_session.commit()
        db_session.refresh(test_user)

        # Create 2 active invoices (at limit)
        for i in range(2):
            invoice = Invoice(
                user_id=test_user.id,
                invoice_number=f"INV-{i:03d}",
                client_name="Test",
                client_email="test@example.com",
                amount=100.00,
                currency="USD",
                due_date=datetime.utcnow() + timedelta(days=30),
                status="sent",
            )
            db_session.add(invoice)
        db_session.commit()

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await middleware.dispatch(request, call_next)

        assert exc_info.value.status_code == fastapi_status.HTTP_403_FORBIDDEN
        assert "limit exceeded" in exc_info.value.detail.lower()
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_limit_check_counts_only_active_invoices(
        self, middleware, db_session, test_user
    ):
        """Test that only non-paid/canceled invoices count toward limit."""
        test_user.subscription_tier = "free"
        test_user.invoice_limit = 2
        db_session.commit()
        db_session.refresh(test_user)

        # Create 1 active invoice
        active_invoice = Invoice(
            user_id=test_user.id,
            invoice_number="INV-ACTIVE",
            client_name="Test",
            client_email="test@example.com",
            amount=100.00,
            currency="USD",
            due_date=datetime.utcnow() + timedelta(days=30),
            status="sent",
        )
        db_session.add(active_invoice)

        # Create 2 paid invoices (should not count)
        for i in range(2):
            paid_invoice = Invoice(
                user_id=test_user.id,
                invoice_number=f"INV-PAID-{i}",
                client_name="Test",
                client_email="test@example.com",
                amount=100.00,
                currency="USD",
                due_date=datetime.utcnow() - timedelta(days=30),
                status="paid",
            )
            db_session.add(paid_invoice)
        db_session.commit()

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        # Should be allowed because only 1 active invoice (limit is 2)
        response = await middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_database_session_closed(self, middleware, db_session, test_user):
        """Test that database session is properly closed after check."""
        test_user.subscription_tier = "free"
        test_user.invoice_limit = 0  # Force check to run
        db_session.commit()
        db_session.refresh(test_user)

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        mock_response = Mock()
        call_next = AsyncMock(return_value=mock_response)

        with patch("src.middleware.get_session") as mock_get_session:
            mock_session = Mock(spec=Session)
            mock_session.query.return_value.filter.return_value.count.return_value = 0
            mock_get_session.return_value = mock_session

            with pytest.raises(HTTPException):
                await middleware.dispatch(request, call_next)

            # Verify session was closed
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_chain_continues_on_success(
        self, middleware, db_session, test_user
    ):
        """Test that middleware properly chains to next handler."""
        test_user.subscription_tier = "free"
        test_user.invoice_limit = 5
        db_session.commit()
        db_session.refresh(test_user)

        request = Mock(spec=Request)
        request.url.path = "/api/invoices/"
        request.method = "POST"
        request.state.user = test_user

        expected_response = Mock(status_code=201, json=lambda: {"id": "123"})
        call_next = AsyncMock(return_value=expected_response)

        response = await middleware.dispatch(request, call_next)

        assert response == expected_response
        call_next.assert_called_once_with(request)


class TestMiddlewareIntegration:
    """Integration tests for middleware with FastAPI app."""

    def test_middleware_added_to_app(self):
        """Test that middleware is properly configured in main app."""
        from src.main import app

        # Check that middleware is present
        middleware_found = False
        for middleware in app.user_middleware:
            if middleware.cls == SubscriptionLimitCheckerMiddleware:
                middleware_found = True
                break

        assert middleware_found is True, (
            "SubscriptionLimitCheckerMiddleware should be added to app"
        )

    def test_middleware_only_applies_to_invoice_endpoints(self):
        """Test that middleware only affects invoice endpoints."""
        from src.main import app

        # This is more of a configuration verification
        # Actual behavior tested in unit tests above
        middleware_found = False
        for middleware in app.user_middleware:
            if middleware.cls == SubscriptionLimitCheckerMiddleware:
                middleware_found = True
                break

        assert middleware_found is True
