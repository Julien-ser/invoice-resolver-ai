from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Invoice Resolver AI"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/invoice_resolver"
    )
    db_echo: bool = False

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Stripe
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # PayPal
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_webhook_id: Optional[str] = None

    # Plaid
    plaid_client_id: Optional[str] = None
    plaid_secret: Optional[str] = None
    plaid_environment: str = "sandbox"

    # OpenAI
    openai_api_key: Optional[str] = None

    # SendGrid (optional alternative to SMTP)
    sendgrid_api_key: Optional[str] = None

    # Email backend (smtp or sendgrid)
    email_backend: str = "smtp"

    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None

    # Redis (Celery)
    redis_url: str = "redis://localhost:6379/0"

    # S3 (PDF storage)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
