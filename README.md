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

### Setup

The project foundation is now in place. To get started:

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Set up environment configuration
cp .env.example .env
# Edit .env with your database and API credentials (see Configuration section)

# 3. Start the development server
python -m src.main
# or
uvicorn src.main:app --reload

# 4. Access the API
# API documentation: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### Configuration

Create a `.env` file from `.env.example` and configure:

- **Database**: `DATABASE_URL` (PostgreSQL connection string)
- **JWT**: `SECRET_KEY` for token signing
- **Payment APIs**: Stripe, PayPal, Plaid credentials
- **AI**: `OPENAI_API_KEY` for dispute letter generation
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
