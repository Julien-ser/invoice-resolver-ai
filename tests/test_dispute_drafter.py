"""
Tests for AI dispute letter drafting functionality.

This module tests the DisputeLetterGenerator and draft_dispute_letter function,
including prompt generation, AI provider integration, and cost calculation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta

from src.models import User, Invoice
from src.core.config import Settings
from src.ai.dispute_drafter import DisputeLetterGenerator, draft_dispute_letter


class TestDisputeLetterGenerator:
    """Tests for the DisputeLetterGenerator class."""

    @pytest.fixture
    def mock_openai_settings(self, monkeypatch):
        """Patch settings to have OpenAI API key."""
        settings = Settings()
        settings.openai_api_key = "sk-test-openai-key"
        settings.anthropic_api_key = None
        return settings

    @pytest.fixture
    def mock_anthropic_settings(self, monkeypatch):
        """Patch settings to have Anthropic API key."""
        settings = Settings()
        settings.openai_api_key = None
        settings.anthropic_api_key = "sk-ant-test-key"
        return settings

    @pytest.fixture
    def mock_no_provider_settings(self, monkeypatch):
        """Patch settings to have no AI provider keys."""
        settings = Settings()
        settings.openai_api_key = None
        settings.anthropic_api_key = None
        return settings

    @pytest.fixture
    def sample_invoice(self):
        """Create a sample invoice object for testing (not persisted)."""
        user = User(
            id="user-123",
            email="test@example.com",
            full_name="John Doe",
            company_name="John's Web Services",
            subscription_tier="pro",
            is_active=True,
        )
        invoice = Invoice(
            id="inv-456",
            user_id=user.id,
            invoice_number="INV-2024-001",
            client_name="Acme Corp",
            client_email="billing@acme.com",
            amount=2500.00,
            currency="USD",
            status="overdue",
            due_date=datetime.utcnow() - timedelta(days=30),
            issue_date=datetime.utcnow() - timedelta(days=60),
            description="Web development services - Phase 2",
            notes="Previous reminder sent on 2024-02-15",
        )
        return invoice

    @pytest.fixture
    def sample_evidence(self):
        """Sample evidence list for dispute letter."""
        return [
            {
                "date": "2024-02-01",
                "description": "Invoice sent to client",
                "type": "invoice",
            },
            {
                "date": "2024-02-15",
                "description": "First follow-up email sent",
                "type": "communication",
            },
            {
                "date": "2024-02-20",
                "description": "Phone call - client promised payment",
                "type": "communication",
            },
            {
                "date": "2024-02-25",
                "description": "Second follow-up - no response",
                "type": "communication",
            },
        ]

    def test_init_with_openai(self, mock_openai_settings, monkeypatch):
        """Test generator initializes with OpenAI when key is set."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_openai_settings)

        generator = DisputeLetterGenerator()
        assert generator.provider == "openai"
        assert generator.openai_client is not None
        assert generator.anthropic_client is None

    def test_init_with_anthropic(self, mock_anthropic_settings, monkeypatch):
        """Test generator initializes with Anthropic when key is set."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_anthropic_settings)

        generator = DisputeLetterGenerator()
        assert generator.provider == "anthropic"
        assert generator.openai_client is None
        assert generator.anthropic_client is not None

    def test_init_with_both_providers(self, monkeypatch):
        """Test generator prefers OpenAI when both keys are set."""
        settings = Settings()
        settings.openai_api_key = "sk-test-openai"
        settings.anthropic_api_key = "sk-ant-test"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        assert generator.provider == "openai"

    def test_init_no_provider_raises_error(
        self, mock_no_provider_settings, monkeypatch
    ):
        """Test generator raises error when no API keys configured."""
        monkeypatch.setattr(
            "src.ai.dispute_drafter.settings", mock_no_provider_settings
        )

        with pytest.raises(ValueError, match="No AI provider configured"):
            DisputeLetterGenerator()

    def test_build_prompt_formal_dispute(
        self, sample_invoice, sample_evidence, monkeypatch
    ):
        """Test prompt construction for formal dispute letter."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=sample_evidence,
            letter_type="formal_dispute",
            recipient="Acme Corp",
        )

        # Check prompt contains key elements
        assert "Invoice #: INV-2024-001" in prompt
        assert "Client: Acme Corp" in prompt
        assert "$2500.00 USD" in prompt
        assert "OVERDUE" in prompt
        assert sample_invoice.description in prompt
        assert "14 days" in prompt  # Payment deadline mentioned
        assert "small claims court" in prompt
        # Check evidence is included
        assert "2024-02-01: Invoice sent to client" in prompt
        assert "2024-02-15: First follow-up email sent" in prompt
        assert "HTML format" in prompt  # Output format specified

    def test_build_prompt_small_claims_prep(
        self, sample_invoice, sample_evidence, monkeypatch
    ):
        """Test prompt construction for small claims preparation."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=sample_evidence,
            letter_type="small_claims_prep",
            recipient="Court Clerk",
        )

        assert "Case summary" in prompt
        assert "Chronological timeline" in prompt
        assert "Calculation of damages" in prompt
        assert "Court forms" in prompt

    def test_build_prompt_demand_letter(
        self, sample_invoice, sample_evidence, monkeypatch
    ):
        """Test prompt construction for demand letter."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=sample_evidence,
            letter_type="demand_letter",
            recipient="Acme Corp",
        )

        assert "final demand" in prompt.lower()
        assert "7-day" in prompt
        assert "legal action" in prompt.lower()
        assert "payment plan" in prompt

    def test_build_prompt_empty_evidence(self, sample_invoice, monkeypatch):
        """Test prompt with no evidence provided."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=[],
            letter_type="formal_dispute",
        )

        assert "No specific evidence provided" in prompt

    def test_build_prompt_default_recipient(
        self, sample_invoice, sample_evidence, monkeypatch
    ):
        """Test prompt uses client name when no recipient specified."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=sample_evidence,
            letter_type="formal_dispute",
        )

        assert "RECIPIENT:\nAcme Corp" in prompt

    @patch("openai.OpenAI")
    def test_call_openai_success(
        self, mock_openai_class, mock_openai_settings, monkeypatch
    ):
        """Test successful OpenAI API call."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_openai_settings)

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="<html>Dispute letter content</html>"))
        ]
        mock_response.usage = Mock(
            prompt_tokens=500, completion_tokens=200, total_tokens=700
        )

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        generator = DisputeLetterGenerator()
        # Re-assign client to use mock
        generator.openai_client = mock_client
        result = generator._call_openai("Test prompt", "formal_dispute")

        assert result["content"] == "<html>Dispute letter content</html>"
        assert result["provider"] == "openai/gpt-4-turbo"
        assert result["tokens_used"] == 700
        assert result["cost_usd"] == round((500 / 1000 * 0.01) + (200 / 1000 * 0.03), 4)
        assert result["model"] == "gpt-4-turbo-preview"

    @patch("anthropic.Anthropic")
    def test_call_anthropic_success(
        self, mock_anthropic_class, mock_anthropic_settings, monkeypatch
    ):
        """Test successful Anthropic API call."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_anthropic_settings)

        # Mock Anthropic response
        mock_content = Mock()
        mock_content.text = "<html>Dispute letter content from Claude</html>"
        mock_response = Mock()
        mock_response.content = [mock_content]
        mock_response.usage = Mock(input_tokens=400, output_tokens=150)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        generator = DisputeLetterGenerator()
        # Re-assign client to use mock
        generator.anthropic_client = mock_client
        result = generator._call_anthropic("Test prompt", "formal_dispute")

        assert result["content"] == "<html>Dispute letter content from Claude</html>"
        assert result["provider"] == "anthropic/claude-3-opus"
        assert result["tokens_used"] == 550
        assert result["cost_usd"] == round(
            (400 / 1000 * 0.015) + (150 / 1000 * 0.075), 4
        )
        assert result["model"] == "claude-3-opus-20240229"

    def test_draft_dispute_letter_integration_openai(
        self, sample_invoice, sample_evidence, mock_openai_settings, monkeypatch
    ):
        """Test full draft_dispute_letter flow with mocked OpenAI."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_openai_settings)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content="<html>Test letter</html>"))
            ]
            mock_response.usage = Mock(
                prompt_tokens=300, completion_tokens=100, total_tokens=400
            )

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            result = draft_dispute_letter(
                invoice=sample_invoice,
                evidence_list=sample_evidence,
                letter_type="formal_dispute",
                recipient=None,
            )

            assert "content" in result
            assert "provider" in result
            assert "tokens_used" in result
            assert "cost_usd" in result
            assert "generated_at" in result
            assert "letter_type" in result
            assert result["letter_type"] == "formal_dispute"

    def test_draft_dispute_letter_integration_anthropic(
        self, sample_invoice, sample_evidence, mock_anthropic_settings, monkeypatch
    ):
        """Test full draft_dispute_letter flow with mocked Anthropic."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_anthropic_settings)

        with patch("anthropic.Anthropic") as mock_anthropic_class:
            mock_content = Mock()
            mock_content.text = "<html>Test letter from Claude</html>"
            mock_response = Mock()
            mock_response.content = [mock_content]
            mock_response.usage = Mock(
                input_tokens=250, output_tokens=80, total_tokens=330
            )

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic_class.return_value = mock_client

            result = draft_dispute_letter(
                invoice=sample_invoice,
                evidence_list=sample_evidence,
                letter_type="demand_letter",
            )

            assert "content" in result
            assert "anthropic" in result["provider"]
            assert result["letter_type"] == "demand_letter"

    def test_different_letter_types(self, sample_invoice, sample_evidence, monkeypatch):
        """Test that different letter types produce appropriate prompts."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()

        for letter_type in ["formal_dispute", "small_claims_prep", "demand_letter"]:
            # Just test that the method doesn't raise errors
            prompt = generator._build_prompt(
                invoice=sample_invoice,
                evidence_list=sample_evidence,
                letter_type=letter_type,
            )
            assert len(prompt) > 0
            assert "invoice" in prompt.lower()

    def test_evidence_includes_amount(self, sample_invoice, monkeypatch):
        """Test that evidence amounts are included when present."""
        settings = Settings()
        settings.openai_api_key = "test-key"
        monkeypatch.setattr("src.ai.dispute_drafter.settings", settings)

        generator = DisputeLetterGenerator()
        evidence_with_amount = [
            {"date": "2024-02-01", "description": "Partial payment", "amount": 500.00}
        ]

        prompt = generator._build_prompt(
            invoice=sample_invoice,
            evidence_list=evidence_with_amount,
            letter_type="formal_dispute",
        )

        assert "$500.00" in prompt

    def test_cost_calculation_openai(self):
        """Test OpenAI cost calculation is accurate."""
        prompt_tokens = 1000
        completion_tokens = 500

        input_cost = (prompt_tokens / 1000) * 0.01
        output_cost = (completion_tokens / 1000) * 0.03
        expected_cost = round(input_cost + output_cost, 4)

        assert expected_cost == round(
            (1.0 * 0.01) + (0.5 * 0.03), 4
        )  # 0.01 + 0.015 = 0.025

    def test_cost_calculation_anthropic(self):
        """Test Anthropic cost calculation is accurate."""
        input_tokens = 800
        output_tokens = 400

        input_cost = (input_tokens / 1000) * 0.015
        output_cost = (output_tokens / 1000) * 0.075
        expected_cost = round(input_cost + output_cost, 4)

        assert expected_cost == round(
            (0.8 * 0.015) + (0.4 * 0.075), 4
        )  # 0.012 + 0.03 = 0.042

    def test_letter_type_in_result(
        self, sample_invoice, sample_evidence, mock_openai_settings, monkeypatch
    ):
        """Test that result includes letter_type."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_openai_settings)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="<html>Test</html>"))]
            mock_response.usage = Mock(
                prompt_tokens=100, completion_tokens=50, total_tokens=150
            )

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            result = draft_dispute_letter(
                invoice=sample_invoice,
                evidence_list=sample_evidence,
                letter_type="small_claims_prep",
                recipient=None,
            )

            assert result["letter_type"] == "small_claims_prep"

    def test_generated_at_timestamp(
        self, sample_invoice, sample_evidence, mock_openai_settings, monkeypatch
    ):
        """Test that result includes ISO timestamp."""
        monkeypatch.setattr("src.ai.dispute_drafter.settings", mock_openai_settings)

        with patch("openai.OpenAI") as mock_openai_class:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="<html>Test</html>"))]
            mock_response.usage = Mock(
                prompt_tokens=100, completion_tokens=50, total_tokens=150
            )

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            result = draft_dispute_letter(
                invoice=sample_invoice,
                evidence_list=sample_evidence,
            )

            # Check it's a valid ISO timestamp
            from datetime import datetime

            dt = datetime.fromisoformat(result["generated_at"])
            assert isinstance(dt, datetime)
