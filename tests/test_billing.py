"""
Tests for billing module.

Tests cover:
- Plan lookups
- Checkout session creation
- Subscription status retrieval
- Invoice limit calculation
- Webhook processing
"""

import os
import json
from unittest.mock import Mock, patch, MagicMock
import pytest
from sqlalchemy.orm import Session

# Mock Stripe settings for testing - MUST be set BEFORE importing billing module
os.environ["STRIPE_API_KEY"] = "sk_test_123"
os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"
os.environ["STRIPE_PRICE_FREE"] = "price_free_123"

from src.models import User
from src.billing import (
    create_checkout_session,
    get_subscription_info,
    calculate_invoice_limit,
    PLANS,
    get_plan_by_price_id,
    get_plan_by_tier,
)
from src.billing.stripe_billing import (
    _handle_subscription_updated,
    _handle_subscription_deleted,
    handle_webhook_event,
)
from src.billing.schemas import CheckoutSessionResponse, SubscriptionStatus


class TestPlanLookups:
    """Test plan lookup functions."""

    def test_get_plan_by_price_id_returns_correct_plan(self):
        """Test retrieving plan by price ID."""
        plan = get_plan_by_price_id("price_pro_123")
        assert plan is not None
        assert plan.name == "Pro"
        assert plan.price_monthly == 1900

    def test_get_plan_by_price_id_returns_none_for_unknown(self):
        """Test that unknown price ID returns None."""
        plan = get_plan_by_price_id("price_unknown")
        assert plan is None

    def test_get_plan_by_tier_returns_correct_plan(self):
        """Test retrieving plan by tier."""
        plan = get_plan_by_tier("pro")
        assert plan is not None
        assert plan.name == "Pro"

    def test_get_plan_by_tier_returns_none_for_unknown(self):
        """Test that unknown tier returns None."""
        plan = get_plan_by_tier("unknown")
        assert plan is None


class TestCalculateInvoiceLimit:
    """Test invoice limit calculation."""

    def test_free_tier_limit(self):
        """Test free tier has 5 invoice limit."""
        limit = calculate_invoice_limit("free")
        assert limit == 5

    def test_pro_tier_limit_unlimited(self):
        """Test pro tier has unlimited invoices (-1)."""
        limit = calculate_invoice_limit("pro")
        assert limit == -1

    def test_legal_pack_tier_limit_zero(self):
        """Test legal pack add-on has 0 invoice limit (doesn't change base)."""
        limit = calculate_invoice_limit("legal_pack")
        assert limit == 0

    def test_unknown_tier_returns_default(self):
        """Test unknown tier returns default free limit."""
        limit = calculate_invoice_limit("unknown")
        assert limit == 5


class TestCreateCheckoutSession:
    """Test checkout session creation."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = User(
            id="user_123",
            email="test@example.com",
            full_name="Test User",
            company_name=None,
            subscription_tier="free",
            invoice_limit=5,
            extra_data={},
        )
        return user

    @patch("src.billing.stripe_billing.stripe")
    def test_create_checkout_session_success(self, mock_stripe, mock_user):
        """Test successful checkout session creation."""
        # Mock Stripe customer and session
        mock_customer = Mock(id="cus_123")
        mock_session = Mock(id="sess_123", url="https://checkout.stripe.com/session")
        mock_stripe.Customer.create.return_value = mock_customer
        mock_stripe.checkout.Session.create.return_value = mock_session

        # Set price ID in environment
        os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"

        response = create_checkout_session(
            user=mock_user,
            plan_id="price_pro_123",
        )

        assert isinstance(response, CheckoutSessionResponse)
        assert response.session_id == "sess_123"
        assert response.url == "https://checkout.stripe.com/session"

        # Verify customer was created with metadata
        mock_stripe.Customer.create.assert_called_once()
        call_args = mock_stripe.Customer.create.call_args
        assert call_args[1]["email"] == mock_user.email
        assert call_args[1]["metadata"]["user_id"] == mock_user.id

        # Verify checkout session was created
        mock_stripe.checkout.Session.create.assert_called_once()
        session_call_args = mock_stripe.checkout.Session.create.call_args
        assert session_call_args[1]["customer"] == "cus_123"
        assert session_call_args[1]["mode"] == "subscription"
        assert len(session_call_args[1]["line_items"]) == 1
        assert session_call_args[1]["line_items"][0]["price"] == "price_pro_123"

    @patch("src.billing.stripe_billing.stripe")
    def test_create_checkout_session_uses_existing_customer(
        self, mock_stripe, mock_user
    ):
        """Test that existing customer ID is reused."""
        # Set existing customer ID
        mock_user.extra_data = {"stripe_customer_id": "cus_existing"}
        mock_stripe.Customer.retrieve.return_value = Mock(id="cus_existing")

        mock_session = Mock(id="sess_123", url="https://checkout.stripe.com/session")
        mock_stripe.checkout.Session.create.return_value = mock_session

        os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"

        response = create_checkout_session(
            user=mock_user,
            plan_id="price_pro_123",
        )

        # Should retrieve existing customer, not create new
        mock_stripe.Customer.retrieve.assert_called_once_with("cus_existing")
        mock_stripe.Customer.create.assert_not_called()

    def test_create_checkout_session_invalid_plan(self, mock_user):
        """Test that invalid plan ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid plan ID"):
            create_checkout_session(
                user=mock_user,
                plan_id="price_invalid",
            )


class TestGetSubscriptionInfo:
    """Test subscription info retrieval."""

    @pytest.fixture
    def mock_user_with_customer(self):
        """Create a mock user with Stripe customer ID."""
        user = User(
            id="user_123",
            email="test@example.com",
            subscription_tier="pro",
            extra_data={"stripe_customer_id": "cus_123"},
        )
        return user

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_with_active_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test retrieving subscription info when user has active subscription."""
        # Mock subscription as object with attributes (Stripe objects have attributes)
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1700000000  # Unix timestamp
        mock_subscription.cancel_at_period_end = False

        # Mock items as a ListObject with .data containing items that have .price.id
        mock_price = Mock()
        mock_price.id = "price_pro_123"
        mock_item = Mock()
        mock_item.price = mock_price
        mock_items = Mock()
        mock_items.data = [mock_item]
        mock_subscription.items = mock_items

        mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])

        # Use real get_plan_by_price_id (PLANS should be configured via conftest env vars)
        subscription = get_subscription_info(mock_user_with_customer)

        assert subscription is not None
        assert subscription.stripe_subscription_id == "sub_123"
        assert subscription.status == "active"
        assert subscription.tier == "pro"
        assert subscription.plan is not None
        assert subscription.plan.name == "Pro"

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_no_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test returning None when user has no active subscription."""
        mock_stripe.Subscription.list.return_value = Mock(data=[])

        subscription = get_subscription_info(mock_user_with_customer)
        assert subscription is None

    def test_get_subscription_info_no_customer_id(self):
        """Test returning None when user has no Stripe customer ID."""
        user = User(
            id="user_123",
            email="test@example.com",
            extra_data={},  # No customer ID
        )

        subscription = get_subscription_info(user)
        assert subscription is None

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_handles_stripe_error(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test that Stripe errors return None gracefully."""
        mock_stripe.Subscription.list.side_effect = Exception("Stripe API error")

        subscription = get_subscription_info(mock_user_with_customer)
        assert subscription is None


class TestWebhookHandling:
    """Test Stripe webhook event handling."""

    @patch("src.billing.stripe_billing.stripe")
    def test_handle_subscription_updated(self, mock_stripe):
        """Test subscription update webhook updates user tier."""
        # Create a mock DB session
        mock_db = MagicMock(spec=Session)

        # Mock subscription payload
        subscription = {
            "id": "sub_123",
            "metadata": {"user_id": "user_123"},
            "items": {"data": [{"price": {"id": "price_pro_123"}}]},
        }

        # Mock plan lookup
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock()
            mock_plan.name = "Pro"
            mock_plan.invoice_limit = -1
            mock_get_plan.return_value = mock_plan

            # We need to mock the SubscriptionUpdater.update_user_tier
            with patch(
                "src.billing.stripe_billing.SubscriptionUpdater.update_user_tier"
            ) as mock_update:
                # Manually set the env var for plan
                os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"

                _handle_subscription_updated(mock_db, subscription)

                # Should call update_user_tier with db, user_id, tier, subscription
                mock_update.assert_called_once()
                call_args = mock_update.call_args
                assert call_args[0][0] == mock_db  # db session
                assert call_args[0][1] == "user_123"  # user_id
                assert call_args[0][2] == "pro"  # tier
                assert call_args[0][3] == subscription  # subscription

    def test_handle_subscription_deleted(self):
        """Test subscription deletion webhook downgrades to free."""
        mock_db = MagicMock(spec=Session)
        with patch(
            "src.billing.stripe_billing.SubscriptionUpdater.downgrade_to_free"
        ) as mock_downgrade:
            subscription = {
                "metadata": {"user_id": "user_123"},
            }

            _handle_subscription_deleted(mock_db, subscription)

            mock_downgrade.assert_called_once_with(mock_db, "user_123")

    @patch("src.billing.stripe_billing.stripe")
    def test_handle_webhook_event_success(self, mock_stripe):
        """Test successful webhook event processing."""
        mock_db = MagicMock(spec=Session)
        signature = "valid_signature"

        # Mock Webhook.construct_event to return a valid event with ID
        payload_with_id = {
            "id": "evt_123",
            "type": "customer.subscription.updated",
            "data": {"object": {}},
        }
        mock_stripe.Webhook.construct_event.return_value = payload_with_id

        payload_bytes = json.dumps(payload_with_id).encode()
        event_id = handle_webhook_event(mock_db, payload_bytes, signature)
        assert event_id == "evt_123"

    def test_handle_webhook_event_invalid_signature(self):
        """Test webhook with invalid signature raises ValueError."""
        mock_db = MagicMock(spec=Session)
        payload_dict = {}
        signature = "invalid"

        with patch("src.billing.stripe_billing.stripe") as mock_stripe:
            mock_stripe.Webhook.construct_event.side_effect = Exception(
                "Invalid signature"
            )

            payload_bytes = json.dumps(payload_dict).encode()
            with pytest.raises(ValueError, match="Webhook verification failed"):
                handle_webhook_event(mock_db, payload_bytes, signature)
