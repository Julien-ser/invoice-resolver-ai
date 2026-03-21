# Invoice Resolver AI

**An autonomous AI agent for resolving invoice disputes and recovering unpaid invoices.**

---

## Problem

Freelancers and small SaaS founders waste hours chasing unpaid invoices, drafting dispute letters, and navigating payment platforms. Payment delays and chargebacks are common, but resolution is manual and frustrating.

## Solution

An intelligent AI agent that monitors Stripe/PayPal/Bank feeds, detects overdue or disputed invoices, and automatically:

- Sends polite follow-ups with payment links
- Drafts formal dispute letters (with evidence attachments) for chargebacks
- Escalates to small claims paperwork if needed (pre-filled forms)
- Learns which templates and timing work best (A/B testing)

## Features

- **Multi-provider Integration**: Stripe, PayPal, and Plaid (bank feeds)
- **AI-Powered Dispute Drafting**: GPT-4/Claude integration for legal letters
- **Automated Email Campaigns**: Follow-up sequences (3, 7, 14 days)
- **PDF Generation**: Dispute letters and small claims forms
- **A/B Testing**: Optimize templates and timing
- **Analytics Dashboard**: Recovery rates, campaign performance
- **Admin Panel**: User management, system health monitoring
- **Freemium Model**: 5 free invoices/month, $19/mo unlimited

## Tech Stack

- **Backend**: Python 3.11-3.13, FastAPI, PostgreSQL (Python 3.14 not yet supported due to pydantic-core compatibility)
- **Task Queue**: Celery + Redis
- **AI Integration**: OpenAI GPT-4 / Anthropic Claude
- **Payment APIs**: Stripe, PayPal REST SDK, Plaid
- **Email**: SendGrid / SMTP with Jinja2 templates
- **Dashboard**: Streamlit
- **PDF**: WeasyPrint or ReportLab
- **Deployment**: Docker, GitHub Actions CI/CD

## Project Structure

```
.
├── README.md              # Project documentation
├── TASKS.md               # Development task list (track progress)
├── schema.sql             # PostgreSQL database schema
├── docs/
│   └── database-er-diagram.md  # ER diagram and table docs
├── .github/
│   └── workflows/
│       └── test.yml       # CI pipeline (to be created)
├── src/                   # Source code (to be created)
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Configuration, logging
│   ├── models/           # SQLAlchemy models
│   ├── integrations/     # Stripe/PayPal/Plaid clients
│   ├── email/            # Email automation
│   ├── ai/               # AI dispute drafter
│   ├── pdf/              # PDF generator
│   ├── dashboard/        # Streamlit app
│   ├── ab_testing/       # A/B testing framework
│   ├── admin/            # Admin panel
│   ├── billing/          # Stripe billing
│   ├── tasks/            # Celery tasks
│   └── utils/            # Helper functions
├── tests/                 # Test suite (pytest)
├── docker-compose.yml     # Local development (PostgreSQL, Redis)
├── Dockerfile             # API container
├── Dockerfile.celery      # Celery worker container
├── pyproject.toml         # Dependencies (Poetry) or requirements.txt
└── .env.example           # Environment variables template
```

## Current Progress

### Phase 1: Planning & Setup

- [x] **Task 1.1**: Database schema design
  - 11 core tables with relationships
  - Comprehensive indexes for performance
  - Row Level Security (RLS) policies
  - Database functions and views
  - Full ER diagram with table documentation
- [x] **Task 1.2**: FastAPI project structure initialization
  - Core configuration module (`src/core/config.py`) with environment-based settings
  - Logging setup (`src/core/logger.py`) with console and file handlers
  - Main FastAPI application (`src/main.py`) with health check and CORS
  - Dependencies in `requirements.txt`: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv, bcrypt, python-jose, passlib
  - Environment variable template (`.env.example`)
- [ ] **Task 1.3**: PostgreSQL setup with SQLAlchemy + Alembic
- [x] **Task 1.4**: API documentation outline

### Phase 2: Core Backend & Data Model

- [x] **Task 2.1**: User authentication system with JWT tokens
  - Implemented `/api/auth/register` endpoint for user signup
  - Implemented `/api/auth/login` endpoint for JWT authentication (access + refresh tokens)
  - Implemented `/api/auth/refresh` endpoint for token rotation
  - Implemented `/api/auth/logout` endpoint to revoke refresh tokens
  - Bcrypt password hashing with passlib
  - JWT token generation with expiration and payload validation
  - Refresh token storage with single-use rotation in database
  - Subscription limit enforcement middleware for free tier users
  - Protected route dependencies (`get_current_user`, `get_current_admin_user`)
  - Comprehensive test suite covering registration, login, token refresh, logout
  - Test fixtures with SQLite in-memory database for isolated tests
- [x] **Task 2.2**: Invoice management endpoints
  - Full CRUD operations: create, list, update status, soft delete
  - Filtering by status and due date range
  - Pydantic schemas for request/response validation
  - Integration with SQLAlchemy models and database
  - Comprehensive tests with pytest
- [x] **Task 2.3**: Webhook receivers for Stripe and PayPal
  - Signature verification for both providers
  - Idempotent processing with webhook_events table
  - Automatic invoice status updates
  - Endpoints: `/api/webhooks/stripe` and `/api/webhooks/paypal`
  - Comprehensive logging and error handling
  - Support for key events: invoice.payment_failed, charge.dispute.created, PAYMENT.DENIED, DISPUTE.CREATED
- [x] **Task 2.4**: Celery background task setup
  - Redis broker and Celery worker configuration
  - Docker Compose setup with Redis service
  - Periodic sync task (`tasks/sync.py`) for invoice status synchronization (fallback if webhooks fail)
  - 15-minute polling interval via Celery Beat
  - Integration with Stripe and PayPal APIs
  - Per-user credential handling for PayPal connections
  - System metrics recording for monitoring

### Phase 3: Integrations & AI Features

- [x] **Task 3.1**: Payment provider integration layer
  - Structured clients for Stripe (`integrations/stripe_client.py`), PayPal (`integrations/paypal_client.py`), and Plaid (`integrations/plaid_client.py`)
  - Unified interface: `connect_account()`, `get_invoice_status()`, `list_transactions()`
  - Error handling and retry logic built-in
  - Ready for API credential injection via encrypted database storage
- [x] **Task 3.2**: Email automation system with follow-up sequences ✓ **COMPLETED**
  - **Email sender abstraction**: `SMTPSender` and `SendGridSender` (placeholder) implementing common interface
  - **Template rendering**: Jinja2-based renderer with HTML and plain text support
  - **Follow-up sequences**: Three automated templates
    - 3-day reminder: Polite pre-due notification
    - 7-day overdue: Clear overdue notice with red warning
    - 14-day final notice: Urgent final warning before dispute escalation
  - **Campaign tracking**: `Campaign` and `EmailEvent` models for send/delivery/engagement metrics
  - **Celery integration**: Asynchronous background tasks (`tasks/email_tasks.py`)
    - `send_followup_task`: Wrapper for single email sending
    - `process_followup_campaign`: Bulk processor for eligible invoices
    - `scheduled_followups`: Periodic task to run every 15 minutes (via Celery Beat)
  - **Database-backed templates**: Template model supports system defaults and user customizations
  - **Comprehensive tests** (`tests/test_email.py`):
    - EmailTemplateRenderer with Jinja2
    - SMTPSender with mocked SMTP
    - `send_followup_email` function with database fixtures
    - Celery task logic and queuing behavior
    - Template file existence and variable validation
  - **Professional email templates**: Responsive HTML templates with inline styling, company branding, payment buttons, and legal compliance footers
- [x] **Task 3.3**: AI-powered dispute letter drafting
  - **Dispute letter generator** (`src/ai/dispute_drafter.py`) with support for:
    - OpenAI GPT-4 Turbo (`gpt-4-turbo-preview`)
    - Anthropic Claude 3 Opus (`claude-3-opus-20240229`)
  - **Three letter types**:
    - `formal_dispute`: Professional payment dispute letter with 14-day deadline
    - `small_claims_prep`: Court preparation document with case summary and evidence
    - `demand_letter`: Urgent final demand with 7-day deadline and payment plan option
  - **Prompt engineering**: Context-aware prompts that include:
    - Invoice details (number, client, amount, dates, status)
    - Evidence timeline (communications, payments, attempts)
    - Legal references and formatting requirements
    - Output format specification (HTML)
  - **Cost tracking**: Automatic token counting and USD cost calculation
    - GPT-4 Turbo: $0.01/1K input + $0.03/1K output
    - Claude 3 Opus: $0.015/1K input + $0.075/1K output
  - **Provider fallback**: Configurable preference (OpenAI prioritized if both keys present)
  - **Comprehensive test suite** (`tests/test_dispute_drafter.py`):
    - Provider initialization and error handling
    - Prompt building verification for each letter type
    - API mocking for both OpenAI and Anthropic
    - Cost calculation accuracy
    - Evidence formatting and recipient handling
- [x] **Task 3.4**: PDF generation for dispute letters and small claims forms ✓ **COMPLETED**
  - **PDF Generator** (`src/pdf/generator.py`) using WeasyPrint (HTML → PDF)
  - **Two professional templates**:
    - `dispute_letter.html`: Formal dispute letter with sender/recipient info, invoice details, evidence log, payment instructions, and legal notices
    - `small_claims_form.html`: Court preparation packet with case summary, timeline, evidence list, damages calculation, witness information, filing instructions, and presentation tips
  - **Template rendering**: Jinja2-based with strict variable checking to ensure all required context is provided
  - **Flexible output**: Save to file path or return PDF bytes for S3/cloud storage upload
  - **Customization**: Support for custom CSS, page sizes (A4, Letter), and margins
  - **Comprehensive tests** (`tests/test_pdf.py`) with 11 passing tests:
    - PDF generation from raw HTML
    - Template rendering with context
    - Error handling for missing variables/templates
    - Custom formatting (margins, page size, CSS)
    - Multiple generation scenarios


### Completed Deliverables

1. **`schema.sql`**: Complete PostgreSQL migration script with:
   - Users, invoices, payment connections, templates
   - Campaigns, A/B tests, email events, webhooks
   - Audit logs, refresh tokens, system metrics
   - Triggers for auto-updating timestamps
   - Functions for business logic (`check_invoice_limit`, `calculate_recovery_rate`, `get_overdue_count`)
   - Materialized views for common queries
   - Encryption extension support for security

2. **`docs/database-er-diagram.md`**: Detailed documentation including:
   - Visual ER diagram with relationship cardinalities
   - Table descriptions with column types and purposes
   - Index strategy and performance notes
   - Security policies (RLS)
   - Migration and rollback instructions

## Getting Started (Local Development)

### Prerequisites

- Python 3.11+
- Git
- Docker & Docker Compose (recommended for database and Redis)

### Quick Start (Using Docker Compose)

The fastest way to get started is using Docker Compose, which spins up PostgreSQL and Redis:

```bash
# 1. Start database and Redis
docker-compose up -d postgres redis

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment configuration
cp .env.example .env
# Edit .env if needed (defaults work for local Docker setup)

# 4. Run database migrations
# (Alembic will be configured in upcoming tasks; for now, tables are created on startup)

# 5. Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 6. In another terminal, start Celery worker
celery -A src.celery_app worker --loglevel=info

# 7. In another terminal, start Celery beat scheduler
celery -A src.celery_app beat --loglevel=info
```

Access the API at http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc.

### Manual Setup (Without Docker)

If you prefer to run PostgreSQL and Redis locally without Docker:

```bash
# 1. Install and start PostgreSQL and Redis on your system

# 2. Create the database
createdb invoice_resolver

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your local database and Redis URLs

# 5. Start services (same as above)
uvicorn src.main:app --reload
celery -A src.celery_app worker --loglevel=info
celery -A src.celery_app beat --loglevel=info
```

### Configuration

Create a `.env` file from `.env.example` and configure:

- **Database**: `DATABASE_URL` (PostgreSQL connection string)
- **JWT**: `SECRET_KEY` for token signing
- **Payment APIs**: Stripe, PayPal, Plaid credentials
- **AI**: `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` for dispute letter generation
- **Email**: SMTP settings for sending follow-ups
- **Redis**: `REDIS_URL` for Celery task queue

See `.env.example` for all available options.

### Project Structure

```
.
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py            # FastAPI application entry point
│   └── core/
│       ├── config.py      # Settings management (pydantic-settings)
│       └── logger.py      # Logging configuration
├── docs/                  # Documentation
├── schema.sql             # Database schema (Phase 1.1)
└── TASKS.md               # Development task list
```

### Current Status

- ✅ Phase 1.1: Database schema design complete
- ✅ Phase 1.2: FastAPI project structure initialized
- 🔄 Phase 1.3: PostgreSQL setup (next task)
- 🔄 Phase 1.4: API documentation outline (pending)

## API Overview (Planned)

### Public Endpoints

- `POST /register` - User registration
- `POST /login` - JWT authentication
- `POST /refresh` - Refresh token rotation

### Protected Endpoints

- `GET|POST /invoices` - Invoice CRUD with filters
- `GET /invoices/{id}` - Retrieve invoice details
- `PATCH /invoices/{id}/status` - Update payment status
- `POST /templates` - Create custom email templates
- `GET|POST /campaigns` - Campaign management
- `GET /analytics/recovery-rate` - KPI metrics

### Webhook Endpoints

- `POST /webhooks/stripe` - Stripe event receiver
- `POST /webhooks/paypal` - PayPal IPN handler
- `POST /webhooks/plaid` - Plaid transaction sync

### Admin Endpoints (Admin only)

- `GET /admin/users` - List all users
- `GET /admin/metrics` - System health metrics
- `POST /admin/users/{id}/tier` - Change subscription tier

## Database Schema Highlights

### Tables (11 core tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | Account management | subscription_tier, invoice_limit |
| `payment_connections` | Encrypted credentials | provider (stripe/paypal/plaid) |
| `invoices` | Invoice records | status, stripe_payment_intent_id |
| `templates` | Email/document templates | type, variables (JSON) |
| `campaigns` | Campaign tracking | ab_test_variant, paid_after_send |
| `ab_tests` | Experiment definitions | test_type, variants (JSON) |
| `email_events` | Engagement tracking | event_type, occurred_at |
| `webhook_events` | Idempotency store | provider, event_id (unique) |
| `audit_logs` | Compliance logging | action, old_values, new_values |
| `refresh_tokens` | JWT rotation | token_hash, expires_at |
| `system_metrics` | Time-series data | metric_name, metric_value |

### Key Features

- **UUID primary keys** for security and distributed systems
- **JSONB columns** for flexible metadata storage
- **Partial indexes** on frequently queried external IDs
- **Row Level Security** for multi-tenant isolation
- **Encrypted credentials** for payment provider integrations
- **Audit trail** for all data changes
- **Idempotent webhook processing** via unique constraints
- **Automatic timestamp updates** via triggers
- **Materialized views** for dashboard performance

## Environment Variables

To be documented once implemented (after Task 1.2).

## Testing

Test suite will be implemented in Phase 5 using pytest with >80% coverage.

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Deployment

Production deployment instructions will be added in Phase 5 (Docker, cloud hosting, CI/CD).

## License

To be determined.

## Contact

For questions or feedback about this project, please open an issue on GitHub.
