"""
Stripe API client for invoice and payment management.

Provides functions to connect to Stripe, retrieve invoice status,
list transactions, and manage payment intents with proper error handling.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import stripe
from stripe import (
    StripeError as StripeLibError,
    RateLimitError,
    AuthenticationError,
)

from ..core.config import settings

logger = logging.getLogger(__name__)


class StripeError(Exception):
    """Custom exception for Stripe API errors."""

    pass


class StripeClient:
    """Client for Stripe API operations."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe client with API key from settings if not provided."""
        self.api_key = api_key or settings.stripe_api_key
        if not self.api_key:
            raise StripeError("Stripe API key not configured")
        stripe.api_key = self.api_key
        self._client = stripe

    def connect_account(self, authorization_code: str) -> Dict[str, Any]:
        """
        Connect a Stripe account via OAuth authorization code.

        Args:
            authorization_code: OAuth authorization code from Stripe Connect

        Returns:
            Dict with account details including account_id and user_id
        """
        try:
            response = stripe.OAuth.token(
                grant_type="authorization_code", code=authorization_code
            )
            logger.info(f"Stripe account connected: {response.get('stripe_user_id')}")
            return {
                "account_id": response.get("stripe_user_id"),
                "access_token": response.get("access_token"),
                "refresh_token": response.get("refresh_token"),
                "livemode": response.get("livemode", False),
            }
        except StripeLibError as e:
            logger.error(f"Stripe OAuth connection failed: {e}")
            raise StripeError(f"Failed to connect Stripe account: {str(e)}")

    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """
        Retrieve invoice status from Stripe.

        Args:
            invoice_id: Stripe invoice ID or payment intent ID

        Returns:
            Dict with invoice details including status, amount, due_date
        """
        try:
            # Try as invoice first
            if invoice_id.startswith("in_"):
                invoice = stripe.Invoice.retrieve(invoice_id)
                return {
                    "status": invoice.status,
                    "amount": invoice.amount_paid / 100.0,
                    "currency": invoice.currency,
                    "due_date": datetime.fromtimestamp(invoice.due_date)
                    if invoice.due_date
                    else None,
                    "paid_date": datetime.fromtimestamp(
                        invoice.status_transitions.paid_at
                    )
                    if invoice.status_transitions.paid_at
                    else None,
                    "invoice_number": invoice.number,
                    "customer_email": invoice.customer_email,
                    "stripe_invoice_id": invoice.id,
                }
            # Try as payment intent
            elif invoice_id.startswith("pi_"):
                payment_intent = stripe.PaymentIntent.retrieve(invoice_id)
                return {
                    "status": payment_intent.status,
                    "amount": payment_intent.amount / 100.0,
                    "currency": payment_intent.currency,
                    "created": datetime.fromtimestamp(payment_intent.created),
                    "customer": payment_intent.customer,
                    "payment_method": payment_intent.payment_method,
                    "stripe_payment_intent_id": payment_intent.id,
                }
            else:
                raise StripeError(f"Invalid Stripe ID format: {invoice_id}")
        except StripeLibError as e:
            logger.error(f"Failed to retrieve Stripe invoice {invoice_id}: {e}")
            raise StripeError(f"Failed to retrieve invoice: {str(e)}")

    def list_transactions(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List transactions for a Stripe account.

        Args:
            account_id: Stripe account ID (uses connected account if provided)
            start_date: Filter transactions after this date
            end_date: Filter transactions before this date
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries with details
        """
        try:
            params: Dict[str, Any] = {"limit": limit}
            created_filter = {}
            if start_date:
                created_filter["gte"] = int(start_date.timestamp())
            if end_date:
                created_filter["lte"] = int(end_date.timestamp())
            if created_filter:
                params["created"] = created_filter

            # Use expand to get more details
            params["expand"] = ["data.customer", "data.payment_intent"]

            if account_id:
                # Use Stripe Connect to access sub-account
                charges = stripe.Charge.list(**params, stripe_account=account_id)
            else:
                charges = stripe.Charge.list(**params)

            transactions = []
            for charge in charges.data:
                transaction = {
                    "id": charge.id,
                    "amount": charge.amount / 100.0,
                    "currency": charge.currency,
                    "status": charge.status,
                    "created": datetime.fromtimestamp(charge.created),
                    "customer_id": charge.customer.id if charge.customer else None,
                    "customer_email": charge.customer.email
                    if charge.customer
                    else None,
                    "payment_method": charge.payment_method,
                    "description": charge.description,
                    "failure_code": charge.failure_code,
                    "failure_message": charge.failure_message,
                }
                transactions.append(transaction)

            logger.info(f"Retrieved {len(transactions)} Stripe transactions")
            return transactions
        except StripeLibError as e:
            logger.error(f"Failed to list Stripe transactions: {e}")
            raise StripeError(f"Failed to list transactions: {str(e)}")

    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment intent in Stripe.

        Args:
            amount: Amount in currency units
            currency: Currency code (e.g., 'usd', 'eur')
            customer_id: Stripe customer ID
            metadata: Additional metadata to attach

        Returns:
            Dict with payment intent details
        """
        try:
            intent_data = {
                "amount": int(amount * 100),  # Convert to cents
                "currency": currency.lower(),
                "metadata": metadata or {},
            }
            if customer_id:
                intent_data["customer"] = customer_id

            payment_intent = stripe.PaymentIntent.create(**intent_data)
            logger.info(f"Created payment intent: {payment_intent.id}")
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status,
                "amount": payment_intent.amount / 100.0,
                "currency": payment_intent.currency,
            }
        except StripeLibError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise StripeError(f"Failed to create payment intent: {str(e)}")

    def update_invoice(self, invoice_id: str, **updates) -> Dict[str, Any]:
        """
        Update an invoice in Stripe.

        Args:
            invoice_id: Stripe invoice ID
            **updates: Fields to update (e.g., metadata, due_date)

        Returns:
            Updated invoice dictionary
        """
        try:
            invoice = stripe.Invoice.modify(invoice_id, **updates)
            logger.info(f"Updated Stripe invoice: {invoice_id}")
            return {
                "invoice_id": invoice.id,
                "status": invoice.status,
                "metadata": invoice.metadata,
                "updated_at": datetime.fromtimestamp(invoice.date_updated),
            }
        except StripeLibError as e:
            logger.error(f"Failed to update Stripe invoice {invoice_id}: {e}")
            raise StripeError(f"Failed to update invoice: {str(e)}")
