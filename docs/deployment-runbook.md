# Deployment Runbook

This runbook provides step-by-step procedures for deploying, backing up, restoring, and monitoring the Invoice Resolver AI application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deployment Options](#deployment-options)
4. [Backup and Restore](#backup-and-restore)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

### Required Accounts and Services

- **Cloud Provider**: Fly.io account (or Heroku/AWS if using alternative)
- **Domain Name**: For SSL certificates (e.g., `yourdomain.com`)
- **Database**: PostgreSQL 15+ (managed or self-hosted)
- **Redis**: For Celery broker (included in Docker Compose)
- **Sentry**: For error tracking (optional but recommended)
- **Docker & Docker Compose**: Latest version
- **Git**: For CI/CD

### Environment Variables

Configure all required environment variables in `.env` file. See `.env.example` for full list.

Critical variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret for JWT token signing (min 64 chars)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `STRIPE_API_KEY`: Stripe secret key
- `SENTRY_DSN`: Sentry DSN for error tracking (optional)

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/invoice-resolver-ai.git
cd invoice-resolver-ai
```

### 2. Initialize Secrets

```bash
chmod +x scripts/init-secrets.sh
./scripts/init-secrets.sh
```

**Important**: Manually edit generated secrets:
- `secrets/openai_api_key.txt` - Add your OpenAI API key
- `secrets/paypal_client_secret.txt` - Add PayPal secret if using PayPal
- `secrets/stripe_webhook_secret.txt` - Add Stripe webhook secret

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your production values:
# - DEBUG=false
# - LOG_LEVEL=INFO
# - API_DOMAIN=api.yourdomain.com
# - DASHBOARD_DOMAIN=dashboard.yourdomain.com
# - TRAEFIK_HOST=traefik.yourdomain.com
# - SENTRY_DSN=your_sentry_dsn
```

### 4. Set Up DNS Records

For Traefik SSL (Let's Encrypt):
```
api.yourdomain.com    A    <your-server-ip>
dashboard.yourdomain.com A <your-server-ip>
traefik.yourdomain.com A <your-server-ip>
```

For Fly.io, DNS is managed automatically.

---

## Deployment Options

### Option A: Docker Compose with Traefik (Self-Hosted)

**Requirements**: Ubuntu 22.04+ server with Docker & Docker Compose

#### Deployment Steps

```bash
# 1. Transfer code to server
git clone <repository-url>
cd invoice-resolver-ai
git checkout main

# 2. Initialize secrets if not already done
./scripts/init-secrets.sh

# 3. Edit .env with production values
nano .env

# 4. Set EMAIL_URL and other app-specific configs

# 5. Pull latest images (optional, uses local build)
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml pull

# 6. Build and start all services
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml up -d

# 7. Run database migrations (if using Alembic)
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 8. Verify all services are running
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml ps

# 9. Check logs for errors
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml logs -f
```

#### Services Exposed

- **API**: `https://api.yourdomain.com` (port 8000)
- **Dashboard**: `https://dashboard.yourdomain.com` (port 8501)
- **Traefik Dashboard**: `https://traefik.yourdomain.com/api` (for admin)
- **Prometheus**: `https://prometheus.yourdomain.com` (if monitoring stack enabled)
- **Grafana**: `https://grafana.yourdomain.com` (if monitoring stack enabled)

#### Updating Deployment

```bash
git pull origin main
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml build --no-cache api
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml up -d
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml exec api alembic upgrade head
```

---

### Option B: Fly.io (Platform-as-a-Service)

**Requirements**: Fly.io account, `flyctl` CLI installed

#### Deployment Steps

```bash
# 1. Install flyctl and login
curl -L https://fly.io/install.sh | sh
flyctl login

# 2. Initialize Fly.io app (if not already done)
flyctl launch invoice-resolver-ai --org personal --region ord --no-deploy

# 3. Set secrets (environment variables)
flyctl secrets set \
  POSTGRES_USER=postgres \
  POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  JWT_SECRET_KEY=$(openssl rand -base64 64) \
  REDIS_PASSWORD=$(openssl rand -base64 32) \
  STRIPE_WEBHOOK_SECRET=whsec_... \
  PAYPAL_CLIENT_SECRET=... \
  OPENAI_API_KEY=sk-... \
  DATABASE_URL=postgresql://... (if using external DB)

# 4. Set app configuration
flyctl scale count 1  # Start with 1 instance
flyctl ips allocate-v4  # Allocate IPv4 address
flyctl ips allocate-v6  # Allocate IPv6 address

# 5. Deploy
flyctl deploy --remote-only

# 6. Run database migrations
flyctl ssh console
# Inside container: alembic upgrade head
exit

# 7. View logs
flyctl logs

# 8. Open in browser
flyctl open
```

**Notes**:
- Fly.io automatically provisions SSL certificates
- Redis and PostgreSQL need to be external (or use Fly's Postgres offering)
- Set up volumes for persistent storage if needed: `flyctl volumes create media --size 1`

---

### Option C: AWS ECS / Heroku

Consult specific platform documentation. Generally:
1. Build and push Docker images to container registry
2. Configure environment variables and secrets
3. Deploy containers/services
4. Set up load balancer with SSL
5. Configure autoscaling if needed

---

## Backup and Restore

### Automated Daily Backups

Backups are configured to run daily at 2 AM UTC via Celery Beat.

**Backup Retention**: 30 days (configurable in `tasks/backup.py`)

**Backup Location**: `./backups/` directory (mounted to `/app/backups` in containers)

#### Manual Backup

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "
from tasks.backup import run_backup
result = run_backup()
print(f'Backup: {result}')
"

# Or create a Celery task:
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A src.celery_app:celery_app call tasks.backup.run_backup
```

#### Restore from Backup

**⚠️ WARNING**: Restoring will overwrite existing data. Always test restore on staging first.

```bash
# List available backups
ls -lh backups/

# Restore to current database
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "
from tasks.backup import run_restore
run_restore('backups/backup_20260321_020000.sql.gz')
"

# Or restore to different database (for testing)
docker-compose -f docker-compose.prod.yml exec -T postgres bash -c 'createdb invoice_resolver_test'
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "
from tasks.backup import run_restore
run_restore('backups/backup_20260321_020000.sql.gz', target_db='invoice_resolver_test')
"
```

#### Download Backup from Server

```bash
scp user@server:/path/to/invoice-resolver-ai/backups/backup_20260321_020000.sql.gz ~/backups/
```

#### Automated Offsite Backup (Optional)

Configure `rclone` or AWS CLI to sync backups to S3/Cloud storage:

```bash
# Example: Sync to S3 daily (add to crontab)
aws s3 sync ./backups/ s3://your-bucket/invoice-resolver-backups/ --delete
```

---

## Monitoring and Alerting

### Sentry (Error Tracking)

Sentry is integrated into the application. Errors are automatically captured when `SENTRY_DSN` is set.

**Setup**:
1. Create project at https://sentry.io/new
2. Copy DSN to `.env`: `SENTRY_DSN=https://xxxx@sentry.io/xxxx`
3. Redeploy to activate

**Alerts**:
- Configure email/Slack alerts in Sentry for:
  - New issues with >5 occurrences in 1 hour
  - Critical-level errors
  - User impact alerts

### Prometheus Metrics

The API exposes metrics at `GET /metrics` (Prometheus format).

**Metrics include**:
- `http_requests_total`: Total HTTP requests by method, path, status
- `http_request_duration_seconds`: Request latency histogram

#### Deploying Prometheus + Grafana

Use `docker-compose.monitoring.yml`:

```bash
# Start monitoring stack
docker-compose -f docker-compose.prod.yml -f docker-compose.traefik.yml -f docker-compose.monitoring.yml up -d

# Access Grafana
# URL: https://grafana.yourdomain.com
# Default admin password: from ./secrets/grafana_admin_password.txt

# Add Prometheus data source:
# URL: http://prometheus:9090
# Then import dashboard from grafana/provisioning/dashboards/
```

#### Key Dashboards

- **API Performance**: Request rate, error rate, latency (95th, 99th percentiles)
- **System Health**: CPU, memory, disk usage per service
- **Business Metrics**: Invoice count, recovery rate (custom queries)

### Health Checks

All services expose health endpoints:

- **API**: `GET https://api.yourdomain.com/health`
- **Dashboard**: `GET https://dashboard.yourdomain.com/_stcore/health`
- **Celery Worker**: `celery -A src.celery_app inspect ping`

Use these for load balancer health checks and monitoring uptime.

### Logs

All logs are persisted to `./logs/` directory. Centralized logging options:

- **Local tail**: `docker-compose -f docker-compose.prod.yml logs -f <service>`
- **Cloud logging**: Configure Docker logging drivers to send to ELK/Graylog/Loki
- **Sentry**: Already capturing error logs

---

## Troubleshooting

### Services Won't Start

**Check secrets**:
```bash
ls -la secrets/
# Ensure all required secret files exist and are readable
```

**Check port conflicts**:
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

**View logs**:
```bash
docker-compose -f docker-compose.prod.yml logs <service-name>
```

### Database Connection Errors

```bash
# Check PostgreSQL health
docker-compose -f docker-compose.prod.yml ps postgres
docker-compose -f docker-compose.prod.yml logs postgres

# Verify DATABASE_URL in .env matches credentials
# Default: postgresql://postgres:<password>@postgres:5432/invoice_resolver
```

### Celery Tasks Not Running

```bash
# Check Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a $(cat secrets/redis_password) ping

# Inspect Celery workers
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A src.celery_app inspect ping

# Restart Celery services
docker-compose -f docker-compose.prod.yml restart celery-worker celery-beat
```

### SSL/TLS Certificate Errors

Traefik automatically obtains certificates from Let's Encrypt.

**Check certificate status**:
```bash
# View Traefik logs
docker-compose -f docker-compose.traefik.yml logs traefik

# Common issues:
# - DNS not pointing to server yet
# - Port 80/443 blocked by firewall
# - Rate limits from Let's Encrypt (wait 1 hour)
```

**Force certificate renewal**:
```bash
docker-compose -f docker-compose.traefik.yml exec traefik traefik certificates-get --providers.docker
```

### Backup Failures

```bash
# Check backup task logs
docker-compose -f docker-compose.prod.yml logs celery-worker | grep "backup"

# Test backup manually
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "from tasks.backup import run_backup; print(run_backup())"

# Disk space check
docker-compose -f docker-compose.prod.yml exec postgres df -h
```

### High Memory Usage

```bash
# Check container resource usage
docker stats

# If Redis uses too much memory, adjust limits in docker-compose.prod.yml:
# --maxmemory 256mb -> increase or decrease as needed
```

---

## Maintenance

### Rotating Secrets

1. Generate new secret:
   ```bash
   openssl rand -base64 32 | tr -d '\n' > secrets/jwt_secret.txt
   ```

2. Restart affected services:
   ```bash
   docker-compose -f docker-compose.prod.yml restart api celery-worker
   ```

Note: Rotating JWT_SECRET will invalidate existing tokens. Users will need to re-login.

### Database Migration (Schema Changes)

```bash
# 1. Generate migration
alembic revision --autogenerate -m "Add new column to invoices"

# 2. Review migration file in alembic/versions/

# 3. Apply migration
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 4. Verify
docker-compose -f docker-compose.prod.yml exec api python -c "from models import inspect; print(inspect(engine))"
```

### Updating Dependencies

```bash
# Update requirements.txt
pip install --upgrade pip-tools
pip-compile --upgrade-package fastapi --upgrade-package sqlalchemy requirements.in
pip-sync requirements.txt

# Rebuild and redeploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

**Scale API workers**:
Edit `.env`: `WORKERS=8` and redeploy

**Scale Celery workers**:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

**Horizontal scaling with Docker Swarm/K8s**: Consider orchestrator for production.

---

## Emergency Procedures

### Database is Down

1. Check PostgreSQL logs: `docker-compose -f docker-compose.prod.yml logs postgres`
2. Restart PostgreSQL: `docker-compose -f docker-compose.prod.yml restart postgres`
3. If data corruption suspected, **DO NOT RESTART**. Contact DBA and restore from latest backup.

### Application Unresponsive

1. Check API logs: `docker-compose -f docker-compose.prod.yml logs api`
2. Restart API: `docker-compose -f docker-compose.prod.yml restart api`
3. Check resource limits: `docker stats`
4. If Celery backed up, restart worker: `docker-compose -f docker-compose.prod.yml restart celery-worker`

### Security Incident

1. Revoke all JWT tokens by changing `JWT_SECRET_KEY`
2. Rotate all API keys (Stripe, PayPal, OpenAI, etc.)
3. Review logs for suspicious activity
4. Check database for unauthorized access
5. Notify users if data breach suspected

---

## Contact Information

- **On-Call Engineer**: [PagerDuty/Opsgenie contact]
- **DevOps Lead**: [Contact info]
- **Emergency Database Access**: [Instructions]

---

## Appendix

### Useful Commands

```bash
# View all containers
docker-compose -f docker-compose.prod.yml ps

# View logs for all services
docker-compose -f docker-compose.prod.yml logs -f

# Execute command in container
docker-compose -f docker-compose.prod.yml exec api python -c "print('Hello')"

# Backup database manually
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres invoice_resolver > backup_manual.sql

# Restore database manually
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres invoice_resolver < backup_manual.sql

# Check disk usage
docker-compose -f docker-compose.prod.yml exec postgres df -h

# Clean up unused Docker resources
docker system prune -a --volumes
```

### Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `API_DOMAIN` | API hostname | `api.local` |
| `DASHBOARD_DOMAIN` | Dashboard hostname | `dashboard.local` |
| `TRAEFIK_HOST` | Traefik hostname | `traefik.local` |
| `SSL_EMAIL` | Email for Let's Encrypt | `admin@example.com` |
| `WORKERS` | Number of Gunicorn workers | `4` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

**Last Updated**: 2026-03-21  
**Version**: 1.0
