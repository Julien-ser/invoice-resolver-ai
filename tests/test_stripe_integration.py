"""
Tests for Stripe API client integration.

This module provides comprehensive unit tests for the StripeClient class
with mocked Stripe SDK to avoid real API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.integrations.stripe_client import StripeClient, StripeError
from src.core.config import Settings


class TestStripeClientInitialization:
    """Test StripeClient initialization and configuration."""

    def test_init_with_api_key(self):
        """Test client initializes with provided API key."""
        client = StripeClient(api_key="sk_test_123")
        assert client.api_key == "sk_test_123"

    def test_init_with_settings(self, monkeypatch):
        """Test client initializes with settings API key."""
        settings = Settings()
        settings.stripe_api_key = "sk_test_from_settings"
        monkeypatch.setattr("src.integrations.stripe_client.settings", settings)

        client = StripeClient()
        assert client.api_key == "sk_test_from_settings"

    def test_init_without_api_key_raises_error(self, monkeypatch):
        """Test client raises error when no API key available."""
        settings = Settings()
        settings.stripe_api_key = None
        monkeypatch.setattr("src.integrations.stripe_client.settings", settings)

        with pytest.raises(StripeError, match="Stripe API key not configured"):
            StripeClient()

    def test_init_prefers_provided_key_over_settings(self, monkeypatch):
        """Test provided key takes precedence over settings."""
        settings = Settings()
        settings.stripe_api_key = "sk_settings"
        monkeypatch.setattr("src.integrations.stripe_client.settings", settings)

        client = StripeClient(api_key="sk_provided")
        assert client.api_key == "sk_provided"


class TestConnectAccount:
    """Test Stripe Connect account linking."""

    @patch("src.integrations.stripe_client.stripe.OAuth")
    def test_connect_account_success(self, mock_oauth):
        """Test successful account connection."""
        # Mock OAuth response
        mock_oauth.token.return_value = {
            "stripe_user_id": "acct_12345",
            "access_token": "sk_live_123",
            "refresh_token": "rt_123",
            "livemode": False,
        }

        client = StripeClient(api_key="sk_test")
        result = client.connect_account("auth_code_123")

        assert result["account_id"] == "acct_12345"
        assert result["access_token"] == "sk_live_123"
        assert result["refresh_token"] == "rt_123"
        assert result["livemode"] is False

        mock_oauth.token.assert_called_once_with(
            grant_type="authorization_code", code="auth_code_123"
        )

    @patch("src.integrations.stripe_client.stripe.OAuth")
    def test_connect_account_stripe_error(self, mock_oauth):
        """Test connection failure with Stripe error."""
        from stripe.error import StripeError as StripeSDKError

        mock_oauth.token.side_effect = StripeSDKError("OAuth failed")

        client = StripeClient(api_key="sk_test")

        with pytest.raises(StripeError, match="Failed to connect Stripe account"):
            client.connect_account("bad_code")

    @patch("src.integrations.stripe_client.stripe.OAuth")
    def test_connect_account_partial_response(self, mock_oauth):
        """Test connection with incomplete OAuth response."""
        mock_oauth.token.return_value = {
            "stripe_user_id": "acct_12345",
            # Missing access_token, refresh_token
        }

        client = StripeClient(api_key="sk_test")
        result = client.connect_account("auth_code")

        assert result["account_id"] == "acct_12345"
        assert result["access_token"] is None
        assert result["refresh_token"] is None

    @patch("src.integrations.stripe_client.stripe.OAuth")
    def test_connect_account_logs_success(self, mock_oauth, caplog):
        """Test that successful connection logs info."""
        mock_oauth.token.return_value = {
            "stripe_user_id": "acct_log_test",
            "access_token": "sk_test",
        }

        client = StripeClient(api_key="sk_test")
        result = client.connect_account("auth_code")

        assert "Stripe account connected: acct_log_test" in caplog.text


class TestGetInvoiceStatus:
    """Test invoice status retrieval from Stripe."""

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_by_invoice_id(self, mock_invoice_class):
        """Test retrieving invoice status using invoice ID."""
        # Create mock invoice object
        mock_invoice = Mock()
        mock_invoice.status = "paid"
        mock_invoice.amount_paid = 250000  # Stripe uses cents
        mock_invoice.currency = "usd"
        mock_invoice.due_date = datetime.now().timestamp()
        mock_invoice.status_transitions = Mock()
        mock_invoice.status_transitions.paid_at = datetime.now().timestamp()
        mock_invoice.number = "INV-001"
        mock_invoice.customer_email = "customer@example.com"
        mock_invoice.id = "in_123456"

        mock_invoice_class.retrieve.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("in_123456")

        assert result["status"] == "paid"
        assert result["amount"] == 2500.00  # Converted from cents
        assert result["currency"] == "usd"
        assert result["invoice_id"] == "in_123456"
        assert result["invoice_number"] == "INV-001"
        assert result["customer_email"] == "customer@example.com"

        mock_invoice_class.retrieve.assert_called_once_with("in_123456")

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_get_invoice_status_by_payment_intent(self, mock_pi_class):
        """Test retrieving status using payment intent ID."""
        mock_pi = Mock()
        mock_pi.status = "succeeded"
        mock_pi.amount = 100000  # $1000 in cents
        mock_pi.currency = "usd"
        mock_pi.created = datetime.now().timestamp()
        mock_pi.customer = "cus_123"
        mock_pi.payment_method = "pm_card_visa"
        mock_pi.id = "pi_123"

        mock_pi_class.retrieve.return_value = mock_pi

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("pi_123")

        assert result["status"] == "succeeded"
        assert result["amount"] == 1000.00
        assert result["provider"] == "stripe"
        assert result["invoice_id"] == "pi_123"
        assert result["customer"] == "cus_123"

        mock_pi_class.retrieve.assert_called_once_with("pi_123")

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_not_found(self, mock_invoice_class):
        """Test handling when invoice is not found."""
        from stripe.error import InvalidRequestError

        mock_invoice_class.retrieve.side_effect = InvalidRequestError(
            "No such invoice", "invoice"
        )

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("invalid_id")

        assert result is None

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_general_error(self, mock_invoice_class):
        """Test handling of other Stripe errors."""
        mock_invoice_class.retrieve.side_effect = Exception("API Error")

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("in_123")

        assert result is None

    def test_get_invoice_status_invalid_id_format(self):
        """Test that invoice ID format is checked correctly."""
        client = StripeClient(api_key="sk_test")

        # Should raise StripeError for invalid ID format (doesn't start with in_ or pi_)
        with pytest.raises(StripeError, match="Invalid Stripe ID format"):
            client.get_invoice_status("random_id")

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_fulfills_data_structure(self, mock_invoice_class):
        """Test that returned structure has all required fields for invoice."""
        mock_invoice = Mock()
        mock_invoice.status = "open"
        mock_invoice.amount_paid = 50000  # $500
        mock_invoice.currency = "usd"
        mock_invoice.due_date = datetime.now().timestamp()
        mock_invoice.status_transitions = Mock()
        mock_invoice.status_transitions.paid_at = None
        mock_invoice.number = "INV-TEST"
        mock_invoice.customer_email = "test@example.com"
        mock_invoice.id = "in_999"

        mock_invoice_class.retrieve.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("in_999")

        required_fields = [
            "status",
            "amount",
            "currency",
            "provider",
            "invoice_id",
            "invoice_number",
            "customer_email",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_get_invoice_status_pi_structure(self, mock_pi_class):
        """Test payment intent returns correct fields."""
        mock_pi = Mock()
        mock_pi.status = "requires_payment_method"
        mock_pi.amount = 200000  # $2000
        mock_pi.currency = "eur"
        mock_pi.created = datetime.now().timestamp()
        mock_pi.customer = "cus_abc"
        mock_pi.payment_method = "pm_visa"
        mock_pi.id = "pi_456"

        mock_pi_class.retrieve.return_value = mock_pi

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("pi_456")

        assert result["status"] == "requires_payment_method"
        assert result["amount"] == 2000.00
        assert result["currency"] == "eur"
        assert result["payment_method"] == "pm_visa"


class TestListTransactions:
    """Test transaction listing functionality."""

    @patch("src.integrations.stripe_client.stripe.BalanceTransaction")
    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_success(self, mock_charge_class, mock_bt_class):
        """Test listing balance transactions."""
        # Note: The actual implementation uses Charge.list, not BalanceTransaction.list
        mock_charge1 = Mock()
        mock_charge1.id = "ch_1"
        mock_charge1.amount = 1000
        mock_charge1.currency = "usd"
        mock_charge1.status = "succeeded"
        mock_charge1.created = datetime.now().timestamp()
        mock_charge1.customer = Mock(id="cus_1", email="c1@example.com")
        mock_charge1.payment_method = "pm_1"
        mock_charge1.description = "Test payment"
        mock_charge1.failure_code = None
        mock_charge1.failure_message = None

        mock_charge2 = Mock()
        mock_charge2.id = "ch_2"
        mock_charge2.amount = -500
        mock_charge2.currency = "usd"
        mock_charge2.status = "failed"
        mock_charge2.created = datetime.now().timestamp()
        mock_charge2.customer = None
        mock_charge2.payment_method = None
        mock_charge2.description = "Refund"
        mock_charge2.failure_code = "card_declined"
        mock_charge2.failure_message = "Card was declined"

        mock_charge_class.list.return_value = Mock(data=[mock_charge1, mock_charge2])

        client = StripeClient(api_key="sk_test")
        result = client.list_transactions(limit=2)

        assert len(result) == 2
        assert result[0]["id"] == "ch_1"
        assert result[0]["amount"] == 10.00  # 1000/100
        assert result[0]["status"] == "succeeded"
        assert result[0]["customer_id"] == "cus_1"
        assert result[1]["amount"] == -5.00  # -500/100
        assert result[1]["failure_code"] == "card_declined"

        mock_charge_class.list.assert_called_once()

    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_with_date_filter(self, mock_charge_class):
        """Test listing transactions with date range."""
        client = StripeClient(api_key="sk_test")
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        result = client.list_transactions(start_date=start_date, end_date=end_date)

        # Verify the call was made with correct date parameters
        call_kwargs = mock_charge_class.list.call_args[1]
        assert "created" in call_kwargs
        assert "limit" in call_kwargs

    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_empty_result(self, mock_charge_class):
        """Test handling empty transaction list."""
        mock_charge_class.list.return_value = Mock(data=[])

        client = StripeClient(api_key="sk_test")
        result = client.list_transactions()

        assert result == []

    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_with_account_id(self, mock_charge_class):
        """Test listing transactions for a specific connected account."""
        client = StripeClient(api_key="sk_test")
        result = client.list_transactions(account_id="acct_123")

        call_kwargs = mock_charge_class.list.call_args[1]
        assert "stripe_account" in call_kwargs
        assert call_kwargs["stripe_account"] == "acct_123"

    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_api_error(self, mock_charge_class):
        """Test handling of API errors."""
        mock_charge_class.list.side_effect = Exception("Rate limited")

        client = StripeClient(api_key="sk_test")
        result = client.list_transactions()

        # Should return empty list on error (graceful degradation)
        assert result == []

    @patch("src.integrations.stripe_client.stripe.Charge")
    def test_list_transactions_includes_expand(self, mock_charge_class):
        """Test that expand parameter is set to get customer and payment intent details."""
        client = StripeClient(api_key="sk_test")
        result = client.list_transactions()

        call_kwargs = mock_charge_class.list.call_args[1]
        assert "expand" in call_kwargs
        assert "data.customer" in call_kwargs["expand"]
        assert "data.payment_intent" in call_kwargs["expand"]


class TestCreatePaymentIntent:
    """Test payment intent creation."""

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_create_payment_intent_success(self, mock_pi_class):
        """Test creating a payment intent."""
        mock_pi = Mock()
        mock_pi.id = "pi_123"
        mock_pi.client_secret = "client_secret_123"
        mock_pi.status = "requires_payment_method"
        mock_pi.amount = 200000  # $2000 in cents
        mock_pi.currency = "usd"

        mock_pi_class.create.return_value = mock_pi

        client = StripeClient(api_key="sk_test")
        result = client.create_payment_intent(
            amount=2000,  # Passed as dollars
            currency="usd",
            customer_id="cus_123",
            metadata={"invoice_id": "inv_123"},
        )

        assert result["payment_intent_id"] == "pi_123"
        assert result["client_secret"] == "client_secret_123"
        assert result["status"] == "requires_payment_method"
        assert result["amount"] == 2000.00

        # Verify amount was converted to cents (multiply by 100)
        call_kwargs = mock_pi_class.create.call_args[1]
        assert call_kwargs["amount"] == 200000  # 2000 * 100
        assert call_kwargs["currency"] == "usd"  # Lowercased
        assert call_kwargs["customer"] == "cus_123"
        assert call_kwargs["metadata"] == {"invoice_id": "inv_123"}

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_create_payment_intent_without_customer(self, mock_pi_class):
        """Test creating payment intent without customer."""
        mock_pi = Mock()
        mock_pi.id = "pi_456"
        mock_pi.client_secret = "secret_456"
        mock_pi.status = "succeeded"
        mock_pi.amount = 100000
        mock_pi.currency = "usd"

        mock_pi_class.create.return_value = mock_pi

        client = StripeClient(api_key="sk_test")
        result = client.create_payment_intent(amount=1000, currency="usd")

        call_kwargs = mock_pi_class.create.call_args[1]
        assert "customer" not in call_kwargs or call_kwargs.get("customer") is None
        assert call_kwargs["amount"] == 100000

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_create_payment_intent_error(self, mock_pi_class):
        """Test payment intent creation failure."""
        mock_pi_class.create.side_effect = Exception("Card declined")

        client = StripeClient(api_key="sk_test")

        with pytest.raises(StripeError, match="Failed to create payment intent"):
            client.create_payment_intent(amount=1000, currency="usd")

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_create_payment_intent_amount_conversion(self, mock_pi_class):
        """Test that amount is correctly converted to cents."""
        mock_pi = Mock()
        mock_pi.id = "pi_test"
        mock_pi.client_secret = "secret"
        mock_pi.status = "pending"
        mock_pi.amount = 0  # Will be set from input
        mock_pi.currency = "usd"

        mock_pi_class.create.return_value = mock_pi

        client = StripeClient(api_key="sk_test")

        # Test with non-integer amount
        result = client.create_payment_intent(amount=1234.56, currency="usd")

        call_kwargs = mock_pi_class.create.call_args[1]
        # Should be 123456 (1234.56 * 100)
        assert call_kwargs["amount"] == 123456

    @patch("src.integrations.stripe_client.stripe.PaymentIntent")
    def test_create_payment_intent_currency_lowercase(self, mock_pi_class):
        """Test that currency is lowercased."""
        mock_pi = Mock()
        mock_pi.id = "pi_cur"
        mock_pi.client_secret = "sec"
        mock_pi.status = "pending"
        mock_pi.currency = "usd"
        mock_pi.amount = 100

        mock_pi_class.create.return_value = mock_pi

        client = StripeClient(api_key="sk_test")
        result = client.create_payment_intent(amount=1, currency="USD")

        call_kwargs = mock_pi_class.create.call_args[1]
        assert call_kwargs["currency"] == "usd"


class TestUpdateInvoice:
    """Test invoice update functionality."""

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_update_invoice_success(self, mock_invoice_class):
        """Test updating an invoice."""
        mock_invoice = Mock()
        mock_invoice.id = "in_123"
        mock_invoice.status = "open"
        mock_invoice.metadata = {"updated": "true"}
        mock_invoice.date_updated = datetime.now().timestamp()

        mock_invoice_class.modify.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.update_invoice(
            "in_123",
            metadata={"note": "updated via API"},
            due_date=datetime.now() + timedelta(days=7),
        )

        assert result["invoice_id"] == "in_123"
        assert result["metadata"] == {"updated": "true"}

        mock_invoice_class.modify.assert_called_once_with(
            "in_123",
            metadata={"note": "updated via API"},
            due_date=pytest.ANY,  # We don't need to check exact value
        )

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_update_invoice_error(self, mock_invoice_class):
        """Test update invoice failure."""
        mock_invoice_class.modify.side_effect = Exception("Update failed")

        client = StripeClient(api_key="sk_test")

        with pytest.raises(StripeError, match="Failed to update invoice"):
            client.update_invoice("in_123", metadata={})

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_update_invoice_with_multiple_fields(self, mock_invoice_class):
        """Test updating multiple invoice fields."""
        mock_invoice = Mock()
        mock_invoice.id = "in_456"
        mock_invoice.status = "draft"
        mock_invoice.metadata = {}
        mock_invoice.date_updated = datetime.now().timestamp()

        mock_invoice_class.modify.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.update_invoice(
            "in_456",
            metadata={"campaign": "summer_2024"},
            description="Updated description",
            custom_fields=[{"name": "Department", "value": "Sales"}],
        )

        mock_invoice_class.modify.assert_called_once()
        # Verify the update included all provided fields
        call_kwargs = mock_invoice_class.modify.call_args[1]
        assert "metadata" in call_kwargs
        assert "description" in call_kwargs
        assert "custom_fields" in call_kwargs


class TestStripeClientEdgeCases:
    """Test edge cases and error conditions."""

    def test_amount_conversion_precision(self):
        """Test that amount conversion maintains precision."""
        client = StripeClient(api_key="sk_test")

        test_cases = [
            (10.00, 1000),
            (10.01, 1001),
            (999.99, 99999),
            (0.01, 1),
            (1234.56, 123456),
        ]

        for dollars, expected_cents in test_cases:
            with patch(
                "src.integrations.stripe_client.stripe.PaymentIntent"
            ) as mock_pi:
                mock_pi_instance = Mock()
                mock_pi_instance.id = "pi_test"
                mock_pi_instance.client_secret = "test"
                mock_pi_instance.status = "pending"
                mock_pi_instance.amount = expected_cents
                mock_pi_instance.currency = "usd"
                mock_pi.create.return_value = mock_pi_instance

                result = client.create_payment_intent(amount=dollars, currency="usd")
                # The internal conversion should match expected_cents
                call_kwargs = mock_pi.create.call_args[1]
                assert call_kwargs["amount"] == expected_cents

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_due_date_none(self, mock_invoice_class):
        """Test invoice with no due date."""
        mock_invoice = Mock()
        mock_invoice.status = "draft"
        mock_invoice.amount_paid = 0
        mock_invoice.currency = "usd"
        mock_invoice.due_date = None
        mock_invoice.status_transitions = Mock()
        mock_invoice.status_transitions.paid_at = None
        mock_invoice.number = "INV-001"
        mock_invoice.customer_email = "test@example.com"
        mock_invoice.id = "in_123"

        mock_invoice_class.retrieve.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("in_123")

        assert result["due_date"] is None

    @patch("src.integrations.stripe_client.stripe.Invoice")
    def test_get_invoice_status_no_paid_date(self, mock_invoice_class):
        """Test invoice with no paid date in status_transitions."""
        mock_invoice = Mock()
        mock_invoice.status = "open"
        mock_invoice.amount_paid = 0
        mock_invoice.currency = "usd"
        mock_invoice.due_date = datetime.now().timestamp()
        mock_invoice.status_transitions = Mock()
        # No paid_at attribute or is None
        mock_invoice.status_transitions.paid_at = None
        mock_invoice.number = "INV-001"
        mock_invoice.customer_email = "test@example.com"
        mock_invoice.id = "in_123"

        mock_invoice_class.retrieve.return_value = mock_invoice

        client = StripeClient(api_key="sk_test")
        result = client.get_invoice_status("in_123")

        assert "paid_date" in result
        assert result["paid_date"] is None
