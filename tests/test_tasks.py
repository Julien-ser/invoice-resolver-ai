"""
Tests for Celery background tasks.

This module tests:
- sync_invoice_status: Periodic task for syncing invoice status with payment providers
- send_followup_task: Task wrapper for sending individual follow-up emails
- process_followup_campaign: Task for processing campaign emails
- scheduled_followups: Scheduled task that triggers follow-up campaigns
"""

import pytest
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.tasks.sync import (
    sync_invoice_status,
    sync_invoice_stripe,
    sync_invoice_paypal,
    get_invoices_to_sync,
    StripeClient as SyncStripeClient,
    PayPalClient as SyncPayPalClient,
)
from src.tasks.email_tasks import (
    send_followup_task,
    process_followup_campaign,
    scheduled_followups,
)
from src.models import Invoice, User, PaymentConnection, Campaign, Template


class TestSyncTasks:
    """Tests for invoice sync tasks."""

    @patch("src.tasks.sync.StripeClient")
    @patch("src.tasks.sync.get_db_session")
    def test_sync_invoice_stripe_success(self, mock_get_db, mock_stripe_client_class):
        """Test syncing a single invoice with Stripe."""
        # Setup mock database session
        mock_db = Mock(spec=Session)
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.id = "inv_123"
        mock_invoice.status = "sent"
        mock_invoice.stripe_invoice_id = "in_123"
        mock_invoice.stripe_payment_intent_id = None

        # Setup mock Stripe client
        mock_stripe_client = Mock()
        mock_stripe_invoice = Mock()
        mock_stripe_invoice.status = "paid"
        mock_stripe_client.get_invoice.return_value = mock_stripe_invoice
        mock_stripe_client.map_status_to_invoice_status.return_value = "paid"
        mock_stripe_client_class.return_value = mock_stripe_client

        # Run sync
        result = sync_invoice_stripe(mock_db, mock_invoice, mock_stripe_client)

        assert result is True
        assert mock_invoice.status == "paid"
        mock_db.commit.assert_called_once()

    @patch("src.tasks.sync.StripeClient")
    @patch("src.tasks.sync.get_db_session")
    def test_sync_invoice_stripe_no_change(self, mock_get_db, mock_stripe_client_class):
        """Test sync when Stripe status matches current status."""
        mock_db = Mock(spec=Session)
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.id = "inv_123"
        mock_invoice.status = "paid"
        mock_invoice.stripe_invoice_id = "in_123"

        mock_stripe_client = Mock()
        mock_stripe_invoice = Mock()
        mock_stripe_invoice.status = "paid"
        mock_stripe_client.get_invoice.return_value = mock_stripe_invoice
        mock_stripe_client.map_status_to_invoice_status.return_value = "paid"
        mock_stripe_client_class.return_value = mock_stripe_client

        result = sync_invoice_stripe(mock_db, mock_invoice, mock_stripe_client)

        assert result is False
        mock_db.commit.assert_not_called()

    @patch("src.tasks.sync.PayPalClient")
    @patch("src.tasks.sync.get_db_session")
    def test_sync_invoice_paypal_success(self, mock_get_db, mock_paypal_client_class):
        """Test syncing a single invoice with PayPal."""
        mock_db = Mock(spec=Session)
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.id = "inv_123"
        mock_invoice.status = "sent"
        mock_invoice.paypal_txn_id = "PAY_123"

        mock_paypal_client = Mock()
        mock_transaction = Mock()
        mock_transaction.to_dict.return_value = {"state": "approved"}
        mock_paypal_client.get_transaction.return_value = mock_transaction
        mock_paypal_client.map_status_to_invoice_status.return_value = "paid"
        mock_paypal_client_class.return_value = mock_paypal_client

        result = sync_invoice_paypal(mock_db, mock_invoice, mock_paypal_client)

        assert result is True
        assert mock_invoice.status == "paid"
        mock_db.commit.assert_called_once()

    @patch("src.tasks.sync.get_db_session")
    def test_get_invoices_to_sync(self, mock_get_db):
        """Test fetching invoices that need syncing."""
        mock_db = Mock(spec=Session)
        mock_invoices = [Mock(), Mock()]
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = mock_invoices

        result = get_invoices_to_sync(mock_db, limit=50)

        assert result == mock_invoices
        mock_db.query.assert_called_once()

    @patch("src.tasks.sync.StripeClient")
    @patch("src.tasks.sync.PayPalClient")
    @patch("src.tasks.sync.get_invoices_to_sync")
    @patch("src.tasks.sync.get_db_session")
    def test_sync_invoice_status_full_success(
        self, mock_get_db, mock_get_invoices, mock_paypal_class, mock_stripe_class
    ):
        """Test full sync task with successful updates."""
        # Setup database session
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db

        # Setup invoices to sync
        mock_user = Mock(spec=User)
        mock_user.id = "user_123"
        mock_user.payment_connections = []
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.id = "inv_123"
        mock_invoice.status = "sent"
        mock_invoice.stripe_invoice_id = "in_123"
        mock_invoice.stripe_payment_intent_id = None
        mock_invoice.paypal_txn_id = None
        mock_invoice.paypal_invoice_id = None
        mock_invoice.user_id = "user_123"
        mock_get_invoices.return_value = [mock_invoice]

        # Mock user query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock Stripe client
        mock_stripe_client = Mock()
        mock_stripe_invoice = Mock()
        mock_stripe_invoice.status = "paid"
        mock_stripe_client.get_invoice.return_value = mock_stripe_invoice
        mock_stripe_client.map_status_to_invoice_status.return_value = "paid"
        mock_stripe_class.return_value = mock_stripe_client

        # Run sync task
        sync_invoice_status()

        # Verify invoice was updated
        assert mock_invoice.status == "paid"
        mock_db.commit.assert_called()
        mock_db.close.assert_called_once()

    @patch("src.tasks.sync.get_db_session")
    def test_sync_invoice_status_with_exception(self, mock_get_db):
        """Test sync task handles exceptions gracefully."""
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []

        # Should complete without raising
        sync_invoice_status()
        mock_db.close.assert_called_once()


class TestEmailTasks:
    """Tests for email Celery tasks."""

    @patch("src.tasks.email_tasks.send_followup_email")
    @patch("src.tasks.email_tasks.next")
    def test_send_followup_task_success(self, mock_next, mock_send_email):
        """Test send follow-up task wrapper."""
        # Mock database session
        mock_db = Mock()
        mock_next.return_value = mock_db

        # Mock successful send
        mock_campaign = Mock()
        mock_send_email.return_value = mock_campaign

        result = send_followup_task("inv_123", "follow_up_3_day")

        assert result is True
        mock_send_email.assert_called_once_with(
            invoice_id="inv_123", template_type="follow_up_3_day", db=mock_db
        )
        mock_db.close.assert_called_once()

    @patch("src.tasks.email_tasks.send_followup_email")
    @patch("src.tasks.email_tasks.next")
    def test_send_followup_task_failure(self, mock_next, mock_send_email):
        """Test send follow-up task handles exceptions."""
        mock_db = Mock()
        mock_next.return_value = mock_db
        mock_send_email.side_effect = Exception("Send failed")

        result = send_followup_task("inv_123", "follow_up_3_day")

        assert result is False
        mock_db.close.assert_called_once()

    @patch("src.tasks.email_tasks.send_followup_task")
    @patch("src.tasks.email_tasks.db")
    def test_process_followup_campaign(self, mock_db_module, mock_send_task):
        """Test processing follow-up campaign."""
        # Setup database mock
        mock_db = Mock(spec=Session)
        mock_db_module.return_value.__enter__ = Mock(return_value=mock_db)
        mock_db_module.return_value.__exit__ = Mock(return_value=False)

        # Mock invoice and user
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.id = "inv_123"
        mock_invoice.client_email = "client@example.com"
        mock_invoice.due_date = datetime.utcnow() - timedelta(days=7)
        mock_user = Mock(spec=User)
        mock_user.id = "user_123"
        mock_user.email_notifications_enabled = True
        mock_user.is_active = True

        # Mock query result
        mock_db.execute.return_value.all.return_value = [(mock_invoice, mock_user)]
        # No existing campaign
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        # Mock send task delay
        mock_send_task.delay = Mock(return_value=None)

        # Execute campaign processing
        sent_count = process_followup_campaign(7, "follow_up_7_day")

        assert sent_count == 1
        mock_send_task.delay.assert_called_once_with("inv_123", "follow_up_7_day")
        mock_db.execute.assert_called()
        mock_db.close.assert_called()

    @patch("src.tasks.email_tasks.process_followup_campaign")
    def test_scheduled_followups(self, mock_process_campaign):
        """Test scheduled follow-ups task."""
        # Mock campaign counts
        mock_process_campaign.side_effect = [5, 3, 1]

        result = scheduled_followups()

        assert result == {
            "follow_up_3_day": 5,
            "follow_up_7_day": 3,
            "follow_up_14_day": 1,
        }
        assert mock_process_campaign.call_count == 3

        # Verify each campaign type was called with correct parameters
        expected_calls = [
            call(3, "follow_up_3_day"),
            call(7, "follow_up_7_day"),
            call(14, "follow_up_14_day"),
        ]
        mock_process_campaign.assert_has_calls(expected_calls)

    @patch("src.tasks.email_tasks.process_followup_campaign")
    def test_scheduled_followups_with_exception(self, mock_process_campaign):
        """Test scheduled follow-ups handles exceptions gracefully."""
        mock_process_campaign.side_effect = Exception("Task failed")

        result = scheduled_followups()

        # Should return empty counts on total failure
        assert result == {
            "follow_up_3_day": 0,
            "follow_up_7_day": 0,
            "follow_up_14_day": 0,
        }
