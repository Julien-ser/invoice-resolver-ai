"""
Stripe Billing integration for subscription management.

This module handles:
- Creating checkout sessions for subscription plans
- Processing Stripe webhook events for subscription lifecycle
- Synchronizing user subscription tiers with Stripe
"""

import os
import stripe
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from src.core.config import settings
from src.models import User
from src.billing.schemas import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionStatus,
    StripePrice,
    SubscriptionUpdateWebhook,
)

# Stripe API configuration
stripe.api_key = settings.stripe_api_key


# Plan definitions - these map to Stripe Price IDs
# Prices should be created in Stripe Dashboard and their IDs set in environment variables
PLANS = {
    "free": StripePrice(
        price_id=os.getenv("STRIPE_PRICE_FREE", "price_free_placeholder"),
        name="Free",
        description="5 invoices per month",
        price_monthly=0,
        currency="usd",
        features=["5 invoices/month", "Basic email support", "Single currency"],
        invoice_limit=5,
        includes_legal_pack=False,
        includes_multi_currency=False,
    ),
    "pro": StripePrice(
        price_id=os.getenv("STRIPE_PRICE_PRO", "price_pro_placeholder"),
        name="Pro",
        description="Unlimited invoices + AI dispute drafting",
        price_monthly=1900,  # $19.00 in cents
        currency="usd",
        features=[
            "Unlimited invoices",
            "AI dispute letter drafting",
            "A/B testing",
            "Email automation",
            "Priority support",
        ],
        invoice_limit=-1,  # Unlimited
        includes_legal_pack=False,
        includes_multi_currency=False,
    ),
    "legal_pack": StripePrice(
        price_id=os.getenv("STRIPE_PRICE_LEGAL_PACK", "price_legal_placeholder"),
        name="Legal Pack",
        description="Additional legal template pack",
        price_monthly=500,  # $5.00 in cents
        currency="usd",
        features=[
            "Premium legal templates",
            "Small claims forms",
            "Court filing guides",
            "Custom dispute letters",
        ],
        invoice_limit=0,  # Add-on, doesn't affect invoice limit
        includes_legal_pack=True,
        includes_multi_currency=False,
    ),
    "multi_currency": StripePrice(
        price_id=os.getenv("STRIPE_PRICE_MULTI_CURRENCY", "price_mc_placeholder"),
        name="Multi-Currency",
        description="Support for multiple currencies",
        price_monthly=300,  # $3.00 in cents
        currency="usd",
        features=[
            "Multiple currency invoices",
            "Auto currency conversion",
            "Exchange rate tracking",
            "Multi-currency reporting",
        ],
        invoice_limit=0,  # Add-on, doesn't affect invoice limit
        includes_legal_pack=False,
        includes_multi_currency=True,
    ),
}


def get_plan_by_price_id(price_id: str) -> Optional[StripePrice]:
    """Get plan details by Stripe Price ID."""
    for plan in PLANS.values():
        if plan.price_id == price_id:
            return plan
    return None


def get_plan_by_tier(tier: str) -> Optional[StripePrice]:
    """Get plan details by subscription tier."""
    return PLANS.get(tier)


def create_checkout_session(
    user: User,
    plan_id: str,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout session for a user to subscribe to a plan.

    Args:
        user: The user creating the checkout session
        plan_id: Stripe Price ID for the plan
        success_url: URL to redirect after successful checkout
        cancel_url: URL to redirect if checkout cancelled

    Returns:
        CheckoutSessionResponse with session ID and URL

    Raises:
        Exception: If Stripe API call fails
        ValueError: If plan_id is invalid
    """
    plan = get_plan_by_price_id(plan_id)
    if not plan:
        raise ValueError(f"Invalid plan ID: {plan_id}")

    # Ensure we have a Stripe customer ID for this user
    customer_id = _get_or_create_customer(user)

    # Build success and cancel URLs
    if not success_url:
        success_url = f"{settings.api_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    if not cancel_url:
        cancel_url = f"{settings.api_base_url}/billing/cancel"

    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        billing_address_collection="required",
        line_items=[
            {
                "price": plan_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user.id,
            "plan_name": plan.name,
            "invoice_limit": str(plan.invoice_limit),
        },
        allow_promotion_codes=True,
    )

    return CheckoutSessionResponse(
        session_id=checkout_session.id,
        url=checkout_session.url or "",
    )


def _get_or_create_customer(user: User) -> str:
    """
    Get existing Stripe customer ID or create a new one.

    Args:
        user: User model instance

    Returns:
        Stripe Customer ID

    Note:
        Stores the customer_id in user's extra_data if available.
        You may want to add a dedicated stripe_customer_id column to User model.
    """
    # Check if user already has a Stripe customer ID stored
    # For now, we'll check extra_data, but consider adding a dedicated column
    customer_id = None
    if hasattr(user, "extra_data") and user.extra_data:
        customer_id = user.extra_data.get("stripe_customer_id")

    if customer_id:
        try:
            # Verify customer exists
            customer = stripe.Customer.retrieve(customer_id)
            return customer.id
        except Exception:
            # Customer doesn't exist, create a new one
            pass

    # Create new customer
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name or user.company_name or user.email,
        metadata={
            "user_id": user.id,
        },
    )

    # Store customer ID in user's extra_data
    if not hasattr(user, "extra_data") or user.extra_data is None:
        user.extra_data = {}
    user.extra_data["stripe_customer_id"] = customer.id

    return customer.id


def handle_webhook_event(db: Session, payload: bytes, signature: str) -> str:
    """
    Verify and process a Stripe webhook event.

    Args:
        db: SQLAlchemy database session
        payload: Raw webhook payload (bytes)
        signature: Stripe-Signature header value

    Returns:
        Event ID that was processed

    Raises:
        ValueError: If signature verification fails or event processing fails
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )
    except Exception as e:
        # Handle signature verification errors and other construct issues
        raise ValueError(f"Webhook verification failed: {e}") from e

    event_id = event.get("id")
    if not event_id:
        raise ValueError("Event ID missing from webhook payload")

    event_type = event.get("type")

    # Process based on event type
    if event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        _handle_subscription_updated(db, subscription)
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        _handle_subscription_deleted(db, subscription)
    elif event_type == "checkout.session.completed":
        session = event["data"]["object"]
        _handle_checkout_session_completed(session)

    return event_id


def _handle_subscription_updated(db: Session, subscription: Dict[str, Any]) -> None:
    """
    Handle subscription update event from Stripe.

    Updates the user's subscription tier based on the subscription's price.

    Args:
        db: SQLAlchemy database session
        subscription: Stripe subscription object
    """
    try:
        # Get user_id from metadata
        user_id = subscription.get("metadata", {}).get("user_id")
        if not user_id:
            return  # Cannot associate with a user

        # Get the price ID from subscription items
        items = subscription.get("items", {}).get("data", [])
        if not items:
            return

        price_id = items[0].get("price", {}).get("id")
        if not price_id:
            return

        # Find the plan matching this price
        plan = get_plan_by_price_id(price_id)
        if not plan:
            return  # Unknown price, skip

        # Determine the subscription tier
        # For add-ons, we need to check what the base subscription is
        # For simplicity, we'll map directly: pro->pro, legal_pack->pro (add-on), multi_currency->pro (add-on)
        # In a real implementation, you'd handle add-ons differently (separate subscription items)

        tier = (
            "pro"
            if plan.name.lower() in ["pro", "legal_pack", "multi_currency"]
            else plan.name.lower()
        )

        # Update user in database
        SubscriptionUpdater.update_user_tier(db, user_id, tier, subscription)

    except Exception as e:
        # Log error but don't fail webhook (already processed by Stripe)
        import sys

        print(f"Error handling subscription update: {e}", file=sys.stderr)


def _handle_subscription_deleted(db: Session, subscription: Dict[str, Any]) -> None:
    """
    Handle subscription deletion/cancellation.

    Args:
        db: SQLAlchemy database session
        subscription: Stripe subscription object
    """
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return

    # Downgrade user to free tier
    SubscriptionUpdater.downgrade_to_free(db, user_id)


def _handle_checkout_session_completed(session: Dict[str, Any]) -> None:
    """
    Handle checkout session completion.

    Args:
        session: Stripe Checkout Session object
    """
    # The subscription will be updated via customer.subscription.updated
    # This is just for logging/analytics if needed
    user_id = session.get("metadata", {}).get("user_id")
    if user_id:
        # Could create an audit log or send welcome email
        pass


class SubscriptionUpdater:
    """Helper class for updating subscription status in database."""

    @staticmethod
    def update_user_tier(
        db: Session, user_id: str, tier: str, subscription: Dict[str, Any]
    ) -> None:
        """
        Update user's subscription tier in database.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            tier: New subscription tier (free, pro, enterprise)
            subscription: Full Stripe subscription object
        """
        from src.models import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # Update subscription tier
        user.subscription_tier = tier

        # Update invoice limit based on tier
        plan = get_plan_by_tier(tier)
        if plan:
            user.invoice_limit = plan.invoice_limit

        # Store Stripe customer ID in extra_data if not already present
        customer_id = subscription.get("customer")
        if customer_id:
            if not hasattr(user, "extra_data") or user.extra_data is None:
                user.extra_data = {}
            user.extra_data["stripe_customer_id"] = customer_id

        db.commit()

    @staticmethod
    def downgrade_to_free(db: Session, user_id: str) -> None:
        """
        Downgrade user to free tier.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
        """
        from src.models import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        user.subscription_tier = "free"
        user.invoice_limit = 5  # Free tier limit

        # Note: We don't remove stripe_customer_id from extra_data
        # because it's useful for future re-subscriptions

        db.commit()


def get_subscription_info(user: User) -> Optional[SubscriptionStatus]:
    """
    Get current subscription information for a user.

    Args:
        user: User model instance

    Returns:
        SubscriptionStatus with current subscription details or None if no subscription
    """
    # Get customer ID
    customer_id = None
    if hasattr(user, "extra_data") and user.extra_data:
        customer_id = user.extra_data.get("stripe_customer_id")

    if not customer_id:
        return None

    try:
        # Retrieve customer's subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1,
        )

        if not subscriptions.data:
            return None

        subscription = subscriptions.data[0]

        # Get the price - use attribute access for Stripe objects
        # subscription.items is a ListObject with .data attribute containing list
        items_data = getattr(subscription.items, "data", subscription.items)
        if not items_data:
            return None

        # First item's price
        price = items_data[0].price
        plan = get_plan_by_price_id(price.id)

        if not plan:
            return None

        # Stripe returns current_period_end as a Unix timestamp (int)
        current_period_end = datetime.fromtimestamp(subscription.current_period_end)  # type: ignore

        return SubscriptionStatus(
            tier=user.subscription_tier,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription.id,
            current_period_end=current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            status=subscription.status,
            plan=plan,
        )
    except Exception:
        return None


def calculate_invoice_limit(tier: str) -> int:
    """
    Calculate the invoice limit for a given subscription tier.

    Args:
        tier: Subscription tier (free, pro, enterprise)

    Returns:
        Monthly invoice limit (-1 for unlimited)
    """
    plan = get_plan_by_tier(tier)
    if plan:
        return plan.invoice_limit
    return 5  # Default to free tier
