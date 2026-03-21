"""
Plaid API client for bank feed linking and transaction synchronization.

Provides functions to create link tokens, exchange public tokens for access tokens,
and sync bank transactions with proper error handling.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

try:
    import plaid
    from plaid.api import PlaidApi
    from plaid.exceptions import PlaidException
    from plaid.models import (
        LinkTokenCreateRequest,
        ItemPublicTokenExchangeRequest,
        TransactionsGetRequest,
        SandboxItemFireWebhookRequest,
    )
    from plaid.model_initializers import (
        LinkTokenCreateRequestUser,
        TransactionsGetRequestOptions,
    )

    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Plaid SDK not installed. Install with: pip install plaid-python")

from ..core.config import settings

logger = logging.getLogger(__name__)


class PlaidError(Exception):
    """Custom exception for Plaid API errors."""

    pass


class PlaidClient:
    """Client for Plaid API operations."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        """
        Initialize Plaid client with credentials from settings if not provided.

        Args:
            client_id: Plaid client ID
            secret: Plaid secret key
            environment: 'sandbox', 'development', or 'production'
        """
        if not PLAID_AVAILABLE:
            raise PlaidError(
                "Plaid SDK not installed. Install with: pip install plaid-python"
            )

        self.client_id = client_id or settings.plaid_client_id
        self.secret = secret or settings.plaid_secret
        self.environment = environment or settings.plaid_environment

        if not self.client_id or not self.secret:
            raise PlaidError("Plaid credentials not configured")

        # Configure Plaid client
        self._client = plaid.ApiClient(
            plaid.Configuration(
                host=self._get_host(self.environment),
                api_key={
                    "clientId": self.client_id,
                    "secret": self.secret,
                },
            )
        )
        self.api = PlaidApi(self._client)

    def _get_host(self, environment: str) -> str:
        """Get Plaid API host based on environment."""
        env_map = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        return env_map.get(environment.lower(), "https://sandbox.plaid.com")

    def connect_account(
        self, user_id: str, client_name: str = "Invoice Resolver"
    ) -> Dict[str, Any]:
        """
        Create a Plaid Link token for bank account connection.

        Args:
            user_id: Unique user identifier (for linking)
            client_name: Application name shown in Plaid Link

        Returns:
            Dict with link_token and expiration
        """
        try:
            request = LinkTokenCreateRequest(
                user_id=user_id,
                client_name=client_name,
                language="en",
                products=["transactions"],
                country_codes=["US"],
                webhook=None,
            )
            response = self.api.link_token_create(request)
            logger.info(f"Created Plaid link token for user {user_id}")
            return {
                "link_token": response.link_token,
                "expires_at": response.expiration,
                "request_id": response.request_id,
            }
        except PlaidException as e:
            logger.error(f"Failed to create Plaid link token: {e}")
            raise PlaidError(f"Failed to create link token: {str(e)}")

    def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        """
        Exchange public token for access token and item ID.

        Args:
            public_token: Public token from Plaid Link frontend

        Returns:
            Dict with access_token, item_id, and associated accounts
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.api.item_public_token_exchange(request)
            logger.info(f"Exchanged public token for item {response.item_id}")
            return {
                "access_token": response.access_token,
                "item_id": response.item_id,
            }
        except PlaidException as e:
            logger.error(f"Failed to exchange public token: {e}")
            raise PlaidError(f"Failed to exchange public token: {str(e)}")

    def list_transactions(
        self,
        access_token: str,
        item_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        count: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List transactions from a Plaid connected bank account.

        Args:
            access_token: Plaid access token for the item
            item_id: Plaid item ID (optional)
            start_date: Start date for transaction sync (defaults to 30 days ago)
            end_date: End date for transaction sync (defaults to today)
            count: Maximum number of transactions to return
            offset: Number of transactions to skip for pagination

        Returns:
            List of transaction dictionaries with details
        """
        try:
            # Default to last 30 days
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            options = TransactionsGetRequestOptions(count=count, offset=offset)
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                options=options,
            )
            response = self.api.transactions_get(request)

            transactions = []
            for txn in response.transactions:
                transaction = {
                    "transaction_id": txn.transaction_id,
                    "account_id": txn.account_id,
                    "amount": float(txn.amount),
                    "currency": txn.iso_currency_code or "USD",
                    "date": datetime.strptime(txn.date, "%Y-%m-%d")
                    if txn.date
                    else None,
                    "name": txn.name,
                    "merchant_name": txn.merchant_name,
                    "category": txn.category,
                    "category_id": txn.category_id,
                    "pending": txn.pending,
                    "payment_channel": txn.payment_channel,
                    "transaction_type": txn.transaction_type,
                }
                transactions.append(transaction)

            logger.info(f"Retrieved {len(transactions)} Plaid transactions")
            return transactions
        except PlaidException as e:
            logger.error(f"Failed to list Plaid transactions: {e}")
            raise PlaidError(f"Failed to list transactions: {str(e)}")

    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get all accounts associated with a Plaid item.

        Args:
            access_token: Plaid access token for the item

        Returns:
            List of account dictionaries with details
        """
        try:
            from plaid.model_initializers import AccountsGetRequest

            request = AccountsGetRequest(access_token=access_token)
            response = self.api.accounts_get(request)

            accounts = []
            for acct in response.accounts:
                account = {
                    "account_id": acct.account_id,
                    "name": acct.name,
                    "official_name": acct.official_name,
                    "type": acct.type,
                    "subtype": acct.subtype,
                    "mask": acct.mask,
                    "balances": {
                        "available": float(acct.balances.available)
                        if acct.balances.available
                        else None,
                        "current": float(acct.balances.current)
                        if acct.balances.current
                        else None,
                        "iso_currency": acct.balances.iso_currency_code,
                    },
                }
                accounts.append(account)

            logger.info(f"Retrieved {len(accounts)} Plaid accounts")
            return accounts
        except PlaidException as e:
            logger.error(f"Failed to get Plaid accounts: {e}")
            raise PlaidError(f"Failed to get accounts: {str(e)}")

    def create_link_token(
        self,
        user_id: str,
        client_user_id: str,
        products: List[str] = ["transactions"],
        country_codes: List[str] = ["US"],
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Create a Plaid Link token (alternative to connect_account).

        Args:
            user_id: Unique user identifier
            client_user_id: Client-side user identifier
            products: Plaid products to enable (e.g., ['transactions', 'auth'])
            country_codes: Country codes for institutions
            language: Language code

        Returns:
            Dict with link_token and expiration
        """
        try:
            user = LinkTokenCreateRequestUser(
                client_user_id=client_user_id, user_id=user_id
            )
            request = LinkTokenCreateRequest(
                user=user,
                client_name="Invoice Resolver",
                products=products,
                countries=country_codes,
                language=language,
                link_customization_name="default",
            )
            response = self.api.link_token_create(request)
            logger.info(f"Created Plaid link token for user {user_id}")
            return {
                "link_token": response.link_token,
                "expires_at": response.expiration,
                "request_id": response.request_id,
            }
        except PlaidException as e:
            logger.error(f"Failed to create Plaid link token: {e}")
            raise PlaidError(f"Failed to create link token: {str(e)}")

    def get_item_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get item metadata from Plaid.

        Args:
            access_token: Plaid access token

        Returns:
            Dict with item details (institution, status, etc.)
        """
        try:
            from plaid.model_initializers import ItemGetRequest

            request = ItemGetRequest(access_token=access_token)
            response = self.api.item_get(request)
            item = response.item
            return {
                "item_id": item.item_id,
                "institution_id": item.institution_id,
                "webhook": item.webhook,
                "available_products": item.available_products,
                "billed_products": item.billed_products,
                "consent_expired": item.consent_expired
                if hasattr(item, "consent_expired")
                else None,
            }
        except PlaidException as e:
            logger.error(f"Failed to get Plaid item info: {e}")
            raise PlaidError(f"Failed to get item info: {str(e)}")

    def refresh_transactions(
        self, access_token: str, item_id: str, days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Trigger a transaction refresh via webhook (sandbox only).

        Args:
            access_token: Plaid access token
            item_id: Plaid item ID
            days_back: Number of days to backfill

        Returns:
            Dict with webhook response status
        """
        if self.environment != "sandbox":
            raise PlaidError("Webhook refresh only available in sandbox environment")

        try:
            request = SandboxItemFireWebhookRequest(
                access_token=access_token,
                webhook_name="TRANSACTIONS",
                days_back=days_back,
            )
            response = self.api.sandbox_item_fire_webhook(request)
            logger.info(f"Triggered Plaid transaction refresh for item {item_id}")
            return {
                "item_id": item_id,
                "webhook_fired": True,
                "request_id": response.request_id,
            }
        except PlaidException as e:
            logger.error(f"Failed to fire Plaid webhook: {e}")
            raise PlaidError(f"Failed to refresh transactions: {str(e)}")
