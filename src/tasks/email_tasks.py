"""
Celery tasks for email automation and follow-up campaigns.

This module contains background tasks for sending follow-up emails
based on invoice status and age.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ..celery_app import celery_app
from ..core.database import get_session
from ..core.config import settings
from ..models import Invoice, User, Template, Campaign
from ..mail.sender import send_followup_email, get_email_sender

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.email.send_followup_task")
def send_followup_task(self, invoice_id: str, template_type: str) -> bool:
    """
    Celery task wrapper for sending a follow-up email.

    Args:
        invoice_id: UUID of the invoice
        template_type: Type of template to send

    Returns:
        True if successful, False otherwise
    """
    try:
        db = next(get_session())
        campaign = send_followup_email(
            invoice_id=invoice_id, template_type=template_type, db=db
        )
        return campaign is not None
    except Exception as e:
        logger.error(f"Error in send_followup_task for invoice {invoice_id}: {e}")
        return False
    finally:
        if "db" in locals():
            db.close()


@celery_app.task(bind=True, name="tasks.email.process_followup_campaign")
def process_followup_campaign(self, days_overdue: int, template_type: str) -> int:
    """
    Process all eligible invoices for a follow-up campaign.

    Args:
        days_overdue: Number of daysinvoice is overdue (3, 7, 14)
        template_type: Template type to send

    Returns:
        Number of emails sent
    """
    db: Optional[Session] = None
    sent_count = 0

    try:
        db = next(get_session())

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)

        # Find invoices that are overdue and haven't been sent this template type yet
        stmt = (
            select(Invoice, User)
            .join(User, Invoice.user_id == User.id)
            .where(
                and_(
                    Invoice.status == "overdue",
                    Invoice.due_date <= cutoff_date,
                    Invoice.client_email.is_not(None),
                    User.email_notifications_enabled == True,
                    User.is_active == True,
                )
            )
        )

        results = db.execute(stmt).all()

        for invoice, user in results:
            # Check if this template was already sent recently (within last 7 days)
            existing_campaign = db.execute(
                select(Campaign).where(
                    and_(
                        Campaign.invoice_id == invoice.id,
                        Campaign.template_id
                        == select(Template.id)
                        .where(Template.type == template_type)
                        .scalar_subquery(),
                        Campaign.sent_at >= datetime.utcnow() - timedelta(days=7),
                    )
                )
            ).scalar_one_or_none()

            if existing_campaign:
                logger.debug(
                    f"Skipping invoice {invoice.id}: template {template_type} "
                    f"already sent within 7 days"
                )
                continue

            # Send email asynchronously
            send_followup_task.delay(str(invoice.id), template_type)
            sent_count += 1

        logger.info(
            f"process_followup_campaign: queued {sent_count} emails "
            f"for template {template_type}"
        )
        return sent_count

    except Exception as e:
        logger.error(f"Error in process_followup_campaign: {e}")
        return 0
    finally:
        if db:
            db.close()


@celery_app.task(bind=True, name="tasks.email.scheduled_followups")
def scheduled_followups(self) -> dict:
    """
    Scheduled task that runs every 15 minutes to check for invoices
    that need follow-up emails based on their overdue status.

    This task checks for:
    - 3-day overdue (3 days past due)
    - 7-day overdue (7 days past due)
    - 14-day overdue (14 days past due - final notice)

    Returns:
        Dictionary with counts of emails sent for each type
    """
    results = {
        "follow_up_3_day": 0,
        "follow_up_7_day": 0,
        "follow_up_14_day": 0,
    }

    try:
        # Process each follow-up stage
        for days, template_type in [
            (3, "follow_up_3_day"),
            (7, "follow_up_7_day"),
            (14, "follow_up_14_day"),
        ]:
            count = process_followup_campaign(days, template_type)
            results[template_type] = count

        logger.info(f"Scheduled follow-ups completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Error in scheduled_followups: {e}")
        return results
