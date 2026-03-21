"""
Email automation module for invoice follow-up sequences.

This module provides email sending functionality with Jinja2 template rendering
and Celery task integration for automated follow-up campaigns.
"""

from .sender import (
    EmailSender,
    SendGridSender,
    SMTPSender,
    get_email_sender,
    send_followup_email,
)

__all__ = [
    "EmailSender",
    "SendGridSender",
    "SMTPSender",
    "get_email_sender",
    "send_followup_email",
]
