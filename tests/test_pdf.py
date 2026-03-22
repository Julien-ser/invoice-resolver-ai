"""
Tests for PDF generator module.

Tests cover PDF generation from HTML content, template rendering,
and proper file output.
"""

import os
import tempfile
from pathlib import Path
from datetime import date

import pytest

from src.pdf.generator import PDFGenerator, generate_pdf


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
    </head>
    <body>
        <h1>Test PDF Generation</h1>
        <p>This is a test document with <strong>bold</strong> text.</p>
        <p>Invoice #: INV-001</p>
        <p>Amount: $500.00</p>
        <table>
            <tr><th>Item</th><th>Price</th></tr>
            <tr><td>Service A</td><td>$300</td></tr>
            <tr><td>Service B</td><td>$200</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def dispute_letter_context():
    """Sample context for dispute letter template."""
    return {
        "sender_name": "John Doe Consulting",
        "sender_address": "123 Main St",
        "sender_city_state_zip": "Anytown, CA 12345",
        "sender_email": "john@example.com",
        "sender_phone": "(555) 123-4567",
        "sender_title": "Owner",
        "date": date.today().strftime("%B %d, %Y"),
        "recipient_name": "Acme Corp",
        "recipient_address": "456 Business Ave",
        "recipient_city_state_zip": "Metropolis, NY 10001",
        "invoice_number": "INV-2024-001",
        "amount": "1250.00",
        "currency": "USD",
        "issue_date": "2024-01-15",
        "due_date": "2024-02-15",
        "days_overdue": "30",
        "deadline_date": (date.today()).strftime("%B %d, %Y"),
        "evidence_list": [
            {
                "date": "2024-02-20",
                "description": "Sent first follow-up email",
                "type": "communication",
            },
            {
                "date": "2024-02-25",
                "description": "Phone call to client",
                "type": "communication",
            },
        ],
        "payment_link": "https://example.com/pay/INV-2024-001",
        "bank_details": "Bank of Example, Account: 123456789, Routing: 987654321",
        "check_address": "123 Main St, Anytown, CA 12345",
        "cc_parties": "Legal Department (if applicable)",
    }


@pytest.fixture
def small_claims_context():
    """Sample context for small claims form template."""
    return {
        "user_name": "John Doe",
        "user_address": "123 Main St",
        "user_phone": "(555) 123-4567",
        "user_email": "john@example.com",
        "prepared_date": date.today().strftime("%B %d, %Y"),
        "defendant_name": "Acme Corp",
        "defendant_address": "456 Business Ave, Metropolis, NY 10001",
        "defendant_phone": "(555) 987-6543",
        "defendant_email": "accounts@acme.com",
        "invoice_number": "INV-2024-001",
        "amount": "1250.00",
        "currency": "USD",
        "issue_date": "2024-01-15",
        "due_date": "2024-02-15",
        "days_overdue": "30",
        "jurisdiction": "Anytown, California Small Claims Court",
        "description": "Consulting services rendered as per agreement. Invoice remains unpaid despite multiple follow-ups.",
        "timeline": [
            {
                "date": "2024-01-15",
                "description": "Invoice issued",
                "document": "Invoice INV-2024-001",
            },
            {
                "date": "2024-02-20",
                "description": "First follow-up email sent",
                "document": "Email record",
            },
            {
                "date": "2024-02-25",
                "description": "Phone call with client",
                "document": "Call log",
            },
            {
                "date": "2024-03-01",
                "description": "Final demand letter sent",
                "document": "Letter copy",
            },
        ],
        "evidence_list": [
            {
                "date": "2024-01-15",
                "type": "document",
                "description": "Invoice issued",
                "amount": "1250.00",
                "document": "Invoice INV-2024-001",
            },
            {
                "date": "2024-02-01",
                "type": "communication",
                "description": "Email acknowledgment received",
                "document": "Email",
            },
            {
                "date": "2024-02-20",
                "type": "communication",
                "description": "Follow-up email sent",
                "document": "Email",
            },
        ],
        "interest_amount": "25.00",
        "additional_costs": "75.00",
        "total_amount": "1350.00",
        "witnesses": [
            {
                "name": "Jane Smith",
                "contact": "jane@example.com",
                "relevance": "Project manager who oversaw work",
            },
        ],
        "statute_of_limitations": "4 years for written contracts (California)",
        "support_contact": "Invoice Resolver AI Support <support@invoiceresolver.ai>",
        "generated_date": date.today().strftime("%B %d, %Y"),
    }


class TestPDFGenerator:
    """Test suite for PDFGenerator class."""

    def test_generator_initialization(self):
        """Test PDF generator can be initialized."""
        generator = PDFGenerator()
        assert generator.templates_dir.exists()
        assert generator.jinja_env is not None

    def test_generate_pdf_from_html(self, sample_html, tmp_path):
        """Test generating PDF from raw HTML content."""
        output_path = tmp_path / "test_output.pdf"
        result = generate_pdf(sample_html, output_path=output_path)

        assert result.exists()
        assert result.stat().st_size > 0

    def test_generate_pdf_returns_bytes(self, sample_html):
        """Test generating PDF returns bytes when no output path given."""
        result = generate_pdf(sample_html)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # Check PDF magic number
        assert result[:4] == b"%PDF"

    def test_generate_pdf_with_custom_margins(self, sample_html, tmp_path):
        """Test generating PDF with custom margins."""
        output_path = tmp_path / "test_margins.pdf"
        margins = {"top": "2cm", "right": "1.5cm", "bottom": "2cm", "left": "1.5cm"}
        result = generate_pdf(sample_html, output_path=output_path, margins=margins)

        assert result.exists()
        assert result.stat().st_size > 0

    def test_generate_pdf_with_custom_page_size(self, sample_html, tmp_path):
        """Test generating PDF with custom page size."""
        output_path = tmp_path / "test_letter.pdf"
        result = generate_pdf(sample_html, output_path=output_path, page_size="Letter")

        assert result.exists()
        assert result.stat().st_size > 0

    def test_render_dispute_letter_template(self, dispute_letter_context, tmp_path):
        """Test rendering dispute letter template."""
        generator = PDFGenerator()
        output_path = tmp_path / "dispute_letter.pdf"
        result = generator.render_template(
            "dispute_letter.html", dispute_letter_context, output_path=output_path
        )

        assert result.exists()
        assert result.stat().st_size > 0

    def test_render_small_claims_template(self, small_claims_context, tmp_path):
        """Test rendering small claims form template."""
        generator = PDFGenerator()
        output_path = tmp_path / "small_claims.pdf"
        result = generator.render_template(
            "small_claims_form.html", small_claims_context, output_path=output_path
        )

        assert result.exists()
        assert result.stat().st_size > 0

    def test_render_template_missing_variable(self, dispute_letter_context):
        """Test error handling when template variable is missing."""
        generator = PDFGenerator()
        context = dispute_letter_context.copy()
        del context["invoice_number"]  # Remove required variable

        with pytest.raises(ValueError, match="Missing template variable"):
            generator.render_template("dispute_letter.html", context)

    def test_render_template_not_found(self):
        """Test error handling when template doesn't exist."""
        generator = PDFGenerator()
        with pytest.raises(FileNotFoundError):
            generator.render_template("nonexistent.html", {})

    def test_generate_pdf_with_additional_css(self, sample_html, tmp_path):
        """Test generating PDF with additional CSS styles."""
        output_path = tmp_path / "test_css.pdf"
        custom_css = """
        h1 { color: red; }
        p { font-size: 14px; }
        """
        result = generate_pdf(
            sample_html, output_path=output_path, css_styles=custom_css
        )

        assert result.exists()
        assert result.stat().st_size > 0

    def test_multiple_generations_produce_different_files(
        self, dispute_letter_context, tmp_path
    ):
        """Test that multiple PDF generations produce unique files."""
        generator = PDFGenerator()

        output_path1 = tmp_path / "letter1.pdf"
        output_path2 = tmp_path / "letter2.pdf"

        # Modify context slightly between generations
        context1 = dispute_letter_context.copy()
        context2 = dispute_letter_context.copy()
        context2["amount"] = "999.99"

        result1 = generator.render_template(
            "dispute_letter.html", context1, output_path=output_path1
        )
        result2 = generator.render_template(
            "dispute_letter.html", context2, output_path=output_path2
        )

        assert result1.exists()
        assert result2.exists()
        # Files should be different sizes due to changed content
        assert result1.stat().st_size != result2.stat().st_size
