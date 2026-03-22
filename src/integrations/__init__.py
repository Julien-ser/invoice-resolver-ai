"""
Payment provider integration layer.

This package provides unified clients for Stripe, PayPal, and Plaid APIs
with consistent error handling and retry logic.
"""

from .stripe_client import StripeClient, StripeError
from .paypal_client import PayPalClient, PayPalError
from .plaid_client import PlaidClient, PlaidError

__all__ = [
    "StripeClient",
    "StripeError",
    "PayPalClient",
    "PayPalError",
    "PlaidClient",
    "PlaidError",
]
