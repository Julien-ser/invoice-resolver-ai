"""
Tests for SQLAlchemy database models.

This module tests all database models, their relationships,
constraints, and business logic methods.
"""

import pytest
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.exc import IntegrityError

from src.models import (
    User,
    Invoice,
    PaymentConnection,
    Template,
    Campaign,
    ABTest,
    EmailEvent,
    AuditLog,
    WebhookEvent,
    SystemMetric,
    RefreshToken,
)


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self, db_session):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            password_hash="hashedpassword",
            full_name="Test User",
            company_name="Test Corp",
            subscription_tier="pro",
            invoice_limit=100,
            timezone="America/New_York",
            email_notifications_enabled=True,
            is_active=True,
            is_admin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.subscription_tier == "pro"
        assert user.invoice_limit == 100
        assert user.is_active is True
        assert user.is_admin is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_uniqueness(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            email="duplicate@example.com",
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_user_defaults(self, db_session):
        """Test default values for User fields."""
        user = User(
            email="defaults@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.subscription_tier == "free"
        assert user.invoice_limit == 5
        assert user.timezone == "UTC"
        assert user.email_notifications_enabled is True
        assert user.is_active is True
        assert user.is_admin is False
        assert user.full_name is None
        assert user.company_name is None

    def test_user_relationships(self, db_session):
        """Test User relationships to other models."""
        user = User(
            email="reltest@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test empty relationships
        assert user.payment_connections == []
        assert user.invoices == []
        assert user.templates == []
        assert user.campaigns == []
        assert user.ab_tests == []
        assert user.audit_logs == []
        assert user.refresh_tokens == []

    def test_user_invoice_limit_check(self, db_session):
        """Test invoice limit based on subscription tier."""
        free_user = User(
            email="free@example.com", password_hash="hash", subscription_tier="free"
        )
        pro_user = User(
            email="pro@example.com", password_hash="hash", subscription_tier="pro"
        )
        enterprise_user = User(
            email="enterprise@example.com",
            password_hash="hash",
            subscription_tier="enterprise",
        )

        db_session.add_all([free_user, pro_user, enterprise_user])
        db_session.commit()

        assert free_user.invoice_limit == 5
        assert pro_user.invoice_limit == 999  # unlimited
        assert enterprise_user.invoice_limit == 999  # unlimited


class TestInvoiceModel:
    """Tests for Invoice model."""

    def test_invoice_creation(self, db_session):
        """Test creating a new invoice."""
        # Create a user first
        user = User(email="invoiceuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-001",
            client_name="Client Corp",
            client_email="client@example.com",
            amount=1500.00,
            currency="USD",
            status="draft",
            due_date=date.today() + timedelta(days=30),
            description="Consulting services",
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        assert invoice.id is not None
        assert invoice.invoice_number == "INV-001"
        assert invoice.amount == 1500.00
        assert invoice.status == "draft"
        assert invoice.user_id == user.id
        assert invoice.created_at is not None

    def test_invoice_status_constraint(self, db_session):
        """Test that invoice status must be valid."""
        user = User(email="statususer@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-002",
            client_name="Client Corp",
            amount=100.00,
            status="invalid_status",
            due_date=date.today(),
        )
        db_session.add(invoice)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_invoice_amount_positive(self, db_session):
        """Test that invoice amount must be positive."""
        user = User(email="amountuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-003",
            client_name="Client Corp",
            amount=-100.00,
            status="draft",
            due_date=date.today(),
        )
        db_session.add(invoice)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_invoice_relationship_user(self, db_session):
        """Test Invoice relationship to User."""
        user = User(email="reluser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-004",
            client_name="Client Corp",
            amount=200.00,
            status="draft",
            due_date=date.today(),
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        assert invoice.user == user
        assert invoice in user.invoices

    def test_invoice_overdue_property(self, db_session):
        """Test Invoice.is_overdue property."""
        user = User(email="overdueuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create an overdue invoice
        overdue_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-OVERDUE",
            client_name="Client Corp",
            amount=100.00,
            status="overdue",
            due_date=date.today() - timedelta(days=5),
        )
        # Create a not overdue invoice
        current_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-CURRENT",
            client_name="Client Corp",
            amount=100.00,
            status="draft",
            due_date=date.today() + timedelta(days=5),
        )
        db_session.add_all([overdue_invoice, current_invoice])
        db_session.commit()

        assert overdue_invoice.is_overdue is True
        assert current_invoice.is_overdue is False

    def test_invoice_paid_property(self, db_session):
        """Test Invoice.is_paid property."""
        user = User(email="paiduser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        now = datetime.now(timezone.utc)
        paid_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-PAID",
            client_name="Client Corp",
            amount=100.00,
            status="paid",
            due_date=date.today(),
            paid_date=now,
        )
        unpaid_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-UNPAID",
            client_name="Client Corp",
            amount=100.00,
            status="draft",
            due_date=date.today(),
        )
        db_session.add_all([paid_invoice, unpaid_invoice])
        db_session.commit()

        assert paid_invoice.is_paid is True
        assert unpaid_invoice.is_paid is False

    def test_invoice_days_overdue_property(self, db_session):
        """Test Invoice.days_overdue property."""
        user = User(email="daysuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Overdue by 5 days
        overdue_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-OVERDUE5",
            client_name="Client Corp",
            amount=100.00,
            status="overdue",
            due_date=date.today() - timedelta(days=5),
        )
        # Not overdue
        current_invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-CURRENT",
            client_name="Client Corp",
            amount=100.00,
            status="draft",
            due_date=date.today() + timedelta(days=5),
        )
        db_session.add_all([overdue_invoice, current_invoice])
        db_session.commit()

        assert overdue_invoice.days_overdue == 5
        assert current_invoice.days_overdue == 0

    def test_invoice_campaigns_relationship(self, db_session):
        """Test Invoice relationship to Campaigns."""
        user = User(email="campuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-CAMPAIGN",
            client_name="Client Corp",
            amount=100.00,
            status="overdue",
            due_date=date.today() - timedelta(days=10),
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        template = Template(
            user_id=user.id,
            is_system=False,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test Subject",
            body_html="<p>Test Body</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=invoice.id,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()

        assert campaign in invoice.campaigns
        assert invoice in user.invoices


class TestPaymentConnectionModel:
    """Tests for PaymentConnection model."""

    def test_payment_connection_creation(self, db_session):
        """Test creating a payment connection."""
        user = User(email="connuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connection = PaymentConnection(
            user_id=user.id,
            provider="stripe",
            connection_name="Main Stripe",
            credentials_encrypted="encrypted_creds",
            external_account_id="acct_123",
            external_user_id="user_123",
            is_active=True,
        )
        db_session.add(connection)
        db_session.commit()
        db_session.refresh(connection)

        assert connection.id is not None
        assert connection.provider == "stripe"
        assert connection.connection_name == "Main Stripe"
        assert connection.is_active is True
        assert connection.user == user

    def test_payment_connection_provider_constraint(self, db_session):
        """Test provider must be one of allowed values."""
        user = User(email="provuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connection = PaymentConnection(
            user_id=user.id,
            provider="invalid_provider",
            credentials_encrypted="encrypted",
        )
        db_session.add(connection)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_payment_connection_unique_constraint(self, db_session):
        """Test unique constraint on (user_id, provider, is_active=True)."""
        user = User(email="uniquser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connection1 = PaymentConnection(
            user_id=user.id,
            provider="stripe",
            credentials_encrypted="creds1",
            is_active=True,
        )
        db_session.add(connection1)
        db_session.commit()

        connection2 = PaymentConnection(
            user_id=user.id,
            provider="stripe",
            credentials_encrypted="creds2",
            is_active=True,
        )
        db_session.add(connection2)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_payment_connection_multiple_inactive_allowed(self, db_session):
        """Test that multiple inactive connections for same provider are allowed."""
        user = User(email="inactiveuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        connection1 = PaymentConnection(
            user_id=user.id,
            provider="stripe",
            credentials_encrypted="creds1",
            is_active=False,
        )
        connection2 = PaymentConnection(
            user_id=user.id,
            provider="stripe",
            credentials_encrypted="creds2",
            is_active=False,
        )
        db_session.add_all([connection1, connection2])
        db_session.commit()  # Should succeed

        assert connection1.id is not None
        assert connection2.id is not None


class TestTemplateModel:
    """Tests for Template model."""

    def test_template_creation(self, db_session):
        """Test creating a template."""
        user = User(email="tpluser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            is_system=False,
            name="Follow-up Email",
            type="follow_up_7_day",
            subject="Invoice {{invoice_number}} is overdue",
            body_html="<p>Hello {{client_name}}, your invoice is overdue.</p>",
            body_text="Hello {{client_name}}, your invoice is overdue.",
            variables=["invoice_number", "client_name", "amount"],
            is_active=True,
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        assert template.id is not None
        assert template.name == "Follow-up Email"
        assert template.type == "follow_up_7_day"
        assert template.variables == ["invoice_number", "client_name", "amount"]

    def test_system_template_without_user(self, db_session):
        """Test that system templates can exist without user_id."""
        template = Template(
            user_id=None,
            is_system=True,
            name="System Template",
            type="follow_up_3_day",
            subject="Reminder",
            body_html="<p>Reminder text</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        assert template.user_id is None
        assert template.is_system is True

    def test_template_type_constraint(self, db_session):
        """Test template type must be valid."""
        user = User(email="tpltypeuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            name="Invalid Type",
            type="invalid_type",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_template_relationship_user(self, db_session):
        """Test Template relationship to User."""
        user = User(email="tplreluser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        assert template.user == user
        assert template in user.templates


class TestCampaignModel:
    """Tests for Campaign model."""

    def test_campaign_creation(self, db_session):
        """Test creating a campaign."""
        user = User(email="campuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            is_system=False,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=None,
            ab_test_variant="A",
            scheduled_send_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        assert campaign.id is not None
        assert campaign.ab_test_variant == "A"
        assert campaign.sent_at is None
        assert campaign.opened_count == 0

    def test_campaign_relationships(self, db_session):
        """Test Campaign relationships."""
        user = User(email="campreluser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-CAMP",
            client_name="Client",
            amount=100.00,
            status="overdue",
            due_date=date.today() - timedelta(days=5),
        )
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)

        template = Template(
            user_id=user.id,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=invoice.id,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()

        assert campaign.user == user
        assert campaign.template == template
        assert campaign.invoice == invoice
        assert campaign in user.campaigns
        assert campaign in template.campaigns
        assert campaign in invoice.campaigns

    def test_campaign_email_events_relationship(self, db_session):
        """Test Campaign relationship to EmailEvents."""
        user = User(email="campuserevent@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=None,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        event = EmailEvent(
            campaign_id=campaign.id,
            event_type="sent",
        )
        db_session.add(event)
        db_session.commit()

        assert event in campaign.email_events


class TestABTestModel:
    """Tests for ABTest model."""

    def test_ab_test_creation(self, db_session):
        """Test creating an A/B test."""
        user = User(email="abtestuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        ab_test = ABTest(
            user_id=user.id,
            name="Email Template Test",
            description="Testing two email templates",
            test_type="template",
            variants={"A": "Template A content", "B": "Template B content"},
            is_active=True,
        )
        db_session.add(ab_test)
        db_session.commit()
        db_session.refresh(ab_test)

        assert ab_test.id is not None
        assert ab_test.name == "Email Template Test"
        assert ab_test.test_type == "template"
        assert ab_test.variants["A"] == "Template A content"
        assert ab_test.is_active is True

    def test_ab_test_type_constraint(self, db_session):
        """Test test_type must be valid."""
        user = User(email="abtesttype@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        ab_test = ABTest(
            user_id=user.id,
            name="Invalid Test",
            test_type="invalid_type",
            variants={},
        )
        db_session.add(ab_test)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_ab_test_relationship_user(self, db_session):
        """Test ABTest relationship to User."""
        user = User(email="abtestrel@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        ab_test = ABTest(
            user_id=user.id,
            name="Test",
            test_type="timing",
            variants={},
        )
        db_session.add(ab_test)
        db_session.commit()

        assert ab_test.user == user
        assert ab_test in user.ab_tests


class TestEmailEventModel:
    """Tests for EmailEvent model."""

    def test_email_event_creation(self, db_session):
        """Test creating an email event."""
        user = User(email="eventuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=None,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        event = EmailEvent(
            campaign_id=campaign.id,
            event_type="opened",
            event_data={"user_agent": "Test Agent"},
            ip_address="192.168.1.1",
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)

        assert event.id is not None
        assert event.event_type == "opened"
        assert event.campaign == campaign
        assert event in campaign.email_events

    def test_email_event_type_constraint(self, db_session):
        """Test event_type must be valid."""
        user = User(email="eventtype@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        template = Template(
            user_id=user.id,
            name="Test Template",
            type="follow_up_7_day",
            subject="Test",
            body_html="<p>Test</p>",
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=None,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        event = EmailEvent(
            campaign_id=campaign.id,
            event_type="invalid_event",
        )
        db_session.add(event)

        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestAuditLogModel:
    """Tests for AuditLog model."""

    def test_audit_log_creation(self, db_session):
        """Test creating an audit log entry."""
        user = User(email="audituser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        audit_log = AuditLog(
            user_id=user.id,
            action="user.login",
            entity_type="user",
            entity_id=user.id,
            old_values={"last_login": None},
            new_values={"last_login": datetime.now(timezone.utc).isoformat()},
            ip_address="192.168.1.1",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.id is not None
        assert audit_log.action == "user.login"
        assert audit_log.entity_type == "user"
        assert audit_log.user == user

    def test_audit_log_without_user(self, db_session):
        """Test audit log can exist without user_id (system action)."""
        audit_log = AuditLog(
            user_id=None,
            action="system.backup",
            entity_type="system",
            entity_id=None,
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        assert audit_log.user is None


class TestRefreshTokenModel:
    """Tests for RefreshToken model."""

    def test_refresh_token_creation(self, db_session):
        """Test creating a refresh token."""
        user = User(email="tokenuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token_123",
            is_revoked=False,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        assert token.id is not None
        assert token.token_hash == "hashed_token_123"
        assert token.is_revoked is False
        assert token.user == user
        assert token in user.refresh_tokens

    def test_refresh_token_revoked(self, db_session):
        """Test revoking a refresh token."""
        user = User(email="revokeuser@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            is_revoked=False,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        token.is_revoked = True
        db_session.commit()

        assert token.is_revoked is True
