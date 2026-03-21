"""
Background task for invoice status synchronization.

This module provides periodic synchronization of invoice status with payment providers
(Stripe, PayPal) as a fallback mechanism when webhooks fail or miss events.

The sync task runs every 15 minutes and:
- Finds invoices in 'sent' or 'overdue' status with payment provider IDs
- Queries Stripe/PayPal APIs to get current payment status
- Updates invoice status based on provider response
- Logs sync metrics for monitoring
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.logger import get_logger
from src.models import Invoice, User, PaymentConnection

# Configure logging
logger = get_logger(__name__)

# Import payment provider SDKs
try:
    import stripe

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe SDK not available, Stripe sync will be disabled")

try:
    import paypalrestsdk

    PAYPAL_AVAILABLE = False  # Will be set True after checking config
except ImportError:
    PAYPAL_AVAILABLE = False
    logger.warning("PayPal SDK not available, PayPal sync will be disabled")


# ========== Database Setup ==========


def get_db_session() -> Session:
    """Create a new database session for Celery tasks."""
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


# ========== Payment Provider Clients ==========


class StripeClient:
    """Stripe API client for invoice status checks."""

    def __init__(self, api_key: str):
        if not STRIPE_AVAILABLE:
            raise RuntimeError("Stripe SDK not installed")
        stripe.api_key = api_key
        self.stripe = stripe

    def get_invoice(self, stripe_invoice_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve invoice from Stripe."""
        try:
            invoice = self.stripe.Invoice.retrieve(stripe_invoice_id)
            return invoice
        except self.stripe.error.InvalidRequestError as e:
            logger.warning(f"Stripe invoice {stripe_invoice_id} not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Stripe invoice {stripe_invoice_id}: {e}")
            return None

    def get_payment_intent(self, payment_intent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve payment intent from Stripe."""
        try:
            pi = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return pi
        except self.stripe.error.InvalidRequestError as e:
            logger.warning(f"Stripe payment intent {payment_intent_id} not found: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Error fetching Stripe payment intent {payment_intent_id}: {e}"
            )
            return None

    def map_status_to_invoice_status(
        self, stripe_status: str, invoice_status: Optional[str] = None
    ) -> str:
        """
        Map Stripe status to our invoice status.

        Stripe Invoice statuses: draft, open, paid, uncollectible, void
        Stripe PaymentIntent statuses: requires_payment_method, requires_confirmation, requires_action,
                                        processing, requires_capture, canceled, succeeded, open
        """
        status_map = {
            "paid": "paid",
            "succeeded": "paid",
            "open": "overdue",
            "uncollectible": "overdue",
            "void": "canceled",
            "canceled": "canceled",
            "processing": "sent",
            "requires_action": "sent",
            "requires_capture": "sent",
            "requires_payment_method": "draft",
            "requires_confirmation": "draft",
        }

        # Prefer invoice status if available, otherwise use payment intent status
        if invoice_status:
            return status_map.get(invoice_status, "sent")
        return status_map.get(stripe_status, "sent")


class PayPalClient:
    """PayPal API client for transaction status checks."""

    def __init__(self, client_id: str, client_secret: str):
        if not PAYPAL_AVAILABLE:
            raise RuntimeError("PayPal SDK not installed")
        # Initialize PayPal SDK (mode should come from settings)
        paypalrestsdk.configure(
            {
                "mode": settings.plaid_environment
                if hasattr(settings, "plaid_environment")
                else "sandbox",
                "client_id": client_id,
                "client_secret": client_secret,
            }
        )
        self.paypal = paypalrestsdk

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve transaction from PayPal."""
        try:
            txn = self.paypal.Payment.find(txn_id)
            return txn.to_dict() if txn else None
        except self.paypal.ResourceNotFound as e:
            logger.warning(f"PayPal transaction {txn_id} not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching PayPal transaction {txn_id}: {e}")
            return None

    def map_status_to_invoice_status(self, paypal_status: str) -> str:
        """
        Map PayPal payment status to our invoice status.

        PayPal payment statuses: created, approved, pending, denied, expired, failed, canceled
        """
        status_map = {
            "approved": "paid",
            "completed": "paid",
            "pending": "sent",
            "created": "draft",
            "denied": "overdue",
            "failed": "overdue",
            "expired": "canceled",
            "canceled": "canceled",
        }
        return status_map.get(paypal_status.lower() if paypal_status else "", "sent")


# ========== Sync Logic ==========


def get_invoices_to_sync(db: Session, limit: int = 100) -> List[Invoice]:
    """
    Fetch invoices that need status synchronization.

    Includes invoices that:
    - Are in 'sent' or 'overdue' status
    - Have at least one payment provider ID attached
    - Haven't been updated in the last 1 hour (to avoid excessive API calls)
    """
    one_hour_ago = datetime.now(timezone.utc).replace(
        hour=datetime.now(timezone.utc).hour - 1
    )

    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.status.in_(["sent", "overdue"]),
            (
                Invoice.stripe_payment_intent_id.isnot(None)
                | Invoice.stripe_invoice_id.isnot(None)
                | Invoice.paypal_txn_id.isnot(None)
                | Invoice.paypal_invoice_id.isnot(None)
            ),
            Invoice.updated_at < one_hour_ago,
        )
        .limit(limit)
        .all()
    )

    logger.info(f"Found {len(invoices)} invoices to sync")
    return invoices


def sync_invoice_stripe(
    db: Session, invoice: Invoice, stripe_client: StripeClient
) -> bool:
    """
    Synchronize a single invoice with Stripe.

    Returns True if invoice was updated, False otherwise.
    """
    try:
        # Try to get invoice data if we have stripe_invoice_id
        stripe_invoice_data = None
        if invoice.stripe_invoice_id:
            stripe_invoice_data = stripe_client.get_invoice(invoice.stripe_invoice_id)

        # Try to get payment intent if we have payment_intent_id
        stripe_pi_data = None
        if invoice.stripe_payment_intent_id:
            stripe_pi_data = stripe_client.get_payment_intent(
                invoice.stripe_payment_intent_id
            )

        # Determine new status
        new_status = None
        if stripe_invoice_data:
            new_status = stripe_client.map_status_to_invoice_status(
                stripe_invoice_data.get("status"),
                invoice_status=stripe_invoice_data.get("status"),
            )
        elif stripe_pi_data:
            new_status = stripe_client.map_status_to_invoice_status(
                stripe_pi_data.get("status"), invoice_status=None
            )

        if new_status and new_status != invoice.status:
            old_status = invoice.status
            invoice.status = new_status
            db.commit()
            logger.info(
                f"Invoice {invoice.id} status updated from {old_status} to {new_status} via Stripe"
            )
            return True
        else:
            logger.debug(f"Invoice {invoice.id} status unchanged: {invoice.status}")
            return False

    except Exception as e:
        logger.error(f"Error syncing invoice {invoice.id} with Stripe: {e}")
        db.rollback()
        return False


def sync_invoice_paypal(
    db: Session, invoice: Invoice, paypal_client: PayPalClient
) -> bool:
    """
    Synchronize a single invoice with PayPal.

    Returns True if invoice was updated, False otherwise.
    """
    try:
        # Try to get transaction data if we have paypal_txn_id
        txn_data = None
        if invoice.paypal_txn_id:
            txn_data = paypal_client.get_transaction(invoice.paypal_txn_id)

        if not txn_data:
            logger.debug(f"No PayPal transaction data for invoice {invoice.id}")
            return False

        # Determine new status from transaction state
        transaction_state = txn_data.get("state", "").lower()
        new_status = paypal_client.map_status_to_invoice_status(transaction_state)

        if new_status and new_status != invoice.status:
            old_status = invoice.status
            invoice.status = new_status
            db.commit()
            logger.info(
                f"Invoice {invoice.id} status updated from {old_status} to {new_status} via PayPal"
            )
            return True
        else:
            logger.debug(f"Invoice {invoice.id} status unchanged: {invoice.status}")
            return False

    except Exception as e:
        logger.error(f"Error syncing invoice {invoice.id} with PayPal: {e}")
        db.rollback()
        return False


def sync_invoice_status():
    """
    Celery task: Synchronize invoice status with payment providers.

    This is the main periodic task that runs every 15 minutes. It:
    1. Fetches invoices that need syncing (sent/overdue with provider IDs)
    2. For each invoice, checks Stripe and/or PayPal depending on available IDs
    3. Updates invoice status based on provider response
    4. Records metrics and handles errors gracefully
    """
    logger.info("Starting invoice status synchronization")

    db = None
    try:
        db = get_db_session()

        # Initialize clients based on configuration
        stripe_client = None
        paypal_client = None

        if STRIPE_AVAILABLE and settings.stripe_api_key:
            try:
                stripe_client = StripeClient(settings.stripe_api_key)
                logger.debug("Stripe client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Stripe client: {e}")

        # PayPal client will be initialized per-user based on credentials
        # since each user may have different PayPal credentials
        logger.debug("PayPal client will be initialized per user")

        # Get invoices to sync
        invoices = get_invoices_to_sync(db, limit=100)
        synced_count = 0
        error_count = 0

        for invoice in invoices:
            try:
                # Get user's payment connections to find credentials
                user = db.query(User).filter(User.id == invoice.user_id).first()
                if not user or not user.payment_connections:
                    logger.debug(
                        f"No payment connections found for user {invoice.user_id}"
                    )
                    continue

                # Try Stripe sync if invoice has Stripe IDs
                if invoice.stripe_invoice_id or invoice.stripe_payment_intent_id:
                    if stripe_client:
                        updated = sync_invoice_stripe(db, invoice, stripe_client)
                        if updated:
                            synced_count += 1
                    else:
                        logger.debug(
                            "Stripe client not available, skipping Stripe sync"
                        )

                # Try PayPal sync if invoice has PayPal IDs
                if invoice.paypal_txn_id or invoice.paypal_invoice_id:
                    # Find active PayPal connection for this user
                    paypal_connection = next(
                        (
                            pc
                            for pc in user.payment_connections
                            if pc.provider == "paypal" and pc.is_active
                        ),
                        None,
                    )
                    if paypal_connection:
                        try:
                            # Decrypt credentials (simplified - proper decryption would be needed)
                            # In production, use proper encryption/decryption
                            import json

                            creds = json.loads(paypal_connection.credentials_encrypted)
                            client_id = creds.get("client_id")
                            client_secret = creds.get("client_secret")

                            if client_id and client_secret:
                                paypal_client = PayPalClient(client_id, client_secret)
                                updated = sync_invoice_paypal(
                                    db, invoice, paypal_client
                                )
                                if updated:
                                    synced_count += 1
                        except Exception as e:
                            logger.error(
                                f"Failed to initialize PayPal client for user {user.id}: {e}"
                            )
                    else:
                        logger.debug(f"No active PayPal connection for user {user.id}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error syncing invoice {invoice.id}: {e}")
                continue

        logger.info(
            f"Invoice sync completed: {synced_count} updated, {error_count} errors, "
            f"{len(invoices)} processed"
        )

        # Record system metric
        from src.models import SystemMetric

        metric = SystemMetric(
            metric_name="invoice_sync_completed",
            metric_value=1.0,
            labels={
                "synced_count": synced_count,
                "error_count": error_count,
                "processed_count": len(invoices),
            },
        )
        db.add(metric)
        db.commit()

    except Exception as e:
        logger.error(f"Fatal error in invoice sync task: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()


# For manual testing
if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    sync_invoice_status()
