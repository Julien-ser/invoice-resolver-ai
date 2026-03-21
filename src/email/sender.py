"""
Email sender implementations for follow-up campaigns.

Supports SMTP and SendGrid backends with Jinja2 template rendering.
"""

import smtplib
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.config import settings
from ..core.database import get_session
from ..models import Template, Campaign, EmailEvent, User, Invoice, ABTest
from ..ab_testing.experiment import ExperimentManager

logger = logging.getLogger(__name__)


class EmailSender(ABC):
    """Abstract base class for email senders."""

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send an email. Returns True if successful."""
        pass


class SMTPSender(EmailSender):
    """SMTP email sender using smtplib."""

    def __init__(self):
        self.host: Optional[str] = settings.smtp_host
        self.port: int = settings.smtp_port
        self.username: Optional[str] = settings.smtp_username
        self.password: Optional[str] = settings.smtp_password
        self.from_email: Optional[str] = settings.email_from

        if not all([self.host, self.username, self.password, self.from_email]):
            logger.warning("SMTP configuration incomplete. Email sending disabled.")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send email via SMTP."""
        if not all([self.host, self.username, self.password, self.from_email]):
            logger.error("SMTP not configured. Cannot send email.")
            return False

        # At this point, mypy should know these are not None due to the check above
        assert self.host is not None
        assert self.username is not None
        assert self.password is not None
        assert self.from_email is not None

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            if headers:
                for key, value in headers.items():
                    msg[key] = value

            # Attach text part first (email clients show first part they support)
            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            else:
                # If no text body provided, create a simple one from HTML
                import re

                text_only = re.sub(r"<[^>]+>", "", html_body)
                msg.attach(MIMEText(text_only, "plain", "utf-8"))

            # Attach HTML part
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


class SendGridSender(EmailSender):
    """SendGrid email sender (placeholder for future implementation)."""

    def __init__(self):
        self.api_key: Optional[str] = settings.sendgrid_api_key
        self.from_email: Optional[str] = settings.email_from

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send email via SendGrid."""
        logger.warning("SendGrid sender not yet implemented. Using SMTP fallback.")
        return False


def get_email_sender() -> EmailSender:
    """Factory function to get the configured email sender."""
    return SMTPSender()


class EmailTemplateRenderer:
    """Jinja2 template renderer for email templates."""

    def __init__(self, template_dir: Optional[str] = None):
        if template_dir is None:
            # Use templates directory relative to this file
            import os

            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise


def send_followup_email(
    invoice_id: str,
    template_type: str,
    db: Optional[Session] = None,
    sender: Optional[EmailSender] = None,
) -> Optional[Campaign]:
    """
    Send a follow-up email for an invoice.

    Args:
        invoice_id: UUID of the invoice
        template_type: Type of template (follow_up_3_day, follow_up_7_day, follow_up_14_day)
        db: Database session (will create one if not provided)
        sender: Email sender instance (will create default if not provided)

    Returns:
        Campaign object if successful, None otherwise
    """
    close_db = False
    if db is None:
        db = next(get_session())
        close_db = True

    try:
        # Get invoice with related data
        from sqlalchemy import select

        stmt = (
            select(Invoice, User)
            .join(User, Invoice.user_id == User.id)
            .where(Invoice.id == invoice_id)
        )
        result = db.execute(stmt).first()

        if not result:
            logger.error(f"Invoice {invoice_id} not found")
            return None

        invoice, user = result

        # Check if user has email notifications enabled
        if not user.email_notifications_enabled:
            logger.info(f"User {user.id} has email notifications disabled")
            return None

        # Check if client email exists
        if not invoice.client_email:
            logger.error(f"Invoice {invoice_id} has no client email")
            return None

        # Get the template (system or user-specific)
        stmt = (
            select(Template)
            .where(
                Template.type == template_type,
                Template.is_active == True,
                (Template.user_id == user.id) | (Template.is_system == True),
            )
            .order_by(Template.is_system.asc())  # Prefer user templates over system
            .limit(1)
        )
        template = db.execute(stmt).scalar_one_or_none()

        if not template:
            logger.error(f"Template {template_type} not found for user {user.id}")
            return None

        # Create campaign record before sending (we need campaign.id for tracking)
        campaign = Campaign(
            user_id=user.id,
            template_id=template.id,
            invoice_id=invoice.id,
            scheduled_send_at=db.execute(select(func.now())).scalar(),
        )
        db.add(campaign)
        db.flush()  # Get campaign ID

        # Assign A/B testing variant if there are active template experiments for this user
        manager = ExperimentManager(db)
        active_experiments = (
            db.query(ABTest)
            .filter(
                ABTest.user_id == user.id,
                ABTest.is_active == True,
                ABTest.test_type == "template",
            )
            .all()
        )
        if active_experiments:
            # Use the most recent active experiment (could be enhanced for multiple concurrent experiments)
            experiment = active_experiments[0]
            variant = manager.assign_variant(
                experiment_id=experiment.id,
                user_id=user.id,
                campaign_id=campaign.id,
            )
            if variant:
                campaign.ab_test_variant = variant
                db.add(campaign)
        # If no active experiment, campaign.ab_test_variant remains None

        # Compute tracking pixel URL for email open tracking
        tracking_pixel_url = (
            f"{settings.api_base_url}/api/ab-tests/track/open/{campaign.id}"
        )

        # Render template with tracking pixel
        renderer = EmailTemplateRenderer()
        days_overdue = 0
        if invoice.status == "overdue" and invoice.due_date:
            days_overdue = (datetime.utcnow().date() - invoice.due_date.date()).days

        html_body = renderer.render(
            template_type,
            {
                "invoice": invoice,
                "user": user,
                "client_name": invoice.client_name,
                "amount": f"{invoice.amount:.2f} {invoice.currency}",
                "due_date": invoice.due_date.strftime("%B %d, %Y")
                if invoice.due_date
                else "",
                "invoice_number": invoice.invoice_number or "N/A",
                "days_overdue": days_overdue,
                "tracking_pixel_url": tracking_pixel_url,
            },
        )

        # Send email
        if sender is None:
            sender = get_email_sender()

        success = sender.send_email(
            to_email=invoice.client_email,
            subject=template.subject,
            html_body=html_body,
            text_body=template.body_text,
        )

        if success:
            campaign.sent_at = db.execute(select(func.now())).scalar()
            campaign.delivered_at = campaign.sent_at  # Assume delivered for now
            db.add(campaign)

            # Create sent event
            event = EmailEvent(
                campaign_id=campaign.id,
                event_type="sent",
            )
            db.add(event)
            db.commit()

            logger.info(
                f"Follow-up email sent: campaign={campaign.id}, invoice={invoice_id}"
            )
            return campaign
        else:
            db.rollback()
            logger.error(f"Failed to send follow-up email for invoice {invoice_id}")
            return None

    except Exception as e:
        logger.error(f"Error in send_followup_email: {e}")
        if close_db:
            db.rollback()
        raise
    finally:
        if close_db:
            db.close()
