# Invoice Resolver AI - Database ER Diagram

## Overview

This document provides an Entity-Relationship (ER) diagram and description of the PostgreSQL database schema for the Invoice Resolver AI application.

## Entity Relationship Diagram

```
┌─────────────────┐      1 ┌──────────────────┐
│    users        │◄────────┤  payment_        │
│─────────────────│        │  connections     │
│ id (PK)         │       ┌┤ id (PK)          │
│ email           │       │ │ user_id (FK)     │
│ password_hash   │       │ │ provider         │
│ full_name       │       └─┤ credentials_enc  │
│ company_name    │         │ external_account │
│ subscription_   │         │ is_active        │
│   tier          │         └──────────────────┘
│ invoice_limit   │
│ is_active       │
│ is_admin        │
└───────┬─────────┘
        │
        │ 1
        │
        ▼
┌─────────────────┐      1 ┌──────────────────┐
│   invoices      │◄────────┤   campaigns      │
│─────────────────│        │──────────────────│
│ id (PK)         │       ┌┤ id (PK)          │
│ user_id (FK)    │       │ │ user_id (FK)    │
│ invoice_number  │       │ │ template_id (FK)│
│ client_name     │       │ │ invoice_id (FK) │
│ amount          │       │ │ scheduled_send  │
│ status          │       │ │ sent_at         │
│ due_date        │       │ │ opened_at       │
│ stripe_pi_id    │       │ │ paid_after_send │
│ paypal_txn_id   │       └─┤ ab_test_variant │
│ plaid_acc_id    │         └──────────────────┘
│ paid_date       │
└───────┬─────────┘
        │
        │
        │ N
        │
        └──────────┐
                   │
                   │ M
                   ▼
        ┌──────────────────┐
        │    templates     │
        │──────────────────│
        │ id (PK)          │
        │ user_id (FK)     │
        │ is_system        │
        │ name             │
        │ type             │
        │ subject          │
        │ body_html        │
        └──────────────────┘

┌─────────────────┐
│    ab_tests     │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ name            │
│ test_type       │
│ variants (JSON) │
│ is_active       │
│ started_at      │
└─────────────────┘

┌─────────────────┐
│  email_events   │
│─────────────────│
│ id (PK)         │
│ campaign_id(FK) │
│ event_type      │
│ event_data(JSON)│
│ occurred_at     │
└─────────────────┘

┌─────────────────┐
│  webhook_events │
│─────────────────│
│ id (PK)         │
│ provider        │
│ event_id        │
│ signature_verif │
│ processing_     │
└─────────────────┘

┌─────────────────┐
│  audit_logs     │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ action          │
│ entity_type     │
│ entity_id       │
│ old_values(JSON)│
│ new_values(JSON)│
└─────────────────┘

┌─────────────────┐
│ refresh_tokens  │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ token_hash      │
│ expires_at      │
│ is_revoked      │
└─────────────────┘

┌─────────────────┐
│ system_metrics  │
│─────────────────│
│ id (PK)         │
│ metric_name     │
│ metric_value    │
│ labels(JSON)    │
│ recorded_at     │
└─────────────────┘
```

## Table Descriptions

### 1. `users`
Stores user account information, subscription tiers, and invoice limits.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique user email |
| password_hash | VARCHAR(255) | Bcrypt hashed password |
| subscription_tier | VARCHAR(50) | Plan level: free, pro, enterprise |
| invoice_limit | INTEGER | Monthly invoice allowance |
| is_active | BOOLEAN | Account status |
| is_admin | BOOLEAN | Admin privileges |

**Indexes:** email, subscription_tier, created_at

---

### 2. `payment_connections`
Stores encrypted credentials for Stripe, PayPal, and Plaid integrations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| provider | VARCHAR(50) | stripe, paypal, or plaid |
| credentials_encrypted | TEXT | Encrypted OAuth tokens/API keys |
| external_account_id | VARCHAR(500) | Provider-specific account ID |

**Indexes:** user_id, provider, is_active

**Constraint:** One active connection per user per provider

---

### 3. `invoices`
Core table storing invoice data with payment status and external provider references.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| invoice_number | VARCHAR(255) | Client-facing invoice number |
| client_name | VARCHAR(500) | Client company/person name |
| amount | DECIMAL(12,2) | Invoice total |
| status | VARCHAR(50) | draft, sent, paid, overdue, disputed, canceled |
| due_date | DATE | Payment due date |
| stripe_payment_intent_id | VARCHAR(500) | Stripe payment intent reference |
| paypal_txn_id | VARCHAR(500) | PayPal transaction reference |

**Indexes:** user_id, status, due_date, external IDs

---

### 4. `templates`
Stores email and document templates for follow-ups and dispute letters.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | NULL for system templates |
| is_system | BOOLEAN | True if built-in template |
| type | VARCHAR(50) | Template category |
| subject | VARCHAR(1000) | Email subject or document title |
| body_html | TEXT | HTML formatted content |
| body_text | TEXT | Plain text fallback |
| variables | JSONB | Array of variable placeholders |

**Indexes:** user_id, type, is_system

---

### 5. `campaigns`
Tracks email campaigns sent to clients with A/B test variant assignments.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| template_id | UUID | Foreign key to templates |
| invoice_id | UUID | Foreign key to invoices |
| ab_test_variant | VARCHAR(50) | Variant identifier |
| scheduled_send_at | TIMESTAMPTZ | Planned send time |
| sent_at | TIMESTAMPTZ | Actual send time |
| opened_at | TIMESTAMPTZ | First open timestamp |
| paid_after_send | BOOLEAN | Payment received post-send |
| paid_amount | DECIMAL(12,2) | Amount paid after campaign |

**Indexes:** user_id, template_id, invoice_id, sent_at

---

### 6. `ab_tests`
Defines A/B test experiments with variants and tracks results.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| name | VARCHAR(255) | Test name |
| test_type | VARCHAR(50) | template, timing, subject_line |
| variants | JSONB | Array of variant configurations |
| is_active | BOOLEAN | Whether test is running |
| started_at | TIMESTAMPTZ | Test start date |

**Indexes:** user_id, test_type, is_active

---

### 7. `email_events`
Logs email delivery and engagement events for tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| campaign_id | UUID | Foreign key to campaigns |
| event_type | VARCHAR(50) | sent, delivered, opened, clicked, bounced, complained |
| event_data | JSONB | Additional event metadata |
| ip_address | INET | Recipient IP address (for analysis) |

**Indexes:** campaign_id, event_type, occurred_at

---

### 8. `webhook_events`
Persistent storage of received webhooks for audit and idempotency.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| provider | VARCHAR(50) | stripe, paypal, plaid |
| event_id | VARCHAR(500) | Provider event ID |
| signature_verified | BOOLEAN | Verification status |
| processing_status | VARCHAR(50) | pending, processed, failed |

**Unique Constraint:** (provider, event_id) prevents duplicate processing

---

### 9. `audit_logs`
Tracks all data changes for compliance and debugging.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | User who performed action |
| action | VARCHAR(100) | Action performed (create, update, delete) |
| entity_type | VARCHAR(50) | Table name |
| entity_id | UUID | Record ID |
| old_values | JSONB | Previous values |
| new_values | JSONB | New values |

**Indexes:** user_id, (entity_type, entity_id), created_at

---

### 10. `refresh_tokens`
Stores JWT refresh tokens with rotation support.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| token_hash | VARCHAR(255) | Hashed refresh token |
| expires_at | TIMESTAMPTZ | Expiration time |
| is_revoked | BOOLEAN | Revocation status |

**Indexes:** user_id, token_hash, expires_at

---

### 11. `system_metrics`
Time-series metrics for monitoring application health.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| metric_name | VARCHAR(100) | Metric identifier |
| metric_value | DECIMAL(15,4) | Numeric value |
| labels | JSONB | Key-value pairs for dimension |
| recorded_at | TIMESTAMPTZ | Measurement timestamp |

**Indexes:** metric_name, recorded_at

---

## Relationships

### One-to-Many Relationships

1. **users → payment_connections**: One user can connect multiple payment providers
2. **users → invoices**: One user has many invoices
3. **users → campaigns**: One user runs many campaigns
4. **users → templates**: One user can create many templates (system templates have user_id NULL)
5. **users → ab_tests**: One user can run multiple A/B tests
6. **users → audit_logs**: One user generates many audit entries
7. **users → refresh_tokens**: One user can have multiple active refresh tokens

### Many-to-One Relationships

1. **payment_connections → users**: Each connection belongs to one user
2. **invoices → users**: Each invoice belongs to one user
3. **campaigns → users**: Each campaign belongs to one user
4. **campaigns → templates**: Each campaign uses one template
5. **campaigns → invoices**: Each campaign targets one invoice
6. **templates → users**: Each custom template belongs to one user (or NULL for system)
7. **ab_tests → users**: Each test belongs to one user
8. **email_events → campaigns**: Each event belongs to one campaign
9. **webhook_events → (provider specific)**: Each webhook event is logged
10. **audit_logs → users**: Each audit entry is tied to a user (or NULL for system actions)
11. **refresh_tokens → users**: Each token belongs to one user

### Many-to-Many (via bridge tables)

None explicitly modeled; all relationships are direct FK references.

---

## Views

### `user_invoice_summary`
Provides aggregated invoice statistics per user:
- Total invoice count
- Paid/overdue/disputed counts
- Outstanding amount
- Recovery rate percentage

**Uses Function:** `calculate_recovery_rate(user_id)`

### `campaign_effectiveness`
Provides campaign performance metrics:
- Email engagement (opens, clicks)
- Revenue generated
- A/B test variant comparison

---

## Functions

### `check_invoice_limit(user_id)`
Returns TRUE if user can create more invoices within their limit.

**Use Case:** Middleware enforcement for freemium users.

### `calculate_recovery_rate(user_id)`
Returns percentage of paid invoices vs total (excluding draft/canceled).

**Use Case:** KPI dashboard, user statistics.

### `get_overdue_count(user_id)`
Returns count of invoices that are overdue or disputed and past due date.

**Use Case:** Dashboard alerts, email triggers.

---

## Triggers

All tables with `updated_at` column have a BEFORE UPDATE trigger that automatically sets `updated_at = NOW()`.

Tables affected:
- users
- payment_connections
- invoices
- templates
- ab_tests

---

## Security

### Row Level Security (RLS)
Enabled on:
- payment_connections
- invoices
- templates
- campaigns

**Policy:** Users can only access rows where `user_id = current_setting('app.current_user_id')::UUID`.

**Implementation Note:** Application must set the session variable `app.current_user_id` after authentication:
```sql
SET app.current_user_id = 'user-uuid-here';
```

---

## Extensions Used

- `uuid-ossp`: For UUID generation (`uuid_generate_v4()`)
- `pgcrypto`: For password hashing (`crypt()`)
- `btree_gin`: (Optional) For advanced GIN indexing

---

## Performance Considerations

### Indexes

- **Single-column indexes** on foreign keys and common filter columns (status, due_date)
- **Composite indexes** on (user_id, status) for filtered user queries
- **Partial indexes** on external provider IDs (only where they exist)
- **GIN indexes** on JSONB columns for metadata queries

### Partitioning (Future)

For invoices > 1M rows, consider partitioning by `created_at` (monthly partitions).

### Vacuum & Analyze

Schedule daily `VACUUM ANALYZE` on large tables to maintain query performance.

---

## Migration Notes

This schema is designed for PostgreSQL 13+.

### Version: 001_initial_schema
### Created: 2026-03-20

See migration notes at the bottom of `schema.sql` for rollback instructions.

---

## Future Enhancements

1. **Multi-tenancy**: Add organization/team support
2. **Audit retention**: Archive audit_logs older than 2 years to cold storage
3. **Metrics aggregation**: Create materialized views for performance
4. **Full-text search**: Add tsvector column on invoices.client_name and templates.body
5. **Foreign data wrappers**: Link to external billing systems
