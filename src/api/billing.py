"""
FastAPI routes for billing management.

Provides endpoints for:
- Creating checkout sessions
- Handling Stripe webhooks
- Viewing subscription status
- Listing available plans
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.config import settings
from src.models import User
from src.api.deps import get_current_user
from src.billing import (
    create_checkout_session,
    handle_webhook_event,
    get_subscription_info,
    calculate_invoice_limit,
    PLANS,
    StripePrice,
)
from src.billing.schemas import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionStatus,
)


router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=List[StripePrice])
async def list_plans() -> List[StripePrice]:
    """
    List all available subscription plans.

    Returns:
        List of StripePrice objects with plan details
    """
    return list(PLANS.values())


@router.get("/subscription", response_model=SubscriptionStatus)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
) -> SubscriptionStatus:
    """
    Get current user's subscription status.

    Returns:
        SubscriptionStatus with subscription details or null if no subscription
    """
    subscription = get_subscription_info(current_user)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
        )
    return subscription


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout session for the current user.

    Args:
        request: CheckoutSessionRequest with plan_id and optional URLs

    Returns:
        CheckoutSessionResponse with session ID and checkout URL
    """
    try:
        response = create_checkout_session(
            user=current_user,
            plan_id=request.plan_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Handle Stripe webhook events.

    This endpoint receives webhooks from Stripe for subscription lifecycle events.
    It verifies the signature and updates user subscription tiers accordingly.

    Returns:
        dict with status information
    """
    # Get the raw body and signature header
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )

    try:
        event_id = handle_webhook_event(db, payload, signature)
        return {"status": "success", "event_id": event_id}
    except ValueError as e:
        # Signature verification failed or invalid payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.get("/invoice-limit")
async def get_invoice_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get current user's invoice limit based on subscription tier.

    Returns:
        dict with tier, limit, and usage information
    """
    limit = calculate_invoice_limit(current_user.subscription_tier)

    # Count current invoices (not deleted)
    from src.models import Invoice

    invoice_count = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.deleted_at.is_(None))
        .count()
    )

    return {
        "tier": current_user.subscription_tier,
        "limit": limit,
        "used": invoice_count,
        "remaining": limit - invoice_count if limit > 0 else -1,  # -1 = unlimited
    }
