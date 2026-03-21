# Invoice Resolver AI - API Documentation

## Overview

RESTful API built with FastAPI for the Invoice Resolver AI platform. All endpoints return JSON and follow consistent patterns for authentication, errors, and pagination.

**Base URL**: `https://api.invoice-resolver-ai.com` (production) or `http://localhost:8000` (development)

**Authentication**: JWT Bearer tokens via `Authorization: Bearer <token>` header

**Content-Type**: All requests should include `Content-Type: application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Invoices](#invoices)
4. [Templates](#templates)
5. [Campaigns](#campaigns)
6. [Webhooks](#webhooks)
7. [Admin](#admin)
8. [Analytics](#analytics)
9. [Billing](#billing)
10. [Data Models](#data-models)
11. [Error Codes](#error-codes)
12. [Rate Limiting](#rate-limiting)

---

## Authentication

All protected endpoints require a valid JWT access token. The token should be included in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Register a New User

**Endpoint**: `POST /auth/register`

**Description**: Creates a new user account with default free tier settings.

**Request Body**:

```json
{
  "email": "john@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "timezone": "America/New_York"
}
```

**Response** (201 Created):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "subscription_tier": "free",
  "invoice_limit": 5,
  "timezone": "America/New_York",
  "is_active": true,
  "created_at": "2025-03-20T12:00:00Z"
}
```

**Errors**:
- `400`: Validation error (email exists, weak password, invalid timezone)
- `422`: Missing required fields

---

### Login

**Endpoint**: `POST /auth/login`

**Description**: Authenticates user and returns JWT access and refresh tokens.

**Request Body**:

```json
{
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "full_name": "John Doe",
    "subscription_tier": "free",
    "invoice_limit": 5
  }
}
```

**Errors**:
- `401`: Invalid credentials
- `423`: Account locked (too many failed attempts)
- `428`: Account inactive

---

### Refresh Access Token

**Endpoint**: `POST /auth/refresh`

**Description**: Rotates access token using refresh token.

**Request Body**:

```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4"
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "a_new_refresh_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors**:
- `401`: Invalid or expired refresh token
- `410`: Refresh token revoked

---

### Logout

**Endpoint**: `POST /auth/logout`

**Description**: Revokes the current access token by adding it to the blocklist.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

**Errors**:
- `401`: Invalid token

---

### Request Password Reset

**Endpoint**: `POST /auth/password-reset/request`

**Description**: Sends password reset email with temporary link.

**Request Body**:

```json
{
  "email": "john@example.com"
}
```

**Response** (200 OK):

```json
{
  "message": "Password reset email sent if account exists"
}
```

---

### Reset Password

**Endpoint**: `POST /auth/password-reset/confirm`

**Description**: Completes password reset using token from email.

**Request Body**:

```json
{
  "token": "reset_token_from_email",
  "new_password": "new_secure_password_123"
}
```

**Response** (200 OK):

```json
{
  "message": "Password reset successful"
}
```

---

## Users

### Get Current User Profile

**Endpoint**: `GET /users/me`

**Description**: Retrieves the authenticated user's profile information.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "subscription_tier": "free",
  "invoice_limit": 5,
  "timezone": "America/New_York",
  "email_notifications_enabled": true,
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-03-20T12:00:00Z",
  "last_login_at": "2025-03-20T14:30:00Z"
}
```

---

### Update Current User Profile

**Endpoint**: `PATCH /users/me`

**Description**: Updates user profile information (partial update).

**Headers**: `Authorization: Bearer <access_token>`

**Request Body** (all fields optional):

```json
{
  "full_name": "Johnathan Doe",
  "company_name": "Acme Inc",
  "timezone": "America/Chicago",
  "email_notifications_enabled": false
}
```

**Response** (200 OK): Updated user object

---

### Get User Invoice Usage

**Endpoint**: `GET /users/me/usage`

**Description**: Returns current invoice count and limit for the authenticated user.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "subscription_tier": "free",
  "invoice_limit": 5,
  "current_invoice_count": 3,
  "remaining_invoices": 2,
  "reset_date": "2025-04-01T00:00:00Z"
}
```

---

## Invoices

### List Invoices

**Endpoint**: `GET /invoices`

**Description**: Retrieves a paginated list of invoices for the authenticated user with optional filters.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `draft`, `sent`, `paid`, `overdue`, `disputed`, `canceled` |
| `due_date_before` | date | Filter invoices due before this date (ISO 8601) |
| `due_date_after` | date | Filter invoices due after this date (ISO 8601) |
| `client_name` | string | Partial match on client name |
| `min_amount` | decimal | Minimum invoice amount |
| `max_amount` | decimal | Maximum invoice amount |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page, max 100 (default: 20) |
| `sort_by` | string | Sort field: `due_date`, `amount`, `created_at` (default: `due_date`) |
| `sort_order` | string | `asc` or `desc` (default: `desc`) |

**Response** (200 OK):

```json
{
  "total": 45,
  "page": 1,
  "limit": 20,
  "invoices": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "invoice_number": "INV-2025-001",
      "client_name": "Acme Corp",
      "client_email": "billing@acme.com",
      "amount": "1500.00",
      "currency": "USD",
      "status": "overdue",
      "due_date": "2025-03-15",
      "issue_date": "2025-02-15",
      "paid_date": null,
      "description": "Website development services",
      "notes": "30-day payment terms",
      "stripe_payment_intent_id": "pi_123456789",
      "stripe_invoice_id": null,
      "paypal_txn_id": null,
      "created_at": "2025-02-15T10:30:00Z",
      "updated_at": "2025-03-16T09:15:00Z"
    }
  ]
}
```

---

### Get Single Invoice

**Endpoint**: `GET /invoices/{invoice_id}`

**Description**: Retrieves detailed information about a specific invoice.

**Headers**: `Authorization: Bearer <access_token>`

**Path Parameters**:
- `invoice_id` (uuid): The invoice's unique ID

**Response** (200 OK): Full invoice object with all fields

**Errors**:
- `404`: Invoice not found or access denied

---

### Create Invoice

**Endpoint**: `POST /invoices`

**Description**: Creates a new invoice (manual entry or imported from payment provider).

**Headers**: `Authorization: Bearer <access_token>`

**Important**: Before creating, verify invoice limit hasn't been exceeded using `GET /users/me/usage`.

**Request Body**:

```json
{
  "invoice_number": "INV-2025-042",
  "client_name": "Beta Startup LLC",
  "client_email": "accounts@beta.com",
  "amount": 2500.00,
  "currency": "USD",
  "status": "sent",
  "due_date": "2025-04-20",
  "issue_date": "2025-03-20",
  "description": "Q1 2025 consulting retainer",
  "notes": "Net 30 terms, 2% late fee after due date",
  "metadata": {
    "project_code": "BETA-001",
    "contract_id": "contract_abc123"
  },
  "stripe_payment_intent_id": "pi_987654321",
  "paypal_txn_id": null
}
```

**Required Fields**:
- `client_name`
- `amount`
- `due_date`
- `issue_date`

**Response** (201 Created):

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "invoice_number": "INV-2025-042",
  "client_name": "Beta Startup LLC",
  "client_email": "accounts@beta.com",
  "amount": "2500.00",
  "currency": "USD",
  "status": "sent",
  "due_date": "2025-04-20",
  "issue_date": "2025-03-20",
  "paid_date": null,
  "description": "Q1 2025 consulting retainer",
  "notes": "Net 30 terms, 2% late fee after due date",
  "metadata": {
    "project_code": "BETA-001",
    "contract_id": "contract_abc123"
  },
  "stripe_payment_intent_id": "pi_987654321",
  "created_at": "2025-03-20T11:45:00Z",
  "updated_at": "2025-03-20T11:45:00Z"
}
```

**Errors**:
- `400`: Invalid data (amount <= 0, invalid currency, past due_date, etc.)
- `409`: Duplicate invoice number (if provided)
- `429`: Invoice limit exceeded (free tier: 5 invoices/month)
- `451`: Invalid payment provider ID (Stripe/PayPal credentials don't match)

---

### Update Invoice

**Endpoint**: `PATCH /invoices/{invoice_id}`

**Description**: Updates invoice details (partial update). Certain fields can only be updated by admin or via webhook.

**Headers**: `Authorization: Bearer <access_token>`

**Path Parameters**:
- `invoice_id` (uuid): The invoice's unique ID

**Request Body** (all fields optional):

```json
{
  "status": "paid",
  "paid_date": "2025-03-18T14:20:00Z",
  "client_email": "updated@email.com",
  "notes": "Payment received via wire transfer"
}
```

**Immutable Fields** (cannot be updated via API):
- `user_id`
- `amount`
- `currency`
- `invoice_number` (after creation)

**Response** (200 OK): Updated invoice object

**Errors**:
- `404`: Invoice not found or access denied
- `422`: Invalid status transition (e.g., `draft` -> `paid` directly)

---

### Delete Invoice (Soft Delete)

**Endpoint**: `DELETE /invoices/{invoice_id}`

**Description**: Marks invoice as canceled. If already paid/overdue, requires admin privileges.

**Headers**: `Authorization: Bearer <access_token>`

**Path Parameters**:
- `invoice_id` (uuid): The invoice's unique ID

**Response** (204 No Content)

**Errors**:
- `403`: Cannot delete paid/overdue invoice without admin rights
- `404`: Invoice not found or access denied

---

### Bulk Create Invoices

**Endpoint**: `POST /invoices/bulk`

**Description**: Creates multiple invoices in a single transaction (for CSV import).

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
  "invoices": [
    {
      "client_name": "Client A",
      "amount": 1000.00,
      "due_date": "2025-04-15"
    },
    {
      "client_name": "Client B",
      "amount": 2500.00,
      "due_date": "2025-04-20"
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "created_count": 2,
  "failed_count": 0,
  "invoice_ids": ["id1", "id2"],
  "errors": []
}
```

**Errors**:
- `429`: Bulk operation would exceed invoice limit

---

### Get Invoice Campaigns

**Endpoint**: `GET /invoices/{invoice_id}/campaigns`

**Description**: Lists all follow-up campaigns associated with this invoice.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "campaigns": [
    {
      "id": "campaign_uuid",
      "template_type": "follow_up_3_day",
      "scheduled_send_at": "2025-03-18T10:00:00Z",
      "sent_at": "2025-03-18T10:00:02Z",
      "opened_at": "2025-03-18T10:05:15Z",
      "paid_after_send": true
    }
  ]
}
```

---

## Templates

### List Templates

**Endpoint**: `GET /templates`

**Description**: Retrieves templates available to the user, including system templates.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by template type |
| `is_system` | boolean | Filter to system templates only (default: false) |
| `is_active` | boolean | Filter by active status |

**Response** (200 OK):

```json
{
  "templates": [
    {
      "id": "template_uuid_1",
      "name": "3-Day Follow-up",
      "type": "follow_up_3_day",
      "subject": "Friendly reminder about your invoice",
      "body_html": "<p>Hello {{client_name}},</p><p>This is a friendly reminder...</p>",
      "variables": ["client_name", "invoice_number", "amount", "due_date"],
      "is_system": true,
      "is_active": true,
      "created_at": "2025-01-15T08:00:00Z"
    }
  ]
}
```

---

### Get Single Template

**Endpoint**: `GET /templates/{template_id}`

**Description**: Retrieves a specific template.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK): Full template object

---

### Create Template

**Endpoint**: `POST /templates`

**Description**: Creates a custom template for the user.

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
  "name": "Custom Late Notice",
  "type": "custom",
  "subject": "URGENT: Invoice {{invoice_number}} is severely overdue",
  "body_html": "<html><body><h1>Overdue Notice</h1><p>Dear {{client_name}},</p>...</body></html>",
  "body_text": "Plain text version...",
  "variables": ["client_name", "invoice_number", "amount", "days_overdue"],
  "is_active": true
}
```

**Required Fields**:
- `name`
- `type` (must be one of the valid types or `custom`)
- `subject`
- `body_html`

**Response** (201 Created): Created template object

---

### Update Template

**Endpoint**: `PATCH /templates/{template_id}`

**Description**: Updates a custom template. System templates (`is_system=true`) are read-only.

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**: Partial template fields

**Response** (200 OK): Updated template object

---

### Delete Template

**Endpoint**: `DELETE /templates/{template_id}`

**Description**: Deletes a custom template. System templates cannot be deleted.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

---

### Clone System Template

**Endpoint**: `POST /templates/{template_id}/clone`

**Description**: Creates a user-owned copy of a system template for customization.

**Headers**: `Authorization: Bearer <access_token>`

**Path Parameters**:
- `template_id`: System template UUID to clone

**Request Body**:

```json
{
  "name": "My Custom 7-Day Follow-up"
}
```

**Response** (201 Created): New user-owned template

---

## Campaigns

### List Campaigns

**Endpoint**: `GET /campaigns`

**Description**: Retrieves campaigns with optional filters.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `invoice_id` | uuid | Filter by specific invoice |
| `status` | string | Filter by `sent`, `delivered`, `opened`, etc. |
| `template_type` | string | Filter by template type |
| `start_date` | date | Campaigns sent on or after this date |
| `end_date` | date | Campaigns sent on or before this date |
| `ab_test_variant` | string | Filter by A/B test variant |
| `page` | integer | Pagination |
| `limit` | integer | Items per page |

**Response** (200 OK):

```json
{
  "total": 23,
  "campaigns": [
    {
      "id": "campaign_uuid",
      "invoice_id": "invoice_uuid",
      "template_id": "template_uuid",
      "template_type": "follow_up_7_day",
      "ab_test_variant": "A",
      "scheduled_send_at": "2025-03-10T14:00:00Z",
      "sent_at": "2025-03-10T14:00:01Z",
      "delivered_at": "2025-03-10T14:00:05Z",
      "opened_at": "2025-03-10T14:02:30Z",
      "opened_count": 2,
      "clicked_at": null,
      "paid_after_send": true,
      "paid_amount": "1500.00",
      "created_at": "2025-03-10T13:45:00Z"
    }
  ]
}
```

---

### Get Campaign Details

**Endpoint**: `GET /campaigns/{campaign_id}`

**Description**: Retrieves full campaign details including email events.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK): Campaign object + nested `email_events` array

---

### Trigger Campaign Manually

**Endpoint**: `POST /campaigns/trigger`

**Description**: Manually triggers a follow-up campaign for an invoice using specified template.

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
  "invoice_id": "invoice_uuid",
  "template_id": "template_uuid",
  "scheduled_send_at": "2025-03-25T10:00:00Z",
  "ab_test_variant": "A"
}
```

**Response** (202 Accepted):

```json
{
  "campaign_id": "new_campaign_uuid",
  "status": "scheduled",
  "scheduled_send_at": "2025-03-25T10:00:00Z"
}
```

**Errors**:
- `404`: Invoice or template not found
- `409`: Campaign already exists for this invoice + template combination
- `422`: Invalid scheduled time (in past or >7 days ahead)

---

### Cancel Campaign

**Endpoint**: `DELETE /campaigns/{campaign_id}`

**Description**: Cancels a scheduled campaign (only allowed if not yet sent).

**Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

---

### Track Email Open

**Endpoint**: `GET /track/open/{campaign_id}`

**Description**: Pixel tracking endpoint for email opens. Returns a 1x1 transparent GIF.

**Path Parameters**:
- `campaign_id` (uuid): Campaign to track

**Query Parameters**:
- `user_id` (optional): For linking to user session

**Response**: Binary GIF image ( Content-Type: `image/gif` )

---

### Track Email Click

**Endpoint**: `GET /track/click/{campaign_id}`

**Description**: Redirects through tracking URL for link clicks.

**Path Parameters**:
- `campaign_id` (uuid): Campaign to track

**Query Parameters**:
- `url` (string, required): Original destination URL (URL-encoded)

**Response**: 302 Redirect to `url` with click tracked

---

## Webhooks

### Stripe Webhook

**Endpoint**: `POST /webhooks/stripe`

**Description**: Receives and processes Stripe webhook events.

**Headers**:
- `Stripe-Signature`: Webhook signature for verification

**Content-Type**: `application/json`

**Processed Events**:
- `invoice.payment_failed` → marks invoice as `overdue`
- `charge.dispute.created` → marks invoice as `disputed`
- `invoice.paid` → marks invoice as `paid`
- `customer.subscription.updated` → updates user subscription tier
- `charge.refunded` → adds refund note to invoice

**Request Payload** (from Stripe):

```json
{
  "id": "evt_123456789",
  "object": "event",
  "type": "invoice.payment_failed",
  "data": {
    "object": {
      "id": "inv_123456",
      "customer": "cus_789",
      "amount_paid": 0,
      "invoice_pdf": "https://pay.stripe.com/invoice.pdf",
      "metadata": {
        "invoice_id": "our_internal_uuid"
      }
    }
  }
}
```

**Response**:
- `202 Accepted`: Webhook received and queued for processing
- `400`: Invalid signature or malformed payload
- `429`: Rate limit exceeded (too many webhooks)

**Idempotency**: Each Stripe event ID is stored and processed only once.

---

### PayPal Webhook

**Endpoint**: `POST /webhooks/paypal`

**Description**: Receives and processes PayPal IPN (Instant Payment Notification) events.

**Headers**:
- `Paypal-Transmission-Id`
- `Paypal-Transmission-Time`
- `Paypal-Transmission-Sig`
- `Paypal-Cert-Url`
- `Paypal-Auth-Algo`

**Content-Type**: `application/x-www-form-urlencoded`

**Processed Events**:
- `PAYMENT.DENIED` → marks invoice as `overdue`
- `DISPUTE.CREATED` → marks invoice as `disputed`
- `PAYMENT.CAPTURE.COMPLETED` → marks invoice as `paid`
- `BILLING.SUBSCRIPTION.UPDATED` → updates subscription tier

**Request Payload** (form-encoded key-value pairs):

```
transaction_subject=invoice_resolver_ai
txn_type=dispute_created
payer_email=disputant@example.com
payer_id=paypal_user_123
invoice_id=our_internal_uuid
mc_gross=1500.00
mc_currency=USD
parent_txn_id=parent_txn_123
reason_code=unauthorized
case_id=PP-12345
```

**Response**:
- `200 OK`: Webhook received (PayPal expects HTTP 200)
- `400`: Invalid signature or missing required fields

---

### Plaid Webhook

**Endpoint**: `POST /webhooks/plaid`

**Description**: Receives Plaid transaction sync notifications.

**Headers**:
- `Plaid-Signature`: Ed25519 signature for verification

**Processed Events**:
- `TRANSACTIONS_REMOVED` → removes orphaned transactions
- `HISTORICAL_UPDATE` → triggers backfill
- `WEBHOOK_TEST` → acknowledgment only

**Request Payload**:

```json
{
  "webhook_code": "TRANSACTIONS_REMOVED",
  "webhook_type": "TRANSACTIONS",
  "item_id": "item_123456",
  "removed_transactions": ["txn_1", "txn_2"]
}
```

**Response**:
- `200 OK`: Webhook received
- `400`: Invalid signature

---

## Admin

**Note**: Admin endpoints require `is_admin=true` on user account.

### Admin Get All Users

**Endpoint**: `GET /admin/users`

**Description**: Retrieves all users with pagination and filters.

**Headers**: `Authorization: Bearer <admin_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `subscription_tier` | string | Filter by tier |
| `is_active` | boolean | Filter by active status |
| `search` | string | Search email, full_name, company_name |
| `page` | integer | Pagination |
| `limit` | integer | Items per page |

**Response** (200 OK):

```json
{
  "total": 150,
  "users": [
    {
      "id": "user_uuid",
      "email": "user@example.com",
      "full_name": "User Name",
      "company_name": "Company LLC",
      "subscription_tier": "pro",
      "invoice_limit": 999,
      "is_active": true,
      "created_at": "2025-01-10T08:00:00Z",
      "last_login_at": "2025-03-20T14:30:00Z"
    }
  ]
}
```

---

### Admin Get User Details

**Endpoint**: `GET /admin/users/{user_id}`

**Description**: Retrieves comprehensive user information including usage stats.

**Response** (200 OK):

```json
{
  "user": { /* user object */ },
  "stats": {
    "total_invoices": 42,
    "paid_invoices": 38,
    "overdue_invoices": 2,
    "disputed_invoices": 0,
    "recovery_rate": 90.48,
    "total_campaigns_sent": 67,
    "total_revenue_generated": 42500.00
  },
  "connections": [
    {
      "provider": "stripe",
      "external_account_id": "acct_123",
      "is_active": true,
      "last_sync_at": "2025-03-20T12:00:00Z"
    }
  ]
}
```

---

### Admin Update User Subscription

**Endpoint**: `PATCH /admin/users/{user_id}/subscription`

**Description**: Changes user's subscription tier and adjusts invoice limit accordingly.

**Headers**: `Authorization: Bearer <admin_token>`

**Request Body**:

```json
{
  "subscription_tier": "pro",
  "invoice_limit": 999,
  "billing_cycle_anchor": "2025-04-01T00:00:00Z"
}
```

**Response** (200 OK): Updated user object

---

### Admin Get System Health

**Endpoint**: `GET /admin/health`

**Description**: Returns system health metrics including Celery workers, database connectivity, queue sizes.

**Headers**: `Authorization: Bearer <admin_token>`

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-03-20T15:45:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "connections": 12,
      "pool_size": 20,
      "response_time_ms": 2.5
    },
    "redis": {
      "status": "healthy",
      "connected_clients": 8,
      "memory_usage_mb": 45.2,
      "response_time_ms": 0.8
    },
    "celery": {
      "status": "healthy",
      "workers": [
        {
          "name": "celery@worker-1",
          "status": "online",
          "active_tasks": 3,
          "processed_tasks": 15432
        }
      ],
      "queue_sizes": {
        "default": 0,
        "email": 2,
        "webhooks": 0
      }
    }
  }
}
```

---

### Admin Get Webhook Events

**Endpoint**: `GET /admin/webhooks`

**Description**: Lists recent webhook events with filtering.

**Headers**: `Authorization: Bearer <admin_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | string | `stripe`, `paypal`, or `plaid` |
| `processing_status` | string | `pending`, `processed`, `failed` |
| `start_date` | date | Events from this date |
| `end_date` | date | Events to this date |
| `limit` | integer | Max 100 (default: 50) |

**Response** (200 OK):

```json
{
  "total": 234,
  "events": [
    {
      "id": "webhook_uuid",
      "provider": "stripe",
      "event_id": "evt_123456",
      "event_type": "invoice.payment_failed",
      "signature_verified": true,
      "processing_status": "processed",
      "processing_error": null,
      "created_at": "2025-03-20T14:30:00Z",
      "processed_at": "2025-03-20T14:30:02Z"
    }
  ]
}
```

---

### Admin Replay Failed Webhook

**Endpoint**: `POST /admin/webhooks/{webhook_id}/replay`

**Description**: Manually retries processing of a failed webhook event.

**Headers**: `Authorization: Bearer <admin_token>`

**Response** (202 Accepted):

```json
{
  "webhook_id": "webhook_uuid",
  "status": "queued",
  "message": "Webhook reprocessing queued"
}
```

---

## Analytics

### Get Dashboard KPIs

**Endpoint**: `GET /analytics/dashboard`

**Description**: Returns key performance indicators for the authenticated user's dashboard.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | date | Start of analysis period (default: 30 days ago) |
| `end_date` | date | End of analysis period (default: today) |

**Response** (200 OK):

```json
{
  "period": {
    "start_date": "2025-02-20",
    "end_date": "2025-03-20"
  },
  "kpis": {
    "total_invoices": 45,
    "total_amount": 67500.00,
    "overdue_count": 5,
    "overdue_amount": 12500.00,
    "paid_count": 38,
    "recovery_rate": 84.44,
    "avg_days_to_pay": 12.3,
    "campaigns_sent": 23,
    "campaign_open_rate": 68.5,
    "campaign_conversion_rate": 22.1,
    "revenue_from_campaigns": 18750.00
  },
  "trends": {
    "recovery_rate_change": "+5.2%",
    "overdue_invoices_change": "-2",
    "campaigns_sent_change": "+8"
  }
}
```

---

### Get Invoice Aging Report

**Endpoint**: `GET /analytics/aging`

**Description**: Buckets outstanding invoices by age for aging report.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "as_of_date": "2025-03-20",
  "total_outstanding": 12500.00,
  "aging_buckets": [
    {
      "bucket": "current",
      "min_days_overdue": 0,
      "max_days_overdue": 0,
      "invoice_count": 2,
      "amount": 3000.00
    },
    {
      "bucket": "1-30",
      "min_days_overdue": 1,
      "max_days_overdue": 30,
      "invoice_count": 3,
      "amount": 5500.00
    },
    {
      "bucket": "31-60",
      "min_days_overdue": 31,
      "max_days_overdue": 60,
      "invoice_count": 1,
      "amount": 2500.00
    },
    {
      "bucket": "60+",
      "min_days_overdue": 61,
      "max_days_overdue": null,
      "invoice_count": 1,
      "amount": 1500.00
    }
  ]
}
```

---

### Get Campaign Effectiveness

**Endpoint**: `GET /analytics/campaign-effectiveness`

**Description**: Analyzes performance of follow-up campaigns by template type and A/B variant.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | date | Analysis start date |
| `end_date` | date | Analysis end date |
| `group_by` | string | `template` or `variant` (default: `template`) |

**Response** (200 OK):

```json
{
  "period": {
    "start_date": "2025-02-20",
    "end_date": "2025-03-20"
  },
  "campaigns": [
    {
      "template_type": "follow_up_3_day",
      "variant": "A",
      "campaigns_sent": 12,
      "emails_delivered": 12,
      "opens": 9,
      "open_rate": 75.0,
      "clicks": 3,
      "click_rate": 25.0,
      "payments_after_send": 3,
      "conversion_rate": 25.0,
      "revenue_generated": 4500.00,
      "avg_days_to_pay_after_send": 4.2
    },
    {
      "template_type": "follow_up_7_day",
      "variant": "B",
      "campaigns_sent": 8,
      "emails_delivered": 8,
      "opens": 6,
      "open_rate": 75.0,
      "clicks": 1,
      "click_rate": 12.5,
      "payments_after_send": 1,
      "conversion_rate": 12.5,
      "revenue_generated": 1500.00,
      "avg_days_to_pay_after_send": 6.0
    }
  ]
}
```

---

### Export Analytics CSV

**Endpoint**: `GET /analytics/export`

**Description**: Generates a CSV file with invoice and campaign data for external reporting.

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | date | Required |
| `end_date` | date | Required |
| `report_type` | string | `invoices`, `campaigns`, or `combined` (default: `combined`) |
| `include_headers` | boolean | Include CSV column headers (default: `true`) |

**Response**: `text/csv` file download

**Example CSV** (invoices):

```csv
invoice_id,client_name,amount,status,due_date,paid_date,days_overdue,campaigns_sent,paid_after_campaign
inv_123,Acme Corp,1500.00,overdue,2025-03-15,,5,2,true
inv_124,Beta LLC,2500.00,paid,2025-02-20,2025-02-25,,1,true
```

---

## Billing

### Get Available Plans

**Endpoint**: `GET /billing/plans`

**Description**: Lists available subscription plans with pricing and features.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price_monthly": 0,
      "price_yearly": 0,
      "invoice_limit": 5,
      "features": [
        "5 invoices/month",
        "Basic email follow-ups",
        "Standard support"
      ],
      "stripe_price_id_monthly": "price_free_monthly",
      "stripe_price_id_yearly": null
    },
    {
      "id": "pro",
      "name": "Pro",
      "price_monthly": 19,
      "price_yearly": 190,
      "invoice_limit": 999,
      "features": [
        "Unlimited invoices",
        "AI-powered dispute letters",
        "A/B testing",
        "Priority support"
      ],
      "stripe_price_id_monthly": "price_pro_monthly",
      "stripe_price_id_yearly": "price_pro_yearly"
    }
  ]
}
```

---

### Create Checkout Session

**Endpoint**: `POST /billing/checkout-session`

**Description**: Creates a Stripe Checkout session for upgrading subscription.

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
  "plan_id": "pro",
  "billing_cycle": "monthly",
  "success_url": "https://app.invoice-resolver-ai.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://app.invoice-resolver-ai.com/billing/cancel"
}
```

**Required Fields**:
- `plan_id`: Must match one of the available plans
- `billing_cycle`: `monthly` or `yearly`

**Response** (200 OK):

```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_123456",
  "session_id": "cs_test_123456",
  "plan_id": "pro",
  "billing_cycle": "monthly"
}
```

---

### Get Current Subscription

**Endpoint**: `GET /billing/subscription`

**Description**: Retrieves the user's current subscription status and billing info.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "subscription_tier": "free",
  "stripe_customer_id": "cus_123456",
  "stripe_subscription_id": null,
  "status": null,
  "current_period_start": null,
  "current_period_end": null,
  "cancel_at_period_end": false,
  "invoice_limit": 5,
  "overage_charges": 0.00
}
```

---

### Cancel Subscription

**Endpoint**: `POST /billing/subscription/cancel`

**Description**: Schedules subscription cancellation at period end.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
  "subscription_id": "sub_123456",
  "status": "canceled_at_period_end",
  "current_period_end": "2025-04-01T00:00:00Z"
}
```

---

## Data Models

### Common Response Envelopes

**Paginated Response**:

```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "items": [ /* array of objects */ ]
}
```

**Error Response**:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## Error Codes

| HTTP Status | Error Code | Description | Retryable |
|-------------|------------|-------------|-----------|
| 400 | `VALIDATION_ERROR` | Request data invalid | No |
| 401 | `UNAUTHENTICATED` | Missing or invalid token | No |
| 403 | `INSUFFICIENT_PERMISSIONS` | User lacks required role | No |
| 404 | `NOT_FOUND` | Resource not found | No |
| 409 | `CONFLICT` | Duplicate or conflicting resource | No |
| 422 | `INVALID_STATE` | Invalid state transition | No |
| 429 | `RATE_LIMITED` | Too many requests | Yes |
| 451 | `PAYMENT_REQUIRED` | Invoice limit exceeded | No |
| 500 | `INTERNAL_ERROR` | Server error | Yes |
| 503 | `SERVICE_UNAVAILABLE` | Maintenance mode | Yes |

---

## Rate Limiting

All endpoints are rate-limited using token bucket algorithm:

**Limits per user**:
- **Authenticated**: 100 requests/minute
- **Unauthenticated**: 10 requests/minute

**Headers in responses**:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1742475300
Retry-After: 12 (only on 429 response)
```

Webhook endpoints have separate limits:
- **Stripe/PayPal**: 1000 requests/minute per IP
- **Plaid**: 500 requests/minute per IP

Rate limits reset every 60 seconds.

---

## Pagination

All list endpoints support pagination via query parameters:

- `page` (integer): Page number, default 1
- `limit` (integer): Items per page, default 20, max 100

Response includes:
- `total`: Total count of items matching query (across all pages)
- `page`: Current page number
- `limit`: Items per page
- `items`: Array of resource objects

**Example**: `GET /invoices?page=2&limit=50` retrieves items 51-100.

---

## Sorting

List endpoints support sorting via:

- `sort_by`: Field name (e.g., `due_date`, `amount`, `created_at`, `updated_at`)
- `sort_order`: `asc` or `desc` (default: `desc`)

**Example**: `GET /invoices?sort_by=due_date&sort_order=asc&status=overdue`

---

## Filtering

Multiple filters can be applied simultaneously using query parameters:

- Exact match: `status=paid`
- Range: `amount_min=100&amount_max=1000`
- Date range: `due_date_after=2025-01-01&due_date_before=2025-03-31`
- Partial text: `client_name=acme` (case-insensitive LIKE)

---

## Webhook Payload Examples

### Stripe: `invoice.payment_failed`

```json
{
  "id": "evt_1abcdefghijklmnopqrstuvwxyz",
  "object": "event",
  "api_version": "2024-06-20",
  "created": 1742475000,
  "type": "invoice.payment_failed",
  "data": {
    "object": {
      "id": "invoicetemplate_1abcdefghijklmnopqrstuvwxy",
      "object": "invoice",
      "amount_paid": 0,
      "amount_remaining": 150000,
      "customer": "cus_abcdefghijklmnopqrstuvwxyz",
      "customer_email": "client@example.com",
      "metadata": {
        "invoice_id": "660e8400-e29b-41d4-a716-446655440001"
      },
      "number": "INV-2025-001",
      "status": "open",
      "billing_reason": "automatic",
      "created": 1742474900
    }
  }
}
```

---

### PayPal: `PAYMENT.DENIED`

**Form-encoded**:

```
transaction_subject=invoice_resolver_ai
txn_type=payment_denied
payer_email=client@example.com
payer_id=ABCDEFGHIJKLMNOP
invoice_id=660e8400-e29b-41d4-a716-446655440001
mc_gross=1500.00
mc_currency=USD
parent_txn_id=9AB12345CD6789012EFGH
reason_code=unauthorized
case_id=PP-12345-ABC-DEF-GHI-JKL
protection_eligibility=INELIGIBLE
```

---

### Stripe: `charge.dispute.created`

```json
{
  "id": "evt_1disputecreated",
  "object": "event",
  "type": "charge.dispute.created",
  "data": {
    "object": {
      "id": "dp_123456",
      "object": "dispute",
      "amount": 150000,
      "currency": "usd",
      "status": "needs_response",
      "reason": "fraudulent",
      "evidence": null,
      "metadata": {
        "invoice_id": "660e8400-e29b-41d4-a716-446655440001"
      },
      "charge": "ch_123456789"
    }
  }
}
```

---

### Stripe: `customer.subscription.updated`

```json
{
  "id": "evt_1subupdated",
  "object": "event",
  "type": "customer.subscription.updated",
  "data": {
    "object": {
      "id": "sub_123456",
      "object": "subscription",
      "status": "active",
      "customer": "cus_abcdefghijklmnopqrstuvwxyz",
      "items": {
        "data": [
          {
            "price": {
              "id": "price_pro_monthly",
              "unit_amount": 1900
            }
          }
        ]
      },
      "current_period_start": 1742475000,
      "current_period_end": 1745067000,
      "cancel_at_period_end": false,
      "metadata": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  }
}
```

---

## Testing

### Test Mode vs Live Mode

- **Test Mode**: Use Stripe/PayPal test credentials. No real charges.
- **Live Mode**: Uses production credentials. Real transactions.

**Toggle via** environment variables:
- `STRIPE_MODE=test|live`
- `PAYPAL_MODE=sandbox|live`

Test webhook signatures require different webhook secrets.

---

### Sandbox Data

For development, use these test webhook payloads:

**Stripe**: Use `stripe trigger` CLI or webhook testing tool in dashboard.

**PayPal**: Send POST to `/webhooks/paypal` with form-encoded data from PayPal sandbox.

**Plaid**: Use `plaid-cli` or sandbox test environment with `SANDBOX_INSTITUTION` credentials.

---

### Local Testing with ngrok

For local webhook development:

```bash
# Start ngrok
ngrok http 8000

# Set webhook URL in Stripe/PayPal dashboard to:
# https://<ngrok-id>.ngrok.io/webhooks/stripe
# https://<ngrok-id>.ngrok.io/webhooks/paypal
```

---

## OpenAPI Specification

The complete OpenAPI 3.1 specification is available at:

```
GET /openapi.json
```

FastAPI auto-generates this from the codebase. It includes:
- All endpoint schemas
- Request/response models
- Authentication schemes (JWT Bearer)
- Example payloads
- Parameter descriptions

---

## SDKs and Client Libraries

Official SDKs:

- **Python**: `pip install invoice-resolver-ai`
- **JavaScript/Node**: `npm install @invoice-resolver-ai/client`

Example Python usage:

```python
from invoice_resolver_ai import Client

client = Client(api_key="your_access_token")
invoices = client.invoices.list(status="overdue")
for invoice in invoices:
    print(f"{invoice.client_name}: ${invoice.amount}")
```

---

## Health Checks

### API Health

**Endpoint**: `GET /health`

**Description**: Simple health check for load balancers.

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-03-20T15:45:00Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### Readiness Check

**Endpoint**: `GET /ready`

**Description**: Checks if API is ready to serve traffic (database + Redis connections established).

**Response**: `200 OK` or `503 Service Unavailable`

### Liveness Check

**Endpoint**: `GET /live`

**Description**: Simple liveness probe for Kubernetes/etc.

**Response**: `200 OK`

---

## Versioning

The API is versioned via URL path:

```
/v1/invoices
/v1/auth/login
```

Current version: `v1`

Breaking changes will increment major version. Minor/backward-compatible changes will increment minor version and be documented in changelog.

---

## Contact & Support

- **API Issues**: https://github.com/your-org/invoice-resolver-ai/issues
- **Email**: api-support@invoice-resolver-ai.com
- **Status Page**: https://status.invoice-resolver-ai.com

---

## Changelog

### v1.0.0 (2025-03-20)
- Initial release
- Authentication endpoints
- Invoice CRUD operations
- Webhook receivers (Stripe, PayPal, Plaid)
- Email campaign management
- Admin API
- Analytics endpoints
- Billing/subscription management

---

**Last Updated**: 2025-03-20
