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

## Billing & Subscriptions

The application includes a complete Stripe Billing integration for managing user subscriptions and handling payment disputes.

### Plans

- **Free**: 5 invoices per month (default)
- **Pro**: $19/month unlimited invoices, AI dispute drafting, A/B testing, priority support
- **Legal Pack Add-on**: $5/month (premium legal templates, small claims forms)
- **Multi-Currency Add-on**: $3/month (multiple currencies, auto conversion)

### Environment Variables

Configure these in your `.env` file:

```bash
# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_FREE=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_LEGAL_PACK=price_...
STRIPE_PRICE_MULTI_CURRENCY=price_...
```

### API Endpoints

- `GET /billing/plans` – List available subscription plans
- `POST /billing/checkout` – Create a Stripe Checkout session for a plan
- `GET /billing/subscription` – Get current user's subscription status
- `GET /billing/invoice-limit` – Get invoice limit based on subscription tier
- `POST /billing/webhook` – Stripe webhook endpoint (handle signature verification)

### Webhook Events

The system automatically handles:

- `customer.subscription.updated` – Updates user's subscription tier
- `customer.subscription.deleted` – Downgrades user to Free tier
- `checkout.session.completed` – Logs successful subscription signup

### How It Works

1. User selects a plan and clicks "Subscribe"
2. Frontend calls `/billing/checkout` to create a Stripe Checkout session
3. User completes payment on Stripe's hosted page
4. Stripe sends webhook to `/billing/webhook`
5. System updates `user.subscription_tier` and `user.invoice_limit` accordingly
6. Subscription status is available via `/billing/subscription`

### Testing

The `tests/test_billing.py` module provides comprehensive test coverage (19 tests) for:

- Plan lookups by price ID and tier
- Checkout session creation (with existing customer reuse)
- Subscription info retrieval from Stripe API
- Invoice limit calculation
- Webhook event handling (signature verification, subscription updates)

Set test environment variables in `tests/conftest.py` before running pytest.

## Project Structure

```
.
├── README.md                    # Project documentation
├── TASKS.md                     # Development task list (track progress)
├── schema.sql                   # PostgreSQL database schema
├── docs/
│   └── database-er-diagram.md  # ER diagram and table docs
├── .github/
│   └── workflows/
│       └── test.yml            # CI pipeline (to be created)
├── src/                        # Source code
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Configuration, logging
│   ├── models/                 # SQLAlchemy models
│   ├── integrations/           # Stripe/PayPal/Plaid clients
│   ├── mail/                   # Email automation
│   ├── ai/                     # AI dispute drafter
│   ├── pdf/                    # PDF generator
│   ├── dashboard/              # Streamlit app
│   ├── ab_testing/             # A/B testing framework
│   ├── admin/                  # Admin panel
│   ├── billing/                # Stripe billing
│   ├── tasks/                  # Celery tasks
│   └── utils/                  # Helper functions
├── tests/                      # Test suite (pytest)
├── docker-compose.yml          # Local development (PostgreSQL, Redis only)
├── docker-compose.prod.yml     # Full production stack
├── Dockerfile                  # FastAPI application container (multi-stage)
├── Dockerfile.celery           # Celery worker/beat container (multi-stage)
├── requirements.txt            # Python dependencies
├── secrets/                    # Docker secrets (gitignored, create manually)
│   ├── postgres_password.txt
│   ├── jwt_secret.txt
│   ├── stripe_webhook_secret.txt
│   ├── paypal_client_secret.txt
│   ├── openai_api_key.txt
│   └── redis_password.txt
├── scripts/
│   └── init-secrets.sh        # Initialize production secrets
├── logs/                       # Application logs (mounted volume)
├── media/                      # Uploaded files (mounted volume)
├── backups/                    # Database backups (mounted volume)
└── .env.example                # Environment variables template
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

### Running the Dashboard

The Streamlit dashboard provides a user-friendly interface for managing invoices and tracking campaigns.

```bash
# Install dashboard dependencies
pip install streamlit streamlit-authenticator plotly pandas

# Set API URL (optional, defaults to http://localhost:8000)
export API_BASE_URL=http://localhost:8000

# Run the dashboard
streamlit run dashboard/app.py
```

Access the dashboard at http://localhost:8501. Login with credentials you created via the registration API at http://localhost:8000/api/auth/register.

**Admin Access:**
By default, registered users are not admins. To grant admin privileges:
1. Set `is_admin=true` in the database for the user, OR
2. Extend the registration endpoint to accept an admin flag (for initial setup)

Admin users will see an additional "🛡️ Admin" menu in the sidebar with full system management capabilities.

**Dashboard Features:**
- **Overview**: View KPIs (total invoices, recovery rate, overdue count)
- **Invoices**: Browse and filter invoices, update status inline
- **Campaigns**: Track email campaign performance and A/B test results
- **Settings**: Manage payment connections (Stripe, PayPal, Plaid)

**Admin Dashboard** (Admin users only):
- **Dashboard**: System overview with user counts, invoice stats, connection stats
- **Users**: View all users, search/filter by tier/status, update subscription tiers
- **Metrics**: System health monitoring including Celery workers, API latency, errors
- **Webhooks**: View recent webhook events with filtering by provider/status
- **Connections**: See all payment provider connections across users


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

## Docker Containerization

The application is fully containerized with multi-stage builds for optimized production images.

### Architecture

- **FastAPI Application** (`Dockerfile`): Multi-stage build with Python 3.12, non-root user, health checks
- **Celery Worker** (`Dockerfile.celery`): Separate container for background tasks
- **Celery Beat** (`Dockerfile.celery`): Scheduler for periodic tasks
- **PostgreSQL**: With pg_stat_statements for query performance monitoring
- **Redis**: With password protection and memory limits

### Development (Docker Compose)

```bash
# Start only database and Redis (app runs locally)
docker-compose up -d postgres redis

# View logs
docker-compose logs -f postgres redis

# Stop services
docker-compose down
```

### Production Deployment

Production uses `docker-compose.prod.yml` with Docker secrets for sensitive data and enhanced security.

#### 1. Initialize Secrets

```bash
# Run the initialization script
chmod +x scripts/init-secrets.sh
./scripts/init-secrets.sh

# Manually edit the generated secrets and add your actual API keys
# - secrets/openai_api_key.txt
# - secrets/paypal_client_secret.txt (if using PayPal)
```

#### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your production settings:
# - DEBUG=false
# - LOG_LEVEL=INFO
# - WORKERS=4
# - API_PORT=8000
# - Any other non-secret configuration
```

#### 3. Start Production Stack

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs for all services
docker-compose -f docker-compose.prod.yml logs -f

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Stop all services
docker-compose -f docker-compose.prod.yml down
```

#### 4. Access the Application

- API: http://localhost:8000 (or your server IP)
- Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

#### 5. Production Management

```bash
# Restart a specific service
docker-compose -f docker-compose.prod.yml restart api

# View logs for a specific service
docker-compose -f docker-compose.prod.yml logs -f api

# Execute a command in a container
docker-compose -f docker-compose.prod.yml exec api python -c "import sys; print(sys.version)"

# Stop and remove everything (including volumes - CAREFUL!)
docker-compose -f docker-compose.prod.yml down -v
```

### Secrets Management

Production uses Docker secrets to securely inject sensitive data:

**Secret Files** (in `./secrets/`):
- `postgres_password.txt` - PostgreSQL database password
- `jwt_secret.txt` - JWT signing key (min 64 characters)
- `stripe_webhook_secret.txt` - Stripe webhook signing secret
- `paypal_client_secret.txt` - PayPal REST API secret
- `openai_api_key.txt` - OpenAI API key
- `redis_password.txt` - Redis authentication password

**Important**: The `secrets/` directory is gitignored. Never commit actual secrets to version control.

To rotate a secret:
1. Generate a new value
2. Update the corresponding file in `secrets/`
3. Restart affected services: `docker-compose -f docker-compose.prod.yml restart`

### Security Features

- **Non-root containers**: All services run as UID 1001 (invoice user)
- **Resource limits**: CPU and memory constraints on each service
- **Health checks**: Automatic container restart on failure
- **Secrets isolation**: Sensitive data mounted as read-only files
- **Network isolation**: Dedicated Docker bridge network
- **Automatic restarts**: All services use `restart: always`

### Backup and Recovery

**Database Backup**:
```bash
# Create a backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres invoice_resolver > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres invoice_resolver < backups/backup_20260321_120000.sql
```

Backups are automatically saved to `./backups/` directory (mounted to `/backups` in container).

### Monitoring

**System Health**:
- FastAPI health endpoint: `GET /health`
- Celery worker status: `docker-compose -f docker-compose.prod.yml logs celery-worker`
- Redis connection: `docker-compose -f docker-compose.prod.yml exec redis redis-cli ping`

**Logs**: All service logs are mounted to `./logs/` directory for persistence.

### Troubleshooting

**Services won't start**:
- Check secrets directory exists and files are readable: `ls -la secrets/`
- Verify no port conflicts: `netstat -tulpn | grep :8000`
- Check logs: `docker-compose -f docker-compose.prod.yml logs`

**Database connection errors**:
- Ensure PostgreSQL is healthy: `docker-compose -f docker-compose.prod.yml ps postgres`
- Verify DATABASE_URL in `.env` matches credentials

**Celery tasks not running**:
- Check Redis connectivity: `docker-compose -f docker-compose.prod.yml exec celery-worker celery -A src.celery_app:celery_app inspect ping`
- Verify worker logs for errors

### Multi-stage Build Optimization

The Dockerfiles use multi-stage builds to keep production images small:

1. **Builder stage**: Installs dependencies to a virtual environment
2. **Final stage**: Copies only the virtual environment and application code
3. **Result**: Final image contains only runtime dependencies, no build tools

Typical image sizes:
- FastAPI: ~180MB (vs ~500MB for single-stage)
- Celery worker: ~160MB

### CI/CD

GitHub Actions workflow runs tests on every push to main/develop branches. Production deployment can be automated with additional workflows for:
- Docker image build and push to registry
- Database migrations
- Zero-downtime deployment with health checks

## License

To be determined.

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

Comprehensive test suite with >80% coverage using pytest.

```bash
# Run tests locally
pytest tests/ -v --cov=src --cov-report=html

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_email.py -v
```

### Test Coverage

The test suite includes:

- **Unit tests** for all services (email, AI, PDF) with mocked external APIs
- **Integration tests** for API endpoints using FastAPI TestClient
- **Database fixtures** with SQLite in-memory for isolated testing
- **Coverage reporting** with pytest-cov

### CI/CD

GitHub Actions automatically runs tests on every push and pull request across Python 3.11 and 3.12.

Key features:
- PostgreSQL service for realistic testing
- System dependencies installed for PDF generation (WeasyPrint)
- Ruff linting and Pyright type checking
- Security scanning with TruffleHog
- Artifact upload of coverage reports

See `.github/workflows/test.yml` for the full pipeline.

## Deployment

Invoice Resolver AI supports multiple deployment options with full CI/CD, SSL, automated backups, and monitoring.

### Quick Deploy (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/invoice-resolver-ai.git
cd invoice-resolver-ai
./scripts/init-secrets.sh
cp .env.example .env
# Edit .env with your API keys and domain names

# 2. Deploy to production (Docker Compose + Traefik)
./deploy.sh --production
```

That's it! The deploy script handles everything: builds, starts services, runs migrations, and verifies health.

### Deployment Options

#### Option 1: Docker Compose with Traefik (Self-Hosted)

**Best for**: Full control on your own VPS (Ubuntu 22.04+)

- Automatic SSL via Let's Encrypt
- Traefik reverse proxy with rate limiting
- Docker secrets for credential management
- Includes monitoring stack (Prometheus + Grafana)

**Setup**:

```bash
# Initialize secrets
./scripts/init-secrets.sh

# Edit configuration
cp .env.example .env
nano .env  # Set API_DOMAIN, DASHBOARD_DOMAIN, SSL_EMAIL, etc.

# Deploy
./deploy.sh --production

# Or deploy with monitoring stack:
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml -f docker-compose.monitoring.yml up -d
```

**Services**:
- API: `https://api.yourdomain.com:8000` (behind Traefik)
- Dashboard: `https://dashboard.yourdomain.com:8501`
- Prometheus: `https://prometheus.yourdomain.com:9090`
- Grafana: `https://grafana.yourdomain.com:3000` (admin password in `secrets/grafana_admin_password.txt`)

**Updating**:
```bash
git pull origin main
./deploy.sh --production --no-build  # Rebuild anyway if code changed
```

#### Option 2: Fly.io (Platform-as-a-Service)

**Best for**: Quick global deployment with minimal ops

- Automatic SSL certificates
- Global edge network
- Free tier available
- No server management

**Setup**:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh
flyctl login

# Launch app (if first time)
flyctl launch invoice-resolver-ai --org personal --region ord --no-deploy

# Set secrets
flyctl secrets set \
  POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  JWT_SECRET_KEY=$(openssl rand -base64 64) \
  REDIS_PASSWORD=$(openssl rand -base64 32) \
  STRIPE_WEBHOOK_SECRET=whsec_... \
  OPENAI_API_KEY=sk-... \
  DATABASE_URL=postgresql://...  # Use Fly's Postgres or external

# Deploy
flyctl deploy --remote-only

# Run migrations
flyctl ssh console -C "alembic upgrade head"
```

**Note**: Fly.io requires external Redis/PostgreSQL or use Fly's managed services. Redis can run on same VM; use Postgres for production.

#### Option 3: AWS ECS / Kubernetes

For large-scale deployments, adapt Docker images to your orchestrator. The application is cloud-agnostic.

---

### Monitoring & Observability

#### Sentry (Error Tracking)

Sentry is built-in. To enable:

1. Create project at https://sentry.io/new
2. Add DSN to `.env`: `SENTRY_DSN=https://public_key@host/project_id`
3. Redeploy

Sentry automatically captures:
- Unhandled exceptions
- Performance traces (with sampling)
- Celery task failures

Configure alerts in Sentry dashboard for new issues, error spikes, and user impact.

#### Prometheus Metrics

Metrics endpoint: `GET /metrics` (Prometheus format)

**Metrics collected**:
- HTTP request count by method, path, status code
- Request duration histograms (p50, p95, p99)
- Application uptime (via health checks)

**Deploy monitoring stack**:

```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml -f docker-compose.monitoring.yml up -d
```

Grafana dashboards are pre-configured in `grafana/provisioning/`. Access Grafana at `https://grafana.yourdomain.com` (admin password in secrets).

**Metrics to alert on**:
- `http_requests_total{status_code=~"5.."}` > 10/min (error rate)
- `http_request_duration_seconds{quantile="0.99"}` > 2s (latency SLA)
- `up{job="invoice-resolver-api"}` == 0 (service down)

#### Health Checks

All services expose health endpoints for load balancers:
- API: `/health` → `{"status": "healthy", "service": "Invoice Resolver AI"}`
- Dashboard: `/_stcore/health` (Streamlit)
- Celery: `celery -A src.celery_app inspect ping`

---

### Automated Backups

Database backups are automated via Celery Beat daily at 2 AM UTC.

**Backup retention**: 30 days (configurable in `src/tasks/backup.py`)

**Backup location**: `./backups/` directory (persisted volume)

**Manual backup**:
```bash
./deploy.sh --backup  # Creates backup before deploying
# Or trigger task directly:
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A src.celery_app:celery_app call tasks.backup.run_backup
```

**Restore from backup**:
```bash
# List backups
ls -lh backups/

# Restore (overwrites current data!)
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "
from tasks.backup import run_restore
run_restore('backups/backup_20260321_020000.sql.gz')
"
```

**Offsite backups** (recommended for production):
```bash
# Sync to S3 daily (add to crontab or use GitHub Action)
aws s3 sync ./backups/ s3://your-bucket/invoice-resolver-backups/ --delete

# Or use rclone for other cloud providers
rclone sync backups/ remote:backup-bucket/invoice-resolver/ --progress
```

---

### CI/CD Pipeline

GitHub Actions workflows automate testing and deployment:

**Workflows**:
- `.github/workflows/test.yml` - Runs tests on every push (Python 3.11 & 3.12), linting, security scanning
- `.github/workflows/deploy-staging.yml` - Auto-deploys to staging on `develop` branch
- `.github/workflows/deploy-production.yml` - Manual production deployment with approval

**CI Checks**:
- ✅ Unit tests (>80% coverage target)
- ✅ Integration tests with real PostgreSQL
- ✅ Ruff linting + Pyright type checking
- ✅ TruffleHog secret scanning
- ✅ System dependency verification (for PDF generation)

**Deployment Workflow**:

1. Push to `develop` → Auto-deploys to staging
2. Create PR to `main` → CI runs full test suite
3. Merge to `main` → Manual production deployment via GitHub Actions UI
4. Production deployment requires admin approval and allows canary releases

**Customizing CI/CD**: Edit workflow files in `.github/workflows/`. The deploy workflows are flexible and can be adapted for Heroku, AWS, or custom scripts.

---

### SSL/TLS

SSL is automatically handled:

- **Traefik** (Docker Compose): Uses Let's Encrypt ACME challenge. Certificates auto-renew.
- **Fly.io**: Built-in SSL via `https://` enforced. No configuration needed.
- **Custom load balancer**: Upload your certificates or use ACME provider.

Ensure ports 80 and 443 are open in firewall for Let's Encrypt validation.

---

### Security Best Practices

1. **Use strong secrets**: Run `scripts/init-secrets.sh` to generate cryptographically secure passwords
2. **Never commit secrets**: All secrets go in `secrets/` (gitignored) and `.env` (gitignored)
3. **Rotate regularly**: Change JWT_SECRET_KEY, API keys quarterly
4. **Enable firewall**: Only expose ports 80, 443, and SSH (if needed)
5. **Use non-root containers**: Docker images run as UID 1001 (enforced in Dockerfile)
6. **Database security**: Enable RLS policies (in schema.sql), use strong database passwords
7. **Monitor with Sentry**: Capture and alert on suspicious activity
8. **Keep updated**: Regularly update base images and dependencies

---

### Scaling

**Vertical Scale** (bigger server):
- Increase CPU/memory limits in `docker-compose.prod.yml` under `deploy.resources`
- Ensure server has sufficient resources

**Horizontal Scale** (more instances):
- API: Set `WORKERS` in `.env` (Gunicorn workers)
- Celery: `docker-compose up --scale celery-worker=3`
- Load balancer required (Traefik already load balances)

**Database Scale**:
- Use managed PostgreSQL (RDS, CloudSQL, Fly Postgres) for production
- Enable connection pooling (PgBouncer)
- Add read replicas for heavy read loads

**Redis Scale**:
- Use managed Redis (ElastiCache, Upstash) for high availability
- Enable Redis persistence (AOF/RDB)

---

### Troubleshooting Deployment

**Services fail to start**:
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs <service>

# Common issues:
# - Missing secrets: ls -la secrets/
# - Port conflicts: sudo netstat -tulpn | grep :80
# - Out of disk space: df -h
```

**SSL certificates not obtained**:
```bash
# Check Traefik logs
docker-compose -f docker-compose.traefik.yml logs traefik | grep -i acme

# Ensure DNS A record points to server IP
# Wait 30s and retry: docker-compose -f docker-compose.traefik.yml restart traefik
```

**Database migrations fail**:
```bash
# Check migration history
docker-compose -f docker-compose.prod.yml exec api alembic history

# Manually apply problematic migration with --sql output review first
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

**High memory usage**:
```bash
# Check container stats
docker stats

# Adjust memory limits in docker-compose.prod.yml
# For Celery workers, increase from 256M to 512M if needed
```

**Metrics not showing in Prometheus**:
```bash
# Verify /metrics endpoint is accessible
curl http://localhost:8000/metrics | head

# Check Prometheus targets: https://prometheus.yourdomain.com/targets
# API target should show "UP"
```

See [docs/deployment-runbook.md](./docs/deployment-runbook.md) for comprehensive troubleshooting guide.

## License

To be determined.

## Contact

For questions or feedback about this project, please open an issue on GitHub.
