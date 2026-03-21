"""
Tests for payment provider integration clients.

This module tests:
- StripeClient: connect_account, get_invoice_status, list_transactions, create_payment_intent, update_invoice
- PayPalClient: connect_account, get_invoice_status, list_transactions, create_dispute, get_dispute, update_dispute
- PlaidClient: connect_account, exchange_public_token, list_transactions, get_accounts, create_link_token, get_item_info, refresh_transactions
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
import json

from src.integrations.stripe_client import StripeClient, StripeError
from src.integrations.paypal_client import PayPalClient, PayPalError
from src.integrations.plaid_client import PlaidClient, PlaidError


class TestStripeClient:
    """Tests for StripeClient."""

    @patch("src.integrations.stripe_client.stripe")
    def test_init_with_api_key(self, mock_stripe):
        """Test initialization with provided API key."""
        client = StripeClient(api_key="sk_test_123")
        assert client.api_key == "sk_test_123"
        mock_stripe.api_key = "sk_test_123"

    @patch("src.integrations.stripe_client.stripe")
    def test_init_with_settings(self, mock_stripe, test_settings):
        """Test initialization using settings."""
        with patch("src.integrations.stripe_client.settings", test_settings):
            test_settings.stripe_api_key = "sk_test_from_settings"
            client = StripeClient()
            assert client.api_key == "sk_test_from_settings"

    @patch("src.integrations.stripe_client.stripe")
    def test_init_missing_api_key(self, mock_stripe):
        """Test initialization fails without API key."""
        with patch("src.integrations.stripe_client.settings") as mock_settings:
            mock_settings.stripe_api_key = None
            with pytest.raises(StripeError, match="Stripe API key not configured"):
                StripeClient()

    @patch("src.integrations.stripe_client.stripe")
    def test_connect_account_success(self, mock_stripe):
        """Test successful Stripe account connection."""
        mock_response = Mock()
        mock_response.get.side_effect = lambda key: {
            "stripe_user_id": "acct_123",
            "access_token": "access_123",
            "refresh_token": "refresh_123",
            "livemode": False,
        }.get(key)
        mock_stripe.OAuth.token.return_value = mock_response

        client = StripeClient(api_key="sk_test_123")
        result = client.connect_account("auth_code_123")

        assert result["account_id"] == "acct_123"
        assert result["access_token"] == "access_123"
        assert result["livemode"] is False
        mock_stripe.OAuth.token.assert_called_once_with(
            grant_type="authorization_code", code="auth_code_123"
        )

    @patch("src.integrations.stripe_client.stripe")
    def test_connect_account_failure(self, mock_stripe):
        """Test Stripe account connection failure."""
        mock_stripe.OAuth.token.side_effect = Exception("OAuth failed")

        client = StripeClient(api_key="sk_test_123")
        with pytest.raises(StripeError, match="Failed to connect Stripe account"):
            client.connect_account("bad_code")

    @patch("src.integrations.stripe_client.stripe")
    def test_get_invoice_status_by_invoice_id(self, mock_stripe):
        """Test retrieving invoice status by invoice ID."""
        mock_invoice = Mock()
        mock_invoice.status = "paid"
        mock_invoice.amount_paid = 1500
        mock_invoice.currency = "usd"
        mock_invoice.due_date = 1700000000
        mock_invoice.status_transitions.paid_at = 1700001000
        mock_invoice.number = "INV-001"
        mock_invoice.customer_email = "client@example.com"
        mock_invoice.id = "in_123"
        mock_stripe.Invoice.retrieve.return_value = mock_invoice

        client = StripeClient(api_key="sk_test_123")
        result = client.get_invoice_status("in_123")

        assert result["status"] == "paid"
        assert result["amount"] == 15.00
        assert result["currency"] == "usd"
        assert isinstance(result["due_date"], datetime)
        assert result["invoice_number"] == "INV-001"
        assert result["stripe_invoice_id"] == "in_123"

    @patch("src.integrations.stripe_client.stripe")
    def test_get_invoice_status_by_payment_intent(self, mock_stripe):
        """Test retrieving invoice status by payment intent ID."""
        mock_pi = Mock()
        mock_pi.status = "succeeded"
        mock_pi.amount = 2000
        mock_pi.currency = "usd"
        mock_pi.created = 1700000000
        mock_pi.customer = "cus_123"
        mock_pi.payment_method = "pm_123"
        mock_pi.id = "pi_123"
        mock_stripe.PaymentIntent.retrieve.return_value = mock_pi

        client = StripeClient(api_key="sk_test_123")
        result = client.get_invoice_status("pi_123")

        assert result["status"] == "succeeded"
        assert result["amount"] == 20.00
        assert result["stripe_payment_intent_id"] == "pi_123"

    @patch("src.integrations.stripe_client.stripe")
    def test_get_invoice_status_invalid_id(self, mock_stripe):
        """Test that invalid ID format raises error."""
        client = StripeClient(api_key="sk_test_123")
        with pytest.raises(StripeError, match="Invalid Stripe ID format"):
            client.get_invoice_status("invalid_id")

    @patch("src.integrations.stripe_client.stripe")
    def test_list_transactions_success(self, mock_stripe):
        """Test listing transactions successfully."""
        mock_charge = Mock()
        mock_charge.id = "ch_123"
        mock_charge.amount = 1000
        mock_charge.currency = "usd"
        mock_charge.status = "succeeded"
        mock_charge.created = 1700000000
        mock_customer = Mock()
        mock_customer.id = "cus_123"
        mock_customer.email = "customer@example.com"
        mock_charge.customer = mock_customer
        mock_charge.payment_method = "pm_123"
        mock_charge.description = "Test payment"
        mock_charge.failure_code = None
        mock_charge.failure_message = None

        mock_stripe.Charge.list.return_value = Mock(data=[mock_charge])

        client = StripeClient(api_key="sk_test_123")
        result = client.list_transactions(limit=10)

        assert len(result) == 1
        assert result[0]["id"] == "ch_123"
        assert result[0]["amount"] == 10.00
        assert result[0]["customer_email"] == "customer@example.com"

    @patch("src.integrations.stripe_client.stripe")
    def test_create_payment_intent(self, mock_stripe):
        """Test creating a payment intent."""
        mock_pi = Mock()
        mock_pi.id = "pi_123"
        mock_pi.client_secret = "secret_123"
        mock_pi.status = "requires_confirmation"
        mock_pi.amount = 5000
        mock_pi.currency = "usd"
        mock_stripe.PaymentIntent.create.return_value = mock_pi

        client = StripeClient(api_key="sk_test_123")
        result = client.create_payment_intent(
            amount=50.00,
            currency="usd",
            customer_id="cus_123",
            metadata={"key": "value"},
        )

        assert result["payment_intent_id"] == "pi_123"
        assert result["client_secret"] == "secret_123"
        assert result["status"] == "requires_confirmation"
        assert result["amount"] == 50.00
        mock_stripe.PaymentIntent.create.assert_called_once()

    @patch("src.integrations.stripe_client.stripe")
    def test_update_invoice(self, mock_stripe):
        """Test updating an invoice."""
        mock_invoice = Mock()
        mock_invoice.id = "in_123"
        mock_invoice.status = "open"
        mock_invoice.metadata = {"updated": "true"}
        mock_invoice.date_updated = 1700000000
        mock_stripe.Invoice.modify.return_value = mock_invoice

        client = StripeClient(api_key="sk_test_123")
        result = client.update_invoice("in_123", metadata={"updated": "true"})

        assert result["invoice_id"] == "in_123"
        assert result["status"] == "open"
        mock_stripe.Invoice.modify.assert_called_once_with(
            "in_123", metadata={"updated": "true"}
        )


class TestPayPalClient:
    """Tests for PayPalClient."""

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_init_with_credentials(self, mock_paypal):
        """Test initialization with provided credentials."""
        mock_paypal.configure.return_value = None
        client = PayPalClient(client_id="client_123", client_secret="secret_123")
        assert client.client_id == "client_123"
        assert client.client_secret == "secret_123"
        mock_paypal.configure.assert_called_once()

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_connect_account_success(self, mock_paypal):
        """Test successful PayPal account connection."""
        mock_response = {
            "access_token": "access_123",
            "refresh_token": "refresh_123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "payer": {
                "payer_info": {
                    "payer_id": "PAYER_123",
                    "email": "user@example.com",
                }
            },
        }
        mock_paypal.OAuthToken.create.return_value = mock_response

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.connect_account("auth_code_123")

        assert result["access_token"] == "access_123"
        assert result["account_id"] == "PAYER_123"
        assert result["email"] == "user@example.com"

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_get_invoice_status_by_payment(self, mock_paypal):
        """Test retrieving payment status from PayPal."""
        mock_payment = Mock()
        mock_payment.state = "approved"
        mock_transaction = Mock()
        mock_transaction.amount = Mock()
        mock_transaction.amount.total = "100.00"
        mock_transaction.amount.currency = "USD"
        payer_info = Mock()
        payer_info.email = "payer@example.com"
        payer_info.payer_id = "PAYER_456"
        mock_payer = Mock()
        mock_payer.payer_info = payer_info
        mock_transaction.payer = mock_payer
        mock_transaction.create_time = "2024-01-15T10:30:00Z"
        mock_payment.transactions = [mock_transaction]
        mock_payment.id = "PAY_123"
        mock_payment.intent = "sale"
        mock_paypal.Payment.find.return_value = mock_payment

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.get_invoice_status("PAY_123")

        assert result["status"] == "approved"
        assert result["amount"] == 100.00
        assert result["payer_email"] == "payer@example.com"
        assert result["paypal_txn_id"] == "PAY_123"

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_get_invoice_status_by_invoice(self, mock_paypal):
        """Test retrieving invoice status from PayPal."""
        # Payment not found, try invoice
        mock_payment = Mock()
        mock_payment.transactions = []
        mock_paypal.Payment.find.side_effect = [mock_payment, Mock()]

        mock_invoice = Mock()
        mock_invoice.status = "paid"
        mock_invoice.amount = Mock()
        mock_invoice.amount.value = "200.00"
        mock_invoice.amount.currency = "USD"
        billing = [Mock(email="billed@example.com")]
        mock_invoice.billing_info = billing
        mock_invoice.invoice_number = "INV-PAYPAL-001"
        mock_invoice.id = "INV_123"
        mock_invoice.issue_date = "2024-01-01T00:00:00Z"
        mock_invoice.due_date = "2024-01-15T00:00:00Z"
        mock_paypal.Invoice.find.return_value = mock_invoice

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.get_invoice_status("INV_123")

        assert result["status"] == "paid"
        assert result["amount"] == 200.00
        assert result["paypal_invoice_id"] == "INV_123"

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_list_transactions(self, mock_paypal):
        """Test listing PayPal transactions."""
        mock_payment = Mock()
        mock_payment.id = "PAY_001"
        mock_payment.state = "completed"
        mock_payment.create_time = "2024-01-15T10:00:00Z"
        mock_payment.intent = "sale"
        mock_transaction = Mock()
        mock_transaction.amount = Mock()
        mock_transaction.amount.total = "75.50"
        mock_transaction.amount.currency = "USD"
        payer_info = Mock()
        payer_info.email = "test@example.com"
        payer_info.payer_id = "PAYER_789"
        mock_payer = Mock()
        mock_payer.payer_info = payer_info
        mock_transaction.payer = mock_payer
        mock_transaction.description = "Test payment"
        mock_payment.transactions = [mock_transaction]

        mock_response = Mock()
        mock_response.payments = [mock_payment]
        mock_paypal.Payment.all.return_value = mock_response

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.list_transactions(limit=10)

        assert len(result) == 1
        assert result[0]["id"] == "PAY_001"
        assert result[0]["amount"] == 75.50
        assert result[0]["status"] == "completed"

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_create_dispute(self, mock_paypal):
        """Test creating a dispute."""
        mock_dispute = Mock()
        mock_dispute.id = "DPT_123"
        mock_dispute.status = "open"
        mock_dispute.reason = "item_not_received"
        mock_paypal.Dispute.create.return_value = mock_dispute

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.create_dispute(
                transaction_id="PAY_123", reason="item_not_received", description="Test"
            )

        assert result["dispute_id"] == "DPT_123"
        assert result["status"] == "open"
        assert result["reason"] == "item_not_received"

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_get_dispute(self, mock_paypal):
        """Test retrieving a dispute."""
        mock_dispute = Mock()
        mock_dispute.id = "DPT_123"
        mock_dispute.status = "resolved"
        mock_dispute.reason = "unauthorized"
        mock_dispute.transaction_id = "PAY_123"
        mock_dispute.create_time = "2024-01-15T10:00:00Z"
        dispute_amount = Mock()
        dispute_amount.value = "100.00"
        dispute_amount.currency = "USD"
        mock_dispute.dispute_amount = dispute_amount
        mock_paypal.Dispute.find.return_value = mock_dispute

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.get_dispute("DPT_123")

        assert result["dispute_id"] == "DPT_123"
        assert result["status"] == "resolved"
        assert result["dispute_amount"] == 100.00

    @patch("src.integrations.paypal_client.paypalrestsdk")
    def test_update_dispute(self, mock_paypal):
        """Test updating a dispute."""
        mock_dispute = Mock()
        mock_dispute.id = "DPT_123"
        mock_dispute.status = "open"
        mock_dispute.update.return_value = None
        mock_paypal.Dispute.find.return_value = mock_dispute

        with patch("src.integrations.paypal_client.paypalrestsdk", mock_paypal):
            client = PayPalClient(client_id="id", client_secret="secret")
            result = client.update_dispute("DPT_123", evidence={"key": "value"})

        assert result["dispute_id"] == "DPT_123"
        assert result["status"] == "open"


class TestPlaidClient:
    """Tests for PlaidClient."""

    @patch("src.integrations.plaid_client.plaid")
    def test_init_success(self, mock_plaid):
        """Test successful Plaid client initialization."""
        mock_plaid.ApiClient.return_value = Mock()
        mock_plaid.PlaidApi.return_value = Mock()

        with patch.dict("src.integrations.plaid_client.os.environ", {}, clear=True):
            with pytest.raises(PlaidError, match="Plaid credentials not configured"):
                PlaidClient()

    @patch("src.integrations.plaid_client.plaid")
    def test_connect_account(self, mock_plaid):
        """Test creating a Plaid link token."""
        mock_response = Mock()
        mock_response.link_token = "link_token_123"
        mock_response.expiration = "2024-01-16T00:00:00Z"
        mock_response.request_id = "req_123"
        mock_plaid.ApiClient.return_value = Mock()
        mock_api = Mock()
        mock_api.link_token_create.return_value = mock_response
        mock_plaid.PlaidApi.return_value = mock_api

        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {"PLAID_CLIENT_ID": "client_123", "PLAID_SECRET": "secret_123"},
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="sandbox"),
            ):
                client = PlaidClient()
                result = client.connect_account("user_123", "Test App")

        assert result["link_token"] == "link_token_123"
        assert result["request_id"] == "req_123"

    @patch("src.integrations.plaid_client.plaid")
    def test_exchange_public_token(self, mock_plaid):
        """Test exchanging public token for access token."""
        mock_response = Mock()
        mock_response.access_token = "access_token_123"
        mock_response.item_id = "item_123"
        mock_plaid.ApiClient.return_value = Mock()
        mock_api = Mock()
        mock_api.item_public_token_exchange.return_value = mock_response
        mock_plaid.PlaidApi.return_value = mock_api

        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {"PLAID_CLIENT_ID": "client_123", "PLAID_SECRET": "secret_123"},
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="sandbox"),
            ):
                client = PlaidClient()
                result = client.exchange_public_token("public_token_123")

        assert result["access_token"] == "access_token_123"
        assert result["item_id"] == "item_123"

    @patch("src.integrations.plaid_client.plaid")
    def test_list_transactions(self, mock_plaid):
        """Test listing transactions from Plaid."""
        mock_txn = Mock()
        mock_txn.transaction_id = "txn_123"
        mock_txn.account_id = "account_123"
        mock_txn.amount = 100.50
        mock_txn.iso_currency_code = "USD"
        mock_txn.date = "2024-01-15"
        mock_txn.name = "Test Merchant"
        mock_txn.merchant_name = "Test Merchant"
        mock_txn.category = ["Food and Drink", "Restaurants"]
        mock_txn.category_id = "13065000"
        mock_txn.pending = False
        mock_txn.payment_channel = "card"
        mock_txn.transaction_type = "purchase"

        mock_response = Mock()
        mock_response.transactions = [mock_txn]
        mock_plaid.ApiClient.return_value = Mock()
        mock_api = Mock()
        mock_api.transactions_get.return_value = mock_response
        mock_plaid.PlaidApi.return_value = mock_api

        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {"PLAID_CLIENT_ID": "client_123", "PLAID_SECRET": "secret_123"},
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="sandbox"),
            ):
                client = PlaidClient()
                result = client.list_transactions(access_token="access_token_123")

        assert len(result) == 1
        assert result[0]["transaction_id"] == "txn_123"
        assert result[0]["amount"] == 100.50
        assert result[0]["name"] == "Test Merchant"

    @patch("src.integrations.plaid_client.plaid")
    def test_get_accounts(self, mock_plaid):
        """Test getting accounts from Plaid."""
        mock_account = Mock()
        mock_account.account_id = "account_123"
        mock_account.name = "Checking Account"
        mock_account.official_name = "Plaid Checking"
        mock_account.type = "depository"
        mock_account.subtype = "checking"
        mock_account.mask = "1234"
        balances = Mock()
        balances.available = 1500.00
        balances.current = 1500.00
        balances.iso_currency_code = "USD"
        mock_account.balances = balances

        mock_response = Mock()
        mock_response.accounts = [mock_account]
        mock_plaid.ApiClient.return_value = Mock()
        mock_api = Mock()
        mock_api.accounts_get.return_value = mock_response
        mock_plaid.PlaidApi.return_value = mock_api

        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {"PLAID_CLIENT_ID": "client_123", "PLAID_SECRET": "secret_123"},
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="sandbox"),
            ):
                client = PlaidClient()
                result = client.get_accounts(access_token="access_token_123")

        assert len(result) == 1
        assert result[0]["account_id"] == "account_123"
        assert result[0]["name"] == "Checking Account"
        assert result[0]["balances"]["available"] == 1500.00

    @patch("src.integrations.plaid_client.plaid")
    def test_get_item_info(self, mock_plaid):
        """Test getting item info from Plaid."""
        mock_item = Mock()
        mock_item.item_id = "item_123"
        mock_item.institution_id = "ins_123"
        mock_item.webhook = "https://example.com/webhook"
        mock_item.available_products = ["transactions"]
        mock_item.billed_products = ["transactions"]

        mock_response = Mock()
        mock_response.item = mock_item
        mock_plaid.ApiClient.return_value = Mock()
        mock_api = Mock()
        mock_api.item_get.return_value = mock_response
        mock_plaid.PlaidApi.return_value = mock_api

        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {"PLAID_CLIENT_ID": "client_123", "PLAID_SECRET": "secret_123"},
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="sandbox"),
            ):
                from src.integrations.plaid_client import PlaidClient

                # Re-import ItemGetRequest inside function
                with patch(
                    "src.integrations.plaid_client.ItemGetRequest"
                ) as MockRequest:
                    client = PlaidClient()
                    result = client.get_item_info(access_token="access_token_123")

        assert result["item_id"] == "item_123"
        assert result["institution_id"] == "ins_123"

    @patch("src.integrations.plaid_client.plaid")
    def test_refresh_transactions_sandbox_only(self, mock_plaid):
        """Test that refresh_transactions only works in sandbox."""
        with patch.dict(
            "src.integrations.plaid_client.os.environ",
            {
                "PLAID_CLIENT_ID": "client_123",
                "PLAID_SECRET": "secret_123",
                "PLAID_ENVIRONMENT": "production",
            },
            clear=True,
        ):
            with patch(
                "src.integrations.plaid_client.settings",
                Mock(plaid_environment="production"),
            ):
                with pytest.raises(
                    PlaidError,
                    match="Webhook refresh only available in sandbox environment",
                ):
                    PlaidClient().refresh_transactions("access_token", "item_123")
