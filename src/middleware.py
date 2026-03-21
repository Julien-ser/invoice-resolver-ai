"""
Subscription limit enforcement middleware.

This middleware checks if a user has exceeded their invoice limit
before allowing access to invoice creation/management endpoints.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from sqlalchemy.orm import Session

from src.core.database import get_session
from src.models import Invoice


class SubscriptionLimitCheckerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce subscription invoice limits.

    Checks that freemium users don't exceed their invoice limit
    when creating or managing invoices.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and check subscription limits if needed.

        Only applies to invoice creation/update operations for non-admin users.
        """
        # Skip check for non-protected endpoints
        if not request.url.path.startswith(("/api/invoices",)):
            return await call_next(request)

        # Skip check for safe methods (GET, OPTIONS, HEAD)
        if request.method in ("GET", "OPTIONS", "HEAD"):
            return await call_next(request)

        # Skip check for non-invoice modification endpoints
        # Only check POST (create) and potentially PATCH (status updates that count)
        if request.method == "DELETE":
            return await call_next(request)

        # Get current user from request state (set by auth dependency)
        user = getattr(request.state, "user", None)
        if user is None:
            # Should be caught by auth middleware, but proceed if not set
            return await call_next(request)

        # Skip check for admin users
        if user.is_admin:
            return await call_next(request)

        # Check invoice limit for free tier users
        if user.subscription_tier == "free":
            db = next(get_session())
            try:
                # Count active/in-progress invoices (not paid or canceled)
                active_invoices = (
                    db.query(Invoice)
                    .filter(
                        Invoice.user_id == user.id,
                        Invoice.status.notin_(["paid", "canceled"]),
                    )
                    .count()
                )

                if active_invoices >= user.invoice_limit:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=(
                            f"Invoice limit exceeded. "
                            f"Current: {active_invoices}, Limit: {user.invoice_limit}. "
                            f"Upgrade to Pro for unlimited invoices."
                        ),
                    )
            finally:
                db.close()

        response = await call_next(request)
        return response
