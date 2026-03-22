"""
Webhook endpoints test suite.

Tests for Stripe and PayPal webhook receivers including:
- Signature verification
- Event processing
- Idempotency
- Invoice status updates
- Error handling
"""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.core.config import Settings
from src.core.database import get_session
from src.models import Base, User, Invoice, PaymentConnection
from src.main import app

# Override settings for testing
test_settings = Settings()
test_settings.database_url = "sqlite:///:memory:"
test_settings.stripe_webhook_secret = "whsec_test_secret"
test_settings.paypal_webhook_id = "webhook_secret"

# Create test database
engine = create_engine(
    test_settings.database_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_user(db: Session) -> User:
    """Create a test user."""
    from src.api.auth import get_password_hash

    user = User(
        email="test@example.com",
        password_hash=get_password_hash("secret"),
        full_name="Test User",
        company_name="Test Co",
        subscription_tier="pro",
        invoice_limit=100,
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_invoice(
    db: Session,
    user: User,
    status: str = "sent",
    stripe_id: str = None,
    paypal_id: str = None,
) -> Invoice:
    """Create a test invoice."""
    invoice = Invoice(
        user_id=user.id,
        invoice_number="INV-001",
        client_name="Test Client",
        client_email="client@example.com",
        amount=100.00,
        currency="USD",
        status=status,
        due_date=datetime.now(),
        issue_date=datetime.now(),
        stripe_invoice_id=stripe_id,
        paypal_txn_id=paypal_id,
        description="Test invoice",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def create_payment_connection(
    db: Session, user: User, provider: str
) -> PaymentConnection:
    """Create a payment connection for the user."""
    conn = PaymentConnection(
        user_id=user.id,
        provider=provider,
        connection_name=f"{provider} Test Connection",
        credentials_encrypted="encrypted_creds",
        external_account_id="acct_123",
        is_active=True,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


def generate_stripe_signature(payload: bytes, secret: str) -> str:
    """Generate a valid Stripe signature for testing."""
    from time import time

    timestamp = int(datetime.now().timestamp())
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    signature = hmac.new(
        secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def generate_paypal_signature(payload: bytes, secret: str) -> str:
    """Generate a PayPal signature for testing."""
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_db


client = TestClient(app)


class TestStripeWebhook:
    """Test Stripe webhook endpoint."""

    def setup_method(self):
        """Set up test database."""
        self.db = TestingSessionLocal()

        # Clean up existing data
        self.db.query(Invoice).delete()
        self.db.query(PaymentConnection).delete()
        self.db.query(User).delete()
        self.db.commit()

        self.user = create_test_user(self.db)
        self.invoice = create_test_invoice(self.db, self.user, stripe_id="inv_123456")
        create_payment_connection(self.db, self.user, "stripe")

    def teardown_method(self):
        """Clean up test database."""
        self.db.rollback()
        self.db.close()

    def test_stripe_valid_payment_failed(self):
        """Test Stripe invoice.payment_failed event."""
        event = {
            "id": "evt_test123",
            "type": "invoice.payment_failed",
            "object": "event",
            "data": {
                "object": {
                    "id": "inv_123456",
                    "payment_intent": "pi_123456",
                    "status": "open",
                }
            },
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_stripe_signature(payload, "whsec_test_secret")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["event_id"] == "evt_test123"

        # Check invoice status updated
        self.db.refresh(self.invoice)
        assert self.invoice.status == "overdue"

    def test_stripe_valid_dispute_created(self):
        """Test Stripe charge.dispute.created event."""
        event = {
            "id": "evt_dispute123",
            "type": "charge.dispute.created",
            "object": "event",
            "data": {
                "object": {
                    "id": "ch_123456",
                    "payment_intent": "pi_123456",
                    "status": "requires_response",
                }
            },
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_stripe_signature(payload, "whsec_test_secret")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        self.db.refresh(self.invoice)
        assert self.invoice.status == "disputed"

    def test_stripe_invalid_signature(self):
        """Test Stripe webhook with invalid signature."""
        event = {
            "id": "evt_test",
            "type": "invoice.payment_failed",
            "data": {"object": {"id": "inv_123"}},
        }
        payload = json.dumps(event).encode("utf-8")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={
                "Stripe-Signature": "t=123,v1=invalid",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    def test_stripe_missing_signature(self):
        """Test Stripe webhook without signature header."""
        event = {"id": "evt_test", "type": "invoice.payment_failed"}
        payload = json.dumps(event).encode("utf-8")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400

    def test_stripe_duplicate_event(self):
        """Test Stripe webhook idempotency."""
        event = {
            "id": "evt_duplicate123",
            "type": "invoice.payment_failed",
            "data": {"object": {"id": "inv_123456"}},
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_stripe_signature(payload, "whsec_test_secret")

        # First request
        response1 = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )
        assert response1.status_code == 200
        assert response1.json()["status"] == "success"

        # Second request with same event ID
        response2 = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )
        assert response2.status_code == 200
        assert response2.json()["status"] == "duplicate"
        assert response2.json()["message"] == "Event already processed"

    def test_stripe_no_matching_invoice(self):
        """Test Stripe webhook with no matching invoice."""
        event = {
            "id": "evt_nomatch",
            "type": "invoice.payment_failed",
            "data": {"object": {"id": "inv_unknown"}},
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_stripe_signature(payload, "whsec_test_secret")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        # Invoice status should remain unchanged
        self.db.refresh(self.invoice)
        assert self.invoice.status == "sent"

    def test_stripe_invalid_json(self):
        """Test Stripe webhook with invalid JSON."""
        payload = b"invalid json{"
        signature = generate_stripe_signature(payload, "whsec_test_secret")

        response = client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
        )

        assert response.status_code == 400


class TestPayPalWebhook:
    """Test PayPal webhook endpoint."""

    def setup_method(self):
        """Set up test database."""
        self.db = TestingSessionLocal()

        # Clean up existing data
        self.db.query(Invoice).delete()
        self.db.query(PaymentConnection).delete()
        self.db.query(User).delete()
        self.db.commit()

        self.user = create_test_user(self.db)
        self.invoice = create_test_invoice(self.db, self.user, paypal_id="PAY-123456")
        create_payment_connection(self.db, self.user, "paypal")

    def teardown_method(self):
        """Clean up test database."""
        self.db.rollback()
        self.db.close()

    def test_paypal_valid_payment_denied(self):
        """Test PayPal PAYMENT.DENIED event."""
        event = {
            "id": "WH-123",
            "event_type": "PAYMENT.DENIED",
            "resource": {"id": "PAY-123456", "status": "DENIED"},
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_paypal_signature(payload, "webhook_secret")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans123",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        self.db.refresh(self.invoice)
        assert self.invoice.status == "overdue"

    def test_paypal_valid_dispute_created(self):
        """Test PayPal DISPUTE.CREATED event."""
        event = {
            "id": "WH-DISPUTE123",
            "event_type": "DISPUTE.CREATED",
            "resource": {"id": "PP-DISPUTE-123", "dispute_id": "DC-123456"},
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_paypal_signature(payload, "webhook_secret")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans456",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        self.db.refresh(self.invoice)
        assert self.invoice.status == "disputed"

    def test_paypal_invalid_signature(self):
        """Test PayPal webhook with invalid signature."""
        event = {"event_type": "PAYMENT.DENIED", "resource": {"id": "PAY-123"}}
        payload = json.dumps(event).encode("utf-8")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans123",
                "Paypal-Transmission-Sig": "invalid_signature",
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400

    def test_paypal_missing_headers(self):
        """Test PayPal webhook with missing required headers."""
        event = {"event_type": "PAYMENT.DENIED"}
        payload = json.dumps(event).encode("utf-8")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400

    def test_paypal_duplicate_event(self):
        """Test PayPal webhook idempotency."""
        event = {
            "id": "WH-DUP123",
            "event_type": "PAYMENT.DENIED",
            "resource": {"id": "PAY-123456"},
        }
        payload = json.dumps(event).encode("utf-8")
        signature = generate_paypal_signature(payload, "webhook_secret")

        # First request
        response1 = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans_dup",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )
        assert response1.status_code == 200

        # Second request with same event ID
        response2 = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans_dup",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )
        assert response2.status_code == 200
        assert response2.json()["status"] == "duplicate"

    def test_paypal_invalid_json(self):
        """Test PayPal webhook with invalid JSON."""
        payload = b"not valid json"
        signature = generate_paypal_signature(payload, "webhook_secret")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans123",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400

    def test_paypal_without_event_type(self):
        """Test PayPal webhook without event_type."""
        event = {"resource": {"id": "PAY-123"}}
        payload = json.dumps(event).encode("utf-8")
        signature = generate_paypal_signature(payload, "webhook_secret")

        response = client.post(
            "/api/webhooks/paypal",
            content=payload,
            headers={
                "Paypal-Transmission-Id": "trans123",
                "Paypal-Transmission-Sig": signature,
                "Paypal-Cert-Url": "https://api.paypal.com/v1/notifications/certs/CERT-test",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400


class TestWebhookStatus:
    """Test webhook status endpoint."""

    def test_webhook_status_endpoint(self):
        """Test the /webhooks/status endpoint."""
        response = client.get("/api/webhooks/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "stripe" in data["providers"]
        assert "paypal" in data["providers"]
        assert "invoice.payment_failed" in data["stripe_events"]
        assert "PAYMENT.DENIED" in data["paypal_events"]
