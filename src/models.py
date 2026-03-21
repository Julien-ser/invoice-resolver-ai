"""
SQLAlchemy models for Invoice Resolver AI.

This module contains all database models mapped to the PostgreSQL schema.
All models use UUID as primary key and include timestamp tracking.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Numeric,
    Text,
    DateTime,
    Date,
    JSON,
    ForeignKey,
    UniqueConstraint,
    Index,
    CheckConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def generate_uuid():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class TimestampMixin:
    """Mixin for models with created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    """User account with subscription tier and invoice limits."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    subscription_tier: Mapped[str] = mapped_column(
        String(50), nullable=False, default="free", server_default="free"
    )
    invoice_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    payment_connections: Mapped[List["PaymentConnection"]] = relationship(
        "PaymentConnection", back_populates="user", cascade="all, delete-orphan"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="user", cascade="all, delete-orphan"
    )
    templates: Mapped[List["Template"]] = relationship(
        "Template", back_populates="user", cascade="all, delete-orphan"
    )
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign", back_populates="user", cascade="all, delete-orphan"
    )
    ab_tests: Mapped[List["ABTest"]] = relationship(
        "ABTest", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_subscription_tier", "subscription_tier"),
        Index("idx_users_created_at", "created_at"),
        CheckConstraint(
            "subscription_tier IN ('free', 'pro', 'enterprise')",
            name="users_subscription_tier_check",
        ),
    )


class PaymentConnection(Base, TimestampMixin):
    """Encrypted payment provider credentials and sync status."""

    __tablename__ = "payment_connections"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    connection_name: Mapped[Optional[str]] = mapped_column(String(255))
    credentials_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    external_account_id: Mapped[Optional[str]] = mapped_column(String(500))
    external_user_id: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payment_connections")

    __table_args__ = (
        Index("idx_payment_connections_user_id", "user_id"),
        Index("idx_payment_connections_provider", "provider"),
        Index("idx_payment_connections_is_active", "is_active"),
        Index(
            "uniq_user_provider_active",
            "user_id",
            "provider",
            unique=True,
            postgresql_where=(is_active == True),
        ),
        CheckConstraint(
            "provider IN ('stripe', 'paypal', 'plaid')",
            name="payment_connections_provider_check",
        ),
    )


class Invoice(Base, TimestampMixin):
    """Invoice records with payment status and external provider IDs."""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    invoice_number: Mapped[Optional[str]] = mapped_column(String(255))
    client_name: Mapped[str] = mapped_column(String(500), nullable=False)
    client_email: Mapped[Optional[str]] = mapped_column(String(500))
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", server_default="draft"
    )
    due_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    issue_date: Mapped[datetime] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    paid_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(500))
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(String(500))
    paypal_txn_id: Mapped[Optional[str]] = mapped_column(String(500))
    paypal_invoice_id: Mapped[Optional[str]] = mapped_column(String(500))
    plaid_account_id: Mapped[Optional[str]] = mapped_column(String(500))
    plaid_transaction_id: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="invoices")
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign", back_populates="invoice", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_invoices_user_id", "user_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_due_date", "due_date"),
        Index("idx_invoices_created_at", "created_at"),
        Index(
            "idx_invoices_stripe_payment_intent",
            "stripe_payment_intent_id",
            postgresql_where=(text("stripe_payment_intent_id IS NOT NULL")),
        ),
        Index(
            "idx_invoices_paypal_txn",
            "paypal_txn_id",
            postgresql_where=(text("paypal_txn_id IS NOT NULL")),
        ),
        Index("idx_invoices_metadata", "extra_data", postgresql_using="gin"),
        Index("idx_invoices_user_status", "user_id", "status"),
        Index("idx_invoices_user_due_date", "user_id", "due_date"),
        CheckConstraint(
            "status IN ('draft', 'sent', 'paid', 'overdue', 'disputed', 'canceled')",
            name="invoices_status_check",
        ),
        CheckConstraint("amount > 0", name="invoices_amount_check"),
    )


class Template(Base, TimestampMixin):
    """Email and document templates for follow-ups and disputes."""

    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE")
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(1000), nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="templates")
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign", back_populates="template"
    )

    __table_args__ = (
        Index("idx_templates_user_id", "user_id"),
        Index("idx_templates_type", "type"),
        Index("idx_templates_is_system", "is_system"),
        Index("idx_templates_created_at", "created_at"),
        CheckConstraint(
            "type IN ('follow_up_3_day', 'follow_up_7_day', 'follow_up_14_day', "
            "'dispute_letter', 'small_claims_form', 'custom')",
            name="templates_type_check",
        ),
    )


class Campaign(Base):
    """Email campaign records with tracking metrics."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    template_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("templates.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invoice_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
    )
    ab_test_variant: Mapped[Optional[str]] = mapped_column(String(50))
    scheduled_send_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opened_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paid_after_send: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="campaigns")
    template: Mapped["Template"] = relationship("Template", back_populates="campaigns")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="campaigns")
    email_events: Mapped[List["EmailEvent"]] = relationship(
        "EmailEvent", back_populates="campaign", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_campaigns_user_id", "user_id"),
        Index("idx_campaigns_template_id", "template_id"),
        Index("idx_campaigns_invoice_id", "invoice_id"),
        Index("idx_campaigns_sent_at", "sent_at"),
        Index("idx_campaigns_opened_at", "opened_at"),
        Index("idx_campaigns_ab_test_variant", "ab_test_variant"),
    )


class ABTest(Base, TimestampMixin):
    """A/B test experiments tracking variants and results."""

    __tablename__ = "ab_tests"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)
    variants: Mapped[dict] = mapped_column(JSON, default=dict)
    experiment_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ab_tests")

    __table_args__ = (
        Index("idx_ab_tests_user_id", "user_id"),
        Index("idx_ab_tests_is_active", "is_active"),
        Index("idx_ab_tests_test_type", "test_type"),
        CheckConstraint(
            "test_type IN ('template', 'timing', 'subject_line')",
            name="ab_tests_test_type_check",
        ),
    )


class EmailEvent(Base):
    """Email delivery and engagement tracking events."""

    __tablename__ = "email_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    campaign_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="email_events"
    )

    __table_args__ = (
        Index("idx_email_events_campaign_id", "campaign_id"),
        Index("idx_email_events_event_type", "event_type"),
        Index("idx_email_events_occurred_at", "occurred_at"),
        CheckConstraint(
            "event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')",
            name="email_events_event_type_check",
        ),
    )


class AuditLog(Base):
    """System audit log for tracking changes."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL")
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )


class WebhookEvent(Base):
    """Persistent storage of received webhooks for audit and idempotency."""

    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    event_id: Mapped[str] = mapped_column(String(500), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", server_default="pending"
    )
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_webhook_events_provider", "provider"),
        Index("idx_webhook_events_event_id", "event_id"),
        Index("idx_webhook_events_processing_status", "processing_status"),
        Index("idx_webhook_events_created_at", "created_at"),
        UniqueConstraint("provider", "event_id", name="uniq_provider_event_id"),
        CheckConstraint(
            "processing_status IN ('pending', 'processed', 'failed')",
            name="webhook_events_processing_status_check",
        ),
        CheckConstraint(
            "provider IN ('stripe', 'paypal', 'plaid')",
            name="webhook_events_provider_check",
        ),
    )


class SystemMetric(Base):
    """System metrics for monitoring and analytics."""

    __tablename__ = "system_metrics"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    labels: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_system_metrics_name", "metric_name"),
        Index("idx_system_metrics_recorded_at", "recorded_at"),
    )


class RefreshToken(Base):
    """Refresh tokens for JWT token rotation."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token_hash", "token_hash"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )
