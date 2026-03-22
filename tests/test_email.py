"""
Tests for email automation system.

This module tests:
- EmailTemplateRenderer
- SMTPSender and SendGridSender
- send_followup_email function
- Celery tasks
"""

import os
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock, Mock
from jinja2 import Template

from src.mail.sender import (
    EmailSender,
    SMTPSender,
    SendGridSender,
    EmailTemplateRenderer,
    send_followup_email,
    get_email_sender,
)
from src.models import User, Invoice, Template, Campaign, EmailEvent


class TestEmailTemplateRenderer:
    """Test the EmailTemplateRenderer class."""

    def test_render_existing_template(self, tmp_path):
        """Test rendering a simple template with context."""
        # Create a temporary template file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test.html"
        template_file.write_text(
            "Hello {{ name }}, your invoice {{ invoice_number }} is {{ amount }}"
        )

        renderer = EmailTemplateRenderer(str(template_dir))
        result = renderer.render(
            "test.html", {"name": "John", "invoice_number": "123", "amount": "$100"}
        )

        assert result == "Hello John, your invoice 123 is $100"

    def test_render_missing_template_raises_error(self, tmp_path):
        """Test that rendering a non-existent template raises an error."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        renderer = EmailTemplateRenderer(str(template_dir))

        with pytest.raises(Exception):
            renderer.render("nonexistent.html", {})

    def test_render_with_jinja2_features(self, tmp_path):
        """Test rendering with conditionals and loops."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "advanced.html"
        template_file.write_text(
            """
            {% if user.is_active %}
            Active user: {{ user.full_name }}
            {% endif %}
            Items: {% for item in items %}{{ item }},{% endfor %}
            """
        )

        renderer = EmailTemplateRenderer(str(template_dir))
        result = renderer.render(
            "advanced.html",
            {
                "user": {"is_active": True, "full_name": "Alice"},
                "items": ["item1", "item2", "item3"],
            },
        )

        assert "Active user: Alice" in result
        assert "item1" in result
        assert "item2" in result
        assert "item3" in result


class TestSMTPSender:
    """Test the SMTPSender class."""

    def test_init_with_missing_config(self):
        """Test that SMTPSender initializes without error even with missing config."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.smtp_host = None
            mock_settings.smtp_username = None
            mock_settings.smtp_password = None
            mock_settings.email_from = None

            sender = SMTPSender()
            assert sender.host is None

    def test_send_email_without_config_returns_false(self):
        """Test that send_email returns False when SMTP is not configured."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.smtp_host = None
            mock_settings.smtp_username = None
            mock_settings.smtp_password = None
            mock_settings.email_from = None

            sender = SMTPSender()
            result = sender.send_email(
                to_email="test@example.com", subject="Test", html_body="<p>Hello</p>"
            )
            assert result is False

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp_class):
        """Test successful email sending via SMTP."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.example.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_username = "user@example.com"
            mock_settings.smtp_password = "password"
            mock_settings.email_from = "sender@example.com"

            sender = SMTPSender()
            result = sender.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_body="<p>HTML content</p>",
                text_body="Text content",
            )

            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("user@example.com", "password")
            mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_with_auth_error(self, mock_smtp_class):
        """Test email sending with authentication error."""
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("SMTP Authentication failed")
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.example.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_username = "user@example.com"
            mock_settings.smtp_password = "password"
            mock_settings.email_from = "sender@example.com"

            sender = SMTPSender()
            result = sender.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_body="<p>HTML content</p>",
            )

            assert result is False

    def test_send_email_generates_text_from_html_when_not_provided(self):
        """Test that a text version is generated from HTML when not provided."""
        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_server = MagicMock()
            mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_server)
            mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

            with patch("src.email.sender.settings") as mock_settings:
                mock_settings.smtp_host = "smtp.example.com"
                mock_settings.smtp_port = 587
                mock_settings.smtp_username = "user@example.com"
                mock_settings.smtp_password = "password"
                mock_settings.email_from = "sender@example.com"

                sender = SMTPSender()
                result = sender.send_email(
                    to_email="recipient@example.com",
                    subject="Test",
                    html_body="<p>Hello <b>World</b></p>",
                )

                assert result is True
                # Verify that a text part was attached
                sent_message = mock_server.send_message.call_args[0][0]
                # The message should have both text and HTML parts
                assert sent_message.is_multipart()


class TestSendGridSender:
    """Test the SendGridSender class."""

    def test_init(self):
        """Test SendGridSender initialization."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.sendgrid_api_key = "test-api-key"
            mock_settings.email_from = "sender@example.com"

            sender = SendGridSender()
            assert sender.api_key == "test-api-key"
            assert sender.from_email == "sender@example.com"

    def test_send_email_not_implemented(self):
        """Test that SendGridSender.send_email returns False (not implemented)."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.sendgrid_api_key = "test-api-key"
            mock_settings.email_from = "sender@example.com"

            sender = SendGridSender()
            result = sender.send_email(
                to_email="test@example.com", subject="Test", html_body="<p>Hello</p>"
            )
            assert result is False


class TestGetEmailSender:
    """Test the get_email_sender factory function."""

    def test_returns_smtp_sender_by_default(self):
        """Test that get_email_sender returns SMTPSender by default."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.email_backend = "smtp"
            sender = get_email_sender()
            assert isinstance(sender, SMTPSender)

    def test_returns_sendgrid_sender_when_configured(self):
        """Test that get_email_sender returns SendGridSender when backend is sendgrid."""
        with patch("src.email.sender.settings") as mock_settings:
            mock_settings.email_backend = "sendgrid"
            mock_settings.sendgrid_api_key = "test-key"
            sender = get_email_sender()
            assert isinstance(sender, SendGridSender)


class TestSendFollowupEmail:
    """Test the send_followup_email function."""

    @pytest.fixture
    def db_with_test_data(self, db_session):
        """Create test data in the database."""
        # Create user
        user = User(
            email="testclient@example.com",
            password_hash="hashedpassword",
            full_name="Test Client",
            company_name="Test Company",
            subscription_tier="pro",
            invoice_limit=999,
            email_notifications_enabled=True,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        # Create invoice
        invoice = Invoice(
            user_id=user.id,
            invoice_number="INV-001",
            client_name="John Doe",
            client_email="john@example.com",
            amount=150.00,
            currency="USD",
            status="overdue",
            due_date=date.today() - timedelta(days=7),
            description="Web development services",
        )
        db_session.add(invoice)
        db_session.flush()

        # Create template
        template = Template(
            user_id=user.id,
            is_system=True,
            name="7-Day Overdue Notice",
            type="follow_up_7_day",
            subject="Overdue Invoice: {{ invoice_number }}",
            body_html="<p>Hello {{ client_name }}, your invoice {{ invoice_number }} is overdue.</p>",
            body_text="Hello {{ client_name }}, your invoice {{ invoice_number }} is overdue.",
            is_active=True,
        )
        db_session.add(template)
        db_session.commit()

        yield {"user": user, "invoice": invoice, "template": template, "db": db_session}

        # Cleanup
        db_session.rollback()

    @patch("src.email.sender.get_email_sender")
    def test_send_followup_email_success(self, mock_get_sender, db_with_test_data):
        """Test successful follow-up email sending."""
        # Mock email sender
        mock_sender = MagicMock()
        mock_sender.send_email.return_value = True
        mock_get_sender.return_value = mock_sender

        data = db_with_test_data
        campaign = send_followup_email(
            invoice_id=data["invoice"].id,
            template_type="follow_up_7_day",
            db=data["db"],
        )

        assert campaign is not None
        assert campaign.invoice_id == data["invoice"].id
        assert campaign.template_id == data["template"].id
        assert campaign.sent_at is not None

        # Verify email was sent
        mock_sender.send_email.assert_called_once()
        call_args = mock_sender.send_email.call_args
        assert call_args[1]["to_email"] == "john@example.com"
        assert "Overdue Invoice:" in call_args[1]["subject"]
        assert "Hello John Doe" in call_args[1]["html_body"]

    def test_send_followup_email_invoice_not_found(self, db_with_test_data):
        """Test that None is returned when invoice doesn't exist."""
        with pytest.raises(Exception):
            send_followup_email(
                invoice_id="nonexistent-id",
                template_type="follow_up_7_day",
                db=db_with_test_data["db"],
            )

    @patch("src.email.sender.get_email_sender")
    def test_send_followup_email_user_without_email_notifications(
        self, mock_get_sender, db_with_test_data
    ):
        """Test that email is not sent when user disabled notifications."""
        data = db_with_test_data
        data["user"].email_notifications_enabled = False
        data["db"].commit()

        campaign = send_followup_email(
            invoice_id=data["invoice"].id,
            template_type="follow_up_7_day",
            db=data["db"],
        )

        assert campaign is None
        mock_get_sender.assert_not_called()

    @patch("src.email.sender.get_email_sender")
    def test_send_followup_email_missing_client_email(
        self, mock_get_sender, db_with_test_data
    ):
        """Test that None is returned when invoice has no client email."""
        data = db_with_test_data
        data["invoice"].client_email = None
        data["db"].commit()

        campaign = send_followup_email(
            invoice_id=data["invoice"].id,
            template_type="follow_up_7_day",
            db=data["db"],
        )

        assert campaign is None
        mock_get_sender.assert_not_called()

    @patch("src.email.sender.get_email_sender")
    def test_send_followup_email_template_not_found(
        self, mock_get_sender, db_with_test_data
    ):
        """Test behavior when template doesn't exist."""
        data = db_with_test_data
        # Delete the template
        data["db"].delete(data["template"])
        data["db"].commit()

        with pytest.raises(Exception):
            send_followup_email(
                invoice_id=data["invoice"].id,
                template_type="follow_up_7_day",
                db=data["db"],
            )

    @patch("src.email.sender.get_email_sender")
    def test_send_followup_email_sender_fails(self, mock_get_sender, db_with_test_data):
        """Test that None is returned when email sending fails."""
        mock_sender = MagicMock()
        mock_sender.send_email.return_value = False
        mock_get_sender.return_value = mock_sender

        data = db_with_test_data
        campaign = send_followup_email(
            invoice_id=data["invoice"].id,
            template_type="follow_up_7_day",
            db=data["db"],
        )

        assert campaign is None

    def test_send_followup_email_creates_campaign_record(self, db_with_test_data):
        """Test that a Campaign record is created and updated correctly."""
        with patch("src.email.sender.get_email_sender") as mock_get_sender:
            mock_sender = MagicMock()
            mock_sender.send_email.return_value = True
            mock_get_sender.return_value = mock_sender

            data = db_with_test_data
            campaign = send_followup_email(
                invoice_id=data["invoice"].id,
                template_type="follow_up_7_day",
                db=data["db"],
            )

            assert campaign is not None
            assert campaign.sent_at is not None
            assert campaign.delivered_at is not None

            # Check that an EmailEvent was created
            event = (
                data["db"].query(EmailEvent).filter_by(campaign_id=campaign.id).first()
            )
            assert event is not None
            assert event.event_type == "sent"

    def test_send_followup_email_calculates_days_overdue(self, db_with_test_data):
        """Test that days_overdue is correctly calculated and passed to template."""
        with patch("src.email.sender.get_email_sender") as mock_get_sender:
            mock_sender = MagicMock()
            mock_sender.send_email.return_value = True
            mock_get_sender.return_value = mock_sender

            data = db_with_test_data
            # Invoice is 7 days overdue
            send_followup_email(
                invoice_id=data["invoice"].id,
                template_type="follow_up_7_day",
                db=data["db"],
            )

            # Check that the template was rendered with days_overdue
            call_args = mock_sender.send_email.call_args
            html_body = call_args[1]["html_body"]
            assert "7 days" in html_body


class TestCeleryEmailTasks:
    """Test Celery email tasks."""

    @pytest.fixture
    def celery_task_data(self, db_session):
        """Create test data for Celery tasks."""
        from src.models import User, Invoice
        from datetime import date, timedelta

        user = User(
            email="celerytest@example.com",
            password_hash="hashed",
            full_name="Celery Test",
            company_name="Celery Corp",
            subscription_tier="pro",
            invoice_limit=999,
            email_notifications_enabled=True,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        # Create overdue invoices with different ages
        invoices = []
        for days in [3, 7, 14]:
            invoice = Invoice(
                user_id=user.id,
                invoice_number=f"INV-{days}",
                client_name=f"Client {days}",
                client_email=f"client{days}@example.com",
                amount=100.00 + days,
                currency="USD",
                status="overdue",
                due_date=date.today() - timedelta(days=days),
            )
            db_session.add(invoice)
            invoices.append(invoice)

        # Create templates
        templates = []
        for template_type in ["follow_up_3_day", "follow_up_7_day", "follow_up_14_day"]:
            template = Template(
                user_id=user.id,
                is_system=True,
                name=f"{template_type} Template",
                type=template_type,
                subject="Overdue Invoice",
                body_html="<p>Hello</p>",
                body_text="Hello",
                is_active=True,
            )
            db_session.add(template)
            templates.append(template)

        db_session.commit()

        yield {
            "user": user,
            "invoices": invoices,
            "templates": templates,
            "db": db_session,
        }

    @patch("src.tasks.email_tasks.send_followup_task")
    def test_process_followup_campaign(self, mock_send_task, celery_task_data):
        """Test that process_followup_campaign queues emails for eligible invoices."""
        from src.tasks.mail_tasks import process_followup_campaign

        mock_send_task.delay.return_value = None

        count = process_followup_campaign(
            days_overdue=7, template_type="follow_up_7_day"
        )

        # Should queue email for the 7-day overdue invoice
        assert count == 1
        mock_send_task.delay.assert_called_once()

    @patch("src.tasks.email_tasks.send_followup_task")
    def test_process_followup_campaign_skips_recently_sent(
        self, mock_send_task, celery_task_data
    ):
        """Test that invoices that already had a recent campaign are skipped."""
        from src.tasks.mail_tasks import process_followup_campaign
        from src.models import Campaign
        from datetime import datetime, timedelta, timezone

        data = celery_task_data
        # Create a recent campaign for the 7-day invoice
        recent_campaign = Campaign(
            user_id=data["user"].id,
            template_id=data["templates"][1].id,  # follow_up_7_day template
            invoice_id=data["invoices"][1].id,
            scheduled_send_at=datetime.now(timezone.utc),
            sent_at=datetime.now(timezone.utc),
        )
        data["db"].add(recent_campaign)
        data["db"].commit()

        mock_send_task.delay.return_value = None

        count = process_followup_campaign(
            days_overdue=7, template_type="follow_up_7_day"
        )

        # Should skip because campaign was sent within last 7 days
        assert count == 0
        mock_send_task.delay.assert_not_called()

    @patch("src.tasks.email_tasks.process_followup_campaign")
    def test_scheduled_followups(self, mock_process):
        """Test the scheduled_followups task."""
        from src.tasks.mail_tasks import scheduled_followups

        # Mock process_followup_campaign to return different counts
        mock_process.side_effect = [5, 3, 1]  # 3-day, 7-day, 14-day counts

        result = scheduled_followups()

        assert result == {
            "follow_up_3_day": 5,
            "follow_up_7_day": 3,
            "follow_up_14_day": 1,
        }
        assert mock_process.call_count == 3

    @patch("src.tasks.email_tasks.send_followup_email")
    def test_send_followup_task_wrapper(self, mock_send_email):
        """Test the send_followup_task Celery task wrapper."""
        from src.tasks.mail_tasks import send_followup_task

        mock_send_email.return_value = MagicMock(id="campaign-123")

        result = send_followup_task("invoice-id-123", "follow_up_7_day")

        assert result is True
        mock_send_email.assert_called_once_with(
            invoice_id="invoice-id-123", template_type="follow_up_7_day", db=None
        )

    @patch("src.tasks.email_tasks.send_followup_email")
    def test_send_followup_task_wrapper_handles_error(self, mock_send_email):
        """Test that send_followup_task returns False on error."""
        from src.tasks.mail_tasks import send_followup_task

        mock_send_email.side_effect = Exception("Database error")

        result = send_followup_task("invoice-id-123", "follow_up_7_day")

        assert result is False


class TestEmailTemplateContent:
    """Test the actual email template content."""

    def test_follow_up_3_day_template_exists(self):
        """Test that the 3-day follow-up template file exists."""
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "src",
            "email",
            "templates",
            "follow_up_3_day.html",
        )
        assert os.path.exists(template_path)

    def test_follow_up_7_day_template_exists(self):
        """Test that the 7-day follow-up template file exists."""
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "src",
            "email",
            "templates",
            "follow_up_7_day.html",
        )
        assert os.path.exists(template_path)

    def test_follow_up_14_day_template_exists(self):
        """Test that the 14-day follow-up template file exists."""
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "src",
            "email",
            "templates",
            "follow_up_14_day.html",
        )
        assert os.path.exists(template_path)

    def test_templates_contain_required_variables(self):
        """Test that all templates use the required Jinja2 variables."""
        required_vars = [
            "{{ client_name }}",
            "{{ amount }}",
            "{{ due_date }}",
            "{{ invoice_number }}",
        ]

        for template_name in [
            "follow_up_3_day.html",
            "follow_up_7_day.html",
            "follow_up_14_day.html",
        ]:
            template_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "src",
                "email",
                "templates",
                template_name,
            )
            with open(template_path, "r") as f:
                content = f.read()

            for var in required_vars:
                assert var in content, f"{var} missing from {template_name}"
