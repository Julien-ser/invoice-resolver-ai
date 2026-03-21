"""
Pydantic schemas for admin panel requests/responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserSummary(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    subscription_tier: str
    invoice_limit: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetail(UserSummary):
    last_login_at: Optional[datetime] = None
    email_notifications_enabled: bool
    payment_connections_count: int
    invoices_count: int
    templates_count: int
    campaigns_count: int

    class Config:
        from_attributes = True


class UserTierUpdate(BaseModel):
    subscription_tier: str = Field(
        ..., description="Subscription tier: free, pro, or enterprise"
    )
    invoice_limit: Optional[int] = Field(
        None, description="Optional custom invoice limit"
    )


# Dashboard/Overview schemas
class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    tier_distribution: Dict[str, int]  # {"free": 10, "pro": 5, "enterprise": 2}
    total_invoices: int
    invoices_by_status: Dict[
        str, int
    ]  # {"pending": 5, "paid": 50, "overdue": 10, "disputed": 2}
    total_payment_connections: int
    connections_by_provider: Dict[str, int]  # {"stripe": 10, "paypal": 5, "plaid": 3}
    recent_webhook_count: int
    system_health: Dict[str, Any]


# System metrics schemas
class SystemHealth(BaseModel):
    celery_workers: Dict[str, Any]  # {"active": 2, "total": 2, "details": [...]}
    recent_errors: List[Dict[str, Any]]
    api_latency_p95: Optional[float] = None
    last_sync_status: Optional[Dict[str, Any]] = None
    uptime_days: float


# Payment connection schemas
class PaymentConnectionInfo(BaseModel):
    id: str
    user_email: str
    provider: str
    connection_name: Optional[str]
    is_active: bool
    last_sync_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Webhook event schemas
class WebhookEventInfo(BaseModel):
    id: str
    provider: str
    event_type: str
    processing_status: str
    processing_error: Optional[str]
    signature_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
