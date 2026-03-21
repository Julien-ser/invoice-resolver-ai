"""
Tests for configuration module (Settings).

This module tests:
- Settings default values
- Environment variable loading
- Type validation
- Configuration error handling
"""

import pytest
from unittest.mock import patch
from typing import Dict, Any
from pydantic import ValidationError

from src.core.config import Settings


class TestSettingsDefaults:
    """Tests for Settings default values."""

    def test_default_app_name(self):
        """Test default app name."""
        settings = Settings()
        assert settings.app_name == "Invoice Resolver AI"

    def test_default_debug(self):
        """Test default debug value."""
        settings = Settings()
        assert settings.debug is False

    def test_default_secret_key(self):
        """Test default secret key."""
        settings = Settings()
        assert settings.secret_key == "change-me-in-production"

    def test_default_database_url(self, monkeypatch):
        """Test default database URL."""
        # Ensure DATABASE_URL is not set to test the actual default
        monkeypatch.delenv("DATABASE_URL", raising=False)
        settings = Settings()
        assert settings.database_url == (
            "postgresql+psycopg://postgres:postgres@localhost:5432/invoice_resolver"
        )

    def test_default_db_echo(self):
        """Test default db_echo."""
        settings = Settings()
        assert settings.db_echo is False

    def test_default_jwt_algorithm(self):
        """Test default JWT algorithm."""
        settings = Settings()
        assert settings.jwt_algorithm == "HS256"

    def test_default_access_token_expire_minutes(self):
        """Test default access token expiration."""
        settings = Settings()
        assert settings.access_token_expire_minutes == 30

    def test_default_refresh_token_expire_days(self):
        """Test default refresh token expiration."""
        settings = Settings()
        assert settings.refresh_token_expire_days == 7

    def test_default_plaid_environment(self):
        """Test default Plaid environment."""
        settings = Settings()
        assert settings.plaid_environment == "sandbox"

    def test_default_email_backend(self):
        """Test default email backend."""
        settings = Settings()
        assert settings.email_backend == "smtp"

    def test_default_smtp_port(self):
        """Test default SMTP port."""
        settings = Settings()
        assert settings.smtp_port == 587

    def test_default_api_base_url(self):
        """Test default API base URL."""
        settings = Settings()
        assert settings.api_base_url == "http://localhost:8000"

    def test_default_redis_url(self):
        """Test default Redis URL."""
        settings = Settings()
        assert settings.redis_url == "redis://localhost:6379/0"


class TestSettingsWithEnvVars:
    """Tests for Settings with environment variables."""

    def test_stripe_api_key_from_env(self, monkeypatch):
        """Test Stripe API key loaded from environment."""
        monkeypatch.setenv("STRIPE_API_KEY", "sk_live_12345")
        settings = Settings()
        assert settings.stripe_api_key == "sk_live_12345"

    def test_paypal_credentials_from_env(self, monkeypatch):
        """Test PayPal credentials from environment."""
        monkeypatch.setenv("PAYPAL_CLIENT_ID", "paypal_client_123")
        monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "paypal_secret_123")
        settings = Settings()
        assert settings.paypal_client_id == "paypal_client_123"
        assert settings.paypal_client_secret == "paypal_secret_123"

    def test_plaid_credentials_from_env(self, monkeypatch):
        """Test Plaid credentials from environment."""
        monkeypatch.setenv("PLAID_CLIENT_ID", "plaid_client_123")
        monkeypatch.setenv("PLAID_SECRET", "plaid_secret_123")
        monkeypatch.setenv("PLAID_ENVIRONMENT", "development")
        settings = Settings()
        assert settings.plaid_client_id == "plaid_client_123"
        assert settings.plaid_secret == "plaid_secret_123"
        assert settings.plaid_environment == "development"

    def test_openai_api_key_from_env(self, monkeypatch):
        """Test OpenAI API key from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-12345")
        settings = Settings()
        assert settings.openai_api_key == "sk-openai-12345"

    def test_anthropic_api_key_from_env(self, monkeypatch):
        """Test Anthropic API key from environment."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-12345")
        settings = Settings()
        assert settings.anthropic_api_key == "sk-ant-12345"

    def test_smtp_config_from_env(self, monkeypatch):
        """Test SMTP configuration from environment."""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "465")
        monkeypatch.setenv("SMTP_USERNAME", "user@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "smtp_password_123")
        monkeypatch.setenv("EMAIL_FROM", "noreply@example.com")
        settings = Settings()
        assert settings.smtp_host == "smtp.example.com"
        assert settings.smtp_port == 465
        assert settings.smtp_username == "user@example.com"
        assert settings.smtp_password == "smtp_password_123"
        assert settings.email_from == "noreply@example.com"

    def test_s3_config_from_env(self, monkeypatch):
        """Test S3 configuration from environment."""
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
        monkeypatch.setenv(
            "AWS_SECRET_ACCESS_KEY", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        monkeypatch.setenv("S3_BUCKET", "my-invoice-bucket")
        settings = Settings()
        assert settings.aws_access_key_id == "AKIAIOSFODNN7EXAMPLE"
        assert (
            settings.aws_secret_access_key == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        assert settings.s3_bucket == "my-invoice-bucket"

    def test_redis_url_from_env(self, monkeypatch):
        """Test Redis URL from environment."""
        monkeypatch.setenv("REDIS_URL", "redis://redis-server:6379/1")
        settings = Settings()
        assert settings.redis_url == "redis://redis-server:6379/1"

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test that config accepts lowercase env vars."""
        # Pydantic settings is case-insensitive by default
        monkeypatch.setenv("stripe_api_key", "lowercase_key")
        settings = Settings()
        assert settings.stripe_api_key == "lowercase_key"


class TestSettingsTypeValidation:
    """Tests for Settings type validation."""

    def test_smtp_port_type_validation(self, monkeypatch):
        """Test that SMTP port is correctly parsed as integer."""
        monkeypatch.setenv("SMTP_PORT", "587")
        settings = Settings()
        assert isinstance(settings.smtp_port, int)
        assert settings.smtp_port == 587

    def test_access_token_expire_minutes_type(self, monkeypatch):
        """Test access token expiration is integer."""
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        settings = Settings()
        assert isinstance(settings.access_token_expire_minutes, int)
        assert settings.access_token_expire_minutes == 60

    def test_debug_as_string(self, monkeypatch):
        """Test debug parsed from string."""
        monkeypatch.setenv("DEBUG", "true")
        settings = Settings()
        assert settings.debug is True
        assert isinstance(settings.debug, bool)

    def test_invalid_port_raises_error(self, monkeypatch):
        """Test invalid port value raises validation error."""
        monkeypatch.setenv("SMTP_PORT", "not-a-number")
        with pytest.raises(ValidationError):
            Settings()

    def test_optional_strings_can_be_none(self):
        """Test optional string fields default to None."""
        settings = Settings()
        assert settings.stripe_api_key is None
        assert settings.openai_api_key is None
        assert settings.sendgrid_api_key is None
        assert settings.smtp_host is None
        assert settings.email_from is None


class TestSettingsSecurity:
    """Tests for security-related settings."""

    def test_secret_key_change_in_production_warning(self):
        """Test that default secret key is insecure."""
        settings = Settings()
        default_secret = settings.secret_key
        assert default_secret == "change-me-in-production"
        # In production, this should be overridden

    def test_optional_api_keys_not_required(self):
        """Test that API keys are optional (services can run without them)."""
        settings = Settings()
        # These should not raise errors even when None
        assert settings.stripe_api_key is None
        assert settings.paypal_client_id is None
        assert settings.openai_api_key is None


class TestSettingsConfiguration:
    """Tests for Settings configuration class."""

    def test_env_file_set(self):
        """Test that env_file is configured."""
        assert Settings.Config.env_file == ".env"

    def test_case_sensitive_false(self):
        """Test that case_sensitive is False (case-insensitive)."""
        assert Settings.Config.case_sensitive is False

    def test_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            "STRIPE_API_KEY=sk_test_from_file\nDEBUG=true\nSMTP_HOST=smtp.test.com\n"
        )

        # Patch the env_file path
        with patch.object(Settings.Config, "env_file", str(env_file)):
            # Clear environment to force file loading
            monkeypatch.delenv("STRIPE_API_KEY", raising=False)
            monkeypatch.delenv("DEBUG", raising=False)
            monkeypatch.delenv("SMTP_HOST", raising=False)

            settings = Settings()
            assert settings.stripe_api_key == "sk_test_from_file"
            assert settings.debug is True
            assert settings.smtp_host == "smtp.test.com"
