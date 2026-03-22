"""
Pydantic schemas for billing module.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StripePrice(BaseModel):
    """Stripe price/plan information."""

    model_config = ConfigDict(from_attributes=True)

    price_id: str = Field(..., description="Stripe Price ID")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    price_monthly: int = Field(..., description="Monthly price in cents")
    currency: str = Field(default="usd", description="Currency code")
    features: list[str] = Field(default_factory=list, description="Plan features")
    invoice_limit: int = Field(..., description="Monthly invoice allowance")
    includes_legal_pack: bool = Field(
        default=False, description="Includes legal template pack"
    )
    includes_multi_currency: bool = Field(
        default=False, description="Includes multi-currency support"
    )


class CheckoutSessionRequest(BaseModel):
    """Request to create a Stripe checkout session."""

    plan_id: str = Field(..., description="Stripe Price ID to subscribe to")
    success_url: Optional[str] = Field(
        None, description="URL to redirect after successful checkout"
    )
    cancel_url: Optional[str] = Field(
        None, description="URL to redirect if checkout cancelled"
    )


class CheckoutSessionResponse(BaseModel):
    """Response containing checkout session details."""

    session_id: str = Field(..., description="Stripe Checkout Session ID")
    url: str = Field(..., description="Checkout URL to redirect user to")


class SubscriptionStatus(BaseModel):
    """User's current subscription status."""

    model_config = ConfigDict(from_attributes=True)

    tier: str = Field(..., description="Subscription tier: free, pro, enterprise")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe Customer ID")
    stripe_subscription_id: Optional[str] = Field(
        None, description="Stripe Subscription ID"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="When current subscription ends"
    )
    cancel_at_period_end: bool = Field(
        default=False, description="Whether subscription cancels at period end"
    )
    status: Optional[str] = Field(None, description="Stripe subscription status")
    plan: Optional[StripePrice] = Field(None, description="Current plan details")


class SubscriptionUpdateWebhook(BaseModel):
    """Stripe subscription update webhook payload."""

    id: str = Field(..., description="Subscription ID")
    object: str = Field(..., description="Object type, should be 'subscription'")
    status: str = Field(
        ..., description="Subscription status: active, past_due, canceled, etc."
    )
    current_period_end: int = Field(..., description="Unix timestamp of period end")
    cancel_at_period_end: bool = Field(
        ..., description="Whether it will cancel at period end"
    )
    customer: str = Field(..., description="Stripe Customer ID")
    items: dict = Field(..., description="Subscription items containing price info")
    metadata: Optional[dict] = Field(
        default_factory=dict, description="Optional metadata"
    )
