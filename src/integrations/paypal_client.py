"""
PayPal API client for transaction and dispute management.

Provides functions to connect to PayPal, retrieve transactions,
handle disputes, and manage payments with proper error handling.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import paypalrestsdk
from paypalrestsdk import ResourceNotFound, PayPalRESTException

from ..core.config import settings

logger = logging.getLogger(__name__)


class PayPalError(Exception):
    """Custom exception for PayPal API errors."""

    pass


class PayPalClient:
    """Client for PayPal API operations."""

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ):
        """Initialize PayPal client with credentials from settings if not provided."""
        self.client_id = client_id or settings.paypal_client_id
        self.client_secret = client_secret or settings.paypal_client_secret
        self.mode = (
            "live"
            if settings.paypal_client_id
            and not settings.paypal_client_id.endswith(".sandbox")
            else "sandbox"
        )

        if not self.client_id or not self.client_secret:
            raise PayPalError("PayPal credentials not configured")

        paypalrestsdk.configure(
            {
                "mode": self.mode,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )
        self._client = paypalrestsdk

    def connect_account(self, authorization_code: str) -> Dict[str, Any]:
        """
        Connect a PayPal account via OAuth authorization code.

        Args:
            authorization_code: OAuth authorization code from PayPal

        Returns:
            Dict with account details including access_token and refresh_token
        """
        try:
            response = paypalrestsdk.OAuthToken.create(
                grant_type="authorization_code", code=authorization_code
            )
            account_info = {
                "access_token": response.get("access_token"),
                "refresh_token": response.get("refresh_token"),
                "token_type": response.get("token_type"),
                "expires_in": response.get("expires_in"),
                "account_id": response.get("payer", {})
                .get("payer_info", {})
                .get("payer_id"),
                "email": response.get("payer", {}).get("payer_info", {}).get("email"),
            }
            logger.info(f"PayPal account connected: {account_info.get('account_id')}")
            return account_info
        except PayPalRESTException as e:
            logger.error(f"PayPal OAuth connection failed: {e}")
            raise PayPalError(f"Failed to connect PayPal account: {str(e)}")

    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """
        Retrieve invoice/payment status from PayPal.

        Args:
            invoice_id: PayPal transaction ID or invoice ID

        Returns:
            Dict with payment/details including status, amount, payer info
        """
        try:
            # Try as payment first
            payment = paypalrestsdk.Payment.find(invoice_id)
            transaction = payment.transactions[0] if payment.transactions else {}

            return {
                "status": payment.state,
                "amount": float(transaction.amount.total)
                if transaction.amount
                else 0.0,
                "currency": transaction.amount.currency
                if transaction.amount
                else "USD",
                "payer_email": transaction.payer.payer_info.email
                if transaction.payer
                else None,
                "payer_id": transaction.payer.payer_info.payer_id
                if transaction.payer
                else None,
                "payment_time": datetime.strptime(
                    transaction.create_time, "%Y-%m-%dT%H:%M:%SZ"
                )
                if transaction.create_time
                else None,
                "paypal_txn_id": payment.id,
                "intent": payment.intent,
            }
        except ResourceNotFound:
            # Try as invoice
            try:
                invoice = paypalrestsdk.Invoice.find(invoice_id)
                return {
                    "status": invoice.status,
                    "amount": float(invoice.amount.value) if invoice.amount else 0.0,
                    "currency": invoice.amount.currency if invoice.amount else "USD",
                    "payer_email": invoice.billing_info[0].email
                    if invoice.billing_info
                    else None,
                    "invoice_number": invoice.invoice_number,
                    "paypal_invoice_id": invoice.id,
                    "issue_date": datetime.strptime(
                        invoice.issue_date, "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if invoice.issue_date
                    else None,
                    "due_date": datetime.strptime(
                        invoice.due_date, "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if invoice.due_date
                    else None,
                }
            except ResourceNotFound:
                raise PayPalError(f"PayPal resource not found: {invoice_id}")
            except PayPalRESTException as e:
                logger.error(f"Failed to retrieve PayPal invoice {invoice_id}: {e}")
                raise PayPalError(f"Failed to retrieve invoice: {str(e)}")
        except PayPalRESTException as e:
            logger.error(f"Failed to retrieve PayPal payment {invoice_id}: {e}")
            raise PayPalError(f"Failed to retrieve payment: {str(e)}")

    def list_transactions(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List transactions for a PayPal account.

        Args:
            account_id: PayPal account ID (not used in standard SDK)
            start_date: Filter transactions after this date
            end_date: Filter transactions before this date
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries with details
        """
        try:
            # Build search parameters
            params = {}
            if start_date:
                params["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            if end_date:
                params["end_date"] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            # PayPal doesn't have a direct transaction list in REST API v1
            # We'll search via Payment API
            search_params = {"count": limit, **params}

            payments = paypalrestsdk.Payment.all(**search_params)
            transactions = []

            for payment in payments.payments:
                if payment.transactions:
                    txn = payment.transactions[0]
                    transaction = {
                        "id": payment.id,
                        "amount": float(txn.amount.total) if txn.amount else 0.0,
                        "currency": txn.amount.currency if txn.amount else "USD",
                        "status": payment.state,
                        "created": datetime.strptime(
                            payment.create_time, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        if payment.create_time
                        else None,
                        "payer_email": txn.payer.payer_info.email
                        if txn.payer
                        else None,
                        "payer_id": txn.payer.payer_info.payer_id
                        if txn.payer
                        else None,
                        "description": txn.description,
                        "intent": payment.intent,
                    }
                    transactions.append(transaction)

            logger.info(f"Retrieved {len(transactions)} PayPal transactions")
            return transactions
        except PayPalRESTException as e:
            logger.error(f"Failed to list PayPal transactions: {e}")
            raise PayPalError(f"Failed to list transactions: {str(e)}")

    def create_dispute(
        self, transaction_id: str, reason: str, description: str
    ) -> Dict[str, Any]:
        """
        Create a dispute/chargeback for a transaction.

        Args:
            transaction_id: PayPal payment/transaction ID
            reason: Dispute reason (e.g., 'unauthorized', 'item_not_received')
            description: Detailed description of the dispute

        Returns:
            Dict with dispute details
        """
        try:
            dispute = paypalrestsdk.Dispute.create(
                transaction_id=transaction_id, reason=reason, description=description
            )
            logger.info(f"Created PayPal dispute: {dispute.id}")
            return {
                "dispute_id": dispute.id,
                "status": dispute.status,
                "reason": dispute.reason,
                "transaction_id": transaction_id,
                "created_time": datetime.now(),
            }
        except PayPalRESTException as e:
            logger.error(f"Failed to create PayPal dispute: {e}")
            raise PayPalError(f"Failed to create dispute: {str(e)}")

    def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """
        Retrieve dispute details from PayPal.

        Args:
            dispute_id: PayPal dispute ID

        Returns:
            Dict with dispute status and details
        """
        try:
            dispute = paypalrestsdk.Dispute.find(dispute_id)
            return {
                "dispute_id": dispute.id,
                "status": dispute.status,
                "reason": dispute.reason,
                "transaction_id": dispute.transaction_id,
                "created_time": datetime.strptime(
                    dispute.create_time, "%Y-%m-%dT%H:%M:%SZ"
                )
                if dispute.create_time
                else None,
                "dispute_amount": float(dispute.dispute_amount.value)
                if dispute.dispute_amount
                else 0.0,
                "dispute_currency": dispute.dispute_amount.currency
                if dispute.dispute_amount
                else "USD",
            }
        except PayPalRESTException as e:
            logger.error(f"Failed to retrieve PayPal dispute {dispute_id}: {e}")
            raise PayPalError(f"Failed to retrieve dispute: {str(e)}")

    def update_dispute(self, dispute_id: str, **updates) -> Dict[str, Any]:
        """
        Update a dispute with evidence or notes.

        Args:
            dispute_id: PayPal dispute ID
            **updates: Fields to update (e.g., evidence, message)

        Returns:
            Updated dispute dictionary
        """
        try:
            dispute = paypalrestsdk.Dispute.find(dispute_id)
            dispute.update(updates)
            logger.info(f"Updated PayPal dispute: {dispute_id}")
            return {
                "dispute_id": dispute.id,
                "status": dispute.status,
                "updated_at": datetime.now(),
            }
        except PayPalRESTException as e:
            logger.error(f"Failed to update PayPal dispute {dispute_id}: {e}")
            raise PayPalError(f"Failed to update dispute: {str(e)}")
