# Iteration 36 - invoice-resolver-ai

**Timestamp:** Fri Mar 20 11:46:47 PM EDT 2026
**Task:** **Task 4.4:** Implement billing integration with Stripe Billing or Paddle for subscription management. Create plans: Free (5 invoices/month), Pro ($19/mo unlimited), add-ons ($5 legal pack, $3 multi-currency). Webhook to handle subscription updates.

## Prompt Sent

```
# Project Agent Instructions (Step 3.5 Flash)

## ROLE DETECTION

**CRITICAL**: Before reading further, check your role:
```bash
cat .agent_role
```

**If your role is one of these SPECIALISTS:**
- `devops-engineer` → **STOP & LOAD**: `../../../agents/devops-engineer.md`
- `qa-specialist` → **STOP & LOAD**: `../../../agents/qa-specialist.md`
- `release-manager` → **STOP & LOAD**: `../../../agents/release-manager.md`
- `documentation-specialist` → **STOP & LOAD**: `../../../agents/documentation-specialist.md`
- `project-orchestrator` → **STOP & LOAD**: `../../../agents/project-orchestrator.md`

**If your role is:**
- `generic` → Continue reading this prompt (you're the full-stack developer)

---

**Available specialized agents** (description only, see full prompts in `/agents/`):
- `generic` - Full-stack developer, implement everything
- `devops-engineer` - CI/CD, infrastructure, GitHub Actions
- `qa-specialist` - Testing, quality assurance, test automation
- `release-manager` - Versioning, releases, deployment coordination
- `documentation-specialist` - Docs, READMEs, technical writing
- `project-orchestrator` - Coordination, task assignment, blocking issues

---

## GENERIC DEVELOPER MODE

## CORE MISSION
1. Read `TASKS.md`
2. Complete ONE task per iteration
3. Update `TASKS.md` with progress: Mark completed tasks with `[x]`
4. Commit & push to GitHub
5. Repeat until all tasks done

## CRITICAL: ALWAYS DO FIRST

**Task 0: GitHub Actions Workflow Setup** (Do before Task 1)

Detect tech stack from these files:
| File | Language |
|------|----------|
| `package.json` | Node.js |
| `pyproject.toml` or `requirements.txt` | Python |
| `go.mod` or `go.sum` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `pom.xml` or `build.gradle` | Java |
| `Dockerfile` (only) | Docker |
| None | Shell/Unknown |

Create `.github/workflows/test.yml` using the correct template:

<details>
<summary>Node.js Template</summary>

```yaml
name: Test & Validate (Node.js)
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['18.x', '20.x']
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    - run: npm ci
    - run: npm run lint || true
      continue-on-error: true
    - run: npm run build || true
      continue-on-error: true
    - run: npm test || true
      continue-on-error: true
```
</details>

<details>
<summary>Python Template</summary>

```yaml
name: Test & Validate (Python)
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install uv && uv pip install -e . || uv pip install -r requirements.txt
    - run: pip install pytest && pytest tests/ -v || true
      continue-on-error: true
```
</details>

<details>
<summary>Go Template</summary>

```yaml
name: Test & Validate (Go)
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: ['1.21', '1.22']
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-go@v4
      with:
        go-version: ${{ matrix.go-version }}
    - run: go mod download
    - run: go test -v ./...
```
</details>

<details>
<summary>Rust Template</summary>

```yaml
name: Test & Validate (Rust)
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
    - run: cargo fmt -- --check
    - run: cargo test
```
</details>

**Then commit IMMEDIATELY:**
```bash
git add .github/workflows/test.yml TASKS.md
git commit -m "ci: setup github actions workflow"
git push origin main
```

## WORKFLOW (Every Iteration)

1. **Read the current task** from TASKS.md
2. **Understand requirements** - Ask clarifying questions if blocked
3. **Implement** - Write code/docs
4. **Test locally** - Verify it works
5. **Commit** - `git add . && git commit -m "Feature: description" && git push`
6. **Update TASKS.md** - Mark `[x]` when DONE
7. **Next iteration** - Move to next task

## CONSTRAINTS

- ❌ NO virtual environments (`venv`, `virtualenv`, `.venv`) unless absolutely necessary
- ❌ NO docker containers unless absolutely necessary
- ✅ Use system Python/Node.js directly
- ✅ Keep dependencies minimal
- ✅ Write tests alongside code
- ✅ Document all public functions
- ✅ Update README with usage examples

## FILE STRUCTURE
```
.
├── README.md          # How to run the project
├── TASKS.md          # Task list (you update this)
├── .github/workflows/test.yml  # CI pipeline you create
├── requirements.txt / package.json  # Dependencies
└── src/              # Your code
```

## SUCCESS CRITERIA (For Each Task)

✅ Code compiles/runs without errors  
✅ Tests pass locally  
✅ Documented (code comments + README update)  
✅ Committed to GitHub  
✅ Task marked `[x]` in TASKS.md  

## IF YOU GET STUCK

1. **Document the issue** in TASKS.md as a note
2. **Move to next task** - don't block progress
3. **Continue** - come back to it later
4. **Never delete tasks** - mark as blocked with explanation

## GIT WORKFLOW (Exact Commands)

```bash
# After making changes:
git add .
git commit -m "Feature: [brief description]"
git push origin main

# Push any new branches:
git push origin [branch-name]

# Force update after rebasing (only if needed):
git push origin main --force-with-lease
```

## EXECUTION MODE

- Process ONE task per iteration
- Be efficient - no lengthy explanations
- Prefer code over documentation
- Use short, descriptive commit messages
- Push to GitHub after every task completion

---

## ROLE-SPECIFIC QUICK START

### If `.agent_role = qa-specialist`
Load full instructions: `../../../agents/qa-specialist.md`

**Quick mission:**
1. Review TASKS.md for testing-related tasks
2. Create/enhance test files (`tests/`, `__tests__/`, `spec/`)
3. Run test suites locally and validate coverage
4. Update `.github/workflows/test.yml` with test steps
5. Document test setup in README
6. Commit: `git commit -m "test: [what tests you added]"`

### If `.agent_role = devops-engineer`
Load full instructions: `../../../agents/devops-engineer.md`

**Quick mission:**
1. Review TASKS.md for CI/CD and infra tasks
2. Create/enhance `.github/workflows/test.yml` and `deploy-*.yml`
3. Set up GitHub environments if needed
4. Test workflows locally with `act` tool (optional)
5. Document deployment process in README
6. Commit: `git commit -m "ci: [workflow changes]"`

### If `.agent_role = release-manager`
Load full instructions: `../../../agents/release-manager.md`

**Quick mission:**
1. Review TASKS.md for version/release tasks
2. Update version numbers in files (`package.json`, `setup.py`, etc.)
3. Create/update CHANGELOG or release notes
4. Tag releases: `git tag -a v1.0.0 -m "Release 1.0.0"`
5. Push tags: `git push origin --tags`
6. Commit: `git commit -m "chore: bump version to v1.0.0"`

### If `.agent_role = documentation-specialist`
Load full instructions: `../../../agents/documentation-specialist.md`

**Quick mission:**
1. Review TASKS.md for docs-related tasks
2. Update/expand README.md with usage examples
3. Add API/function documentation (docstrings)
4. Create/update CONTRIBUTING.md, SETUP.md, TROUBLESHOOTING.md
5. Validate all code examples work
6. Commit: `git commit -m "docs: [what documentation you added]"`

### If `.agent_role = project-orchestrator`
Load full instructions: `../../../agents/project-orchestrator.md`

**Quick mission:**
1. Review TASKS.md and identify blockers/dependencies
2. Plan which tasks can run in parallel
3. Assign work to specialists (update `.agent_role` as needed)
4. Track progress and update status
5. Escalate blockers and risks
6. Commit: `git commit -m "chore: priority update - [what changed]"`

---

## CALLING SPECIALIZED AGENTS

If a task needs a specialist you can't handle alone, update `.agent_role`:

```bash
# Switch to a specialist for specific work
echo "devops-engineer" > .agent_role
git add .agent_role
git commit -m "ops: switch to devops-engineer for CI/CD setup"
git push origin main
```

After switching, the next iteration will load that agent's expertise.

**Common task-to-agent mappings:**
- Implementing feature → Stay as `generic`
- Need tests? → Switch to `qa-specialist`
- Ready to release? → Switch to `release-manager`
- Need better docs? → Switch to `documentation-specialist`
- Complex multi-part work? → Switch to `project-orchestrator`
- Setting up CI/CD? → Switch to `devops-engineer`

Switch back to `generic` when the specialist work is done.

---

**Now start: Check `.agent_role` and read TASKS.md**

---

### ⚠️ CRITICAL TOKEN CONSTRAINTS:
- Iteration: 36 / 64k Token Budget
- Attempt: 1 (previous attempts may have partial progress)
- **Mandate:** Operate efficiently. Use partial edits, not full file rewrites when possible.
- **Output:** Be concise and action-oriented.


## CURRENT PROJECT STATE (Iteration 36)

```
# invoice-resolver-ai
**Mission:** **Startup Idea: Invoiced – Autonomous Invoice Dispute Resolver for Freelancers & Micro-SaaS**

**Problem:** Freelancers and small SaaS founders waste hours chasing unpaid invoices, drafting dispute letters, and navigating payment platforms. Payment delays and chargebacks are common, but resolution is manual and frustrating.

**Solution:** An AI agent that monitors Stripe/PayPal/Bank feeds, detects overdue or disputed invoices, and automatically:
- Sends polite follow-ups with payment links
- Drafts formal dispute letters (with evidence attachments) for chargebacks
- Escalates to small claims paperwork if needed (pre-filled forms)
- Learns which templates and timing work best (A/B test)

**Tech Stack:** Python/FastAPI, PostgreSQL, Celery, Stripe/PayPal/Bank APIs (Plaid), OpenAI/Claude for letter drafting, PDF generation (WeasyPrint or ReportLab), optional web dashboard (Streamlit).

**Monetization:** Freemium – free for up to 5 invoices/month, then $19/mo for unlimited + AI dispute drafting. Add-ons: legal template packs, multi-currency support.

**Why Wiggum can build it:** Clear tasks (scrapers, API integrations, email automation, PDF generation, simple ML for timing optimization). Well-defined data model. Can launch MVP in a week. Sells to a huge market (independent creators, indie hackers).

## Phase 1: Planning & Setup
- [x] **Task 1.1:** Design complete database schema (PostgreSQL) for users, invoices, templates, campaigns, payment connections, and A/B test results. Create ER diagram and write migration SQL.
  - *Deliverable:* `schema.sql` with tables: users (subscription_tier, invoice_limit), invoices (status, due_date, amount, stripe_payment_intent_id, paypal_txn_id, plaid_account_id), payment_connections (provider, credentials_encrypted, user_id), templates (type, content, variables), campaigns (template_id, sent_at, opened_at, paid_after), ab_tests (variant, metric, result).
- [x] **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.
  - *Deliverable:* Project scaffold with `main.py`, `core/config.py`, `core/logger.py`, `requirements.txt` or `pyproject.toml` including: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv.
- [x] **Task 1.3:** Setup PostgreSQL database locally (docker-compose.yml) and implement SQLAlchemy models with Alembic migrations for the schema.
  - *Deliverable:* `docker-compose.yml` with PostgreSQL service, `models.py` with all SQLAlchemy models, Alembic setup with initial migration.
- [x] **Task 1.4:** Create comprehensive API documentation outline and define OpenAPI specs for all endpoints to be built (authentication, invoice CRUD, webhook receivers, admin endpoints).
  - *Deliverable:* `docs/api.md` with endpoint list, request/response schemas, authentication flow (JWT), and webhook payload examples for Stripe/PayPal.

## Phase 2: Core Backend & Data Model
- [x] **Task 2.1:** Implement FastAPI user authentication system with JWT tokens, password hashing (bcrypt), and subscription tier enforcement middleware (check invoice limits for freemium users).
  - *Deliverable:* `api/auth.py` with /register, /login, /refresh endpoints, `middleware.py` with SubscriptionLimitChecker, and protected route decorator.
- [x] **Task 2.2:** Build invoice management endpoints: create invoice (manual import), list invoices with filters (status, due_date range), update status (mark as paid/disputed), and soft delete. Integrate with database models.
  - *Deliverable:* `api/invoices.py` with CRUD operations, Pydantic schemas for InvoiceCreate/Update/Response, and integration tests using pytest.
- [x] **Task 2.3:** Implement webhook receivers for Stripe (invoice.payment_failed, charge.dispute.created) and PayPal (PAYMENT.DENIED, DISPUTE.CREATED) to automatically update invoice status in database.
  - *Deliverable:* `api/webhooks.py` with signature verification for Stripe (webhook secret) and PayPal (transmission ID + secret), endpoint at /webhooks/{provider}, event handler functions that update invoice records and trigger Celery tasks.
- [x] **Task 2.4:** Setup Celery with Redis broker, create worker processes, and implement background task for invoice status synchronization (periodic polling as fallback if webhooks fail).
  - *Deliverable:* `celery_app.py` configured with Redis, `tasks/sync.py` with periodic task (every 15 min) that queries Stripe/PayPal APIs for invoice status updates, and worker startup script.

## Phase 3: Integrations & AI Features
- [x] **Task 3.1:** Implement payment provider integration layer: Stripe API client (stripe-python) for retrieving invoices, payment intents, and customers; PayPal API client (paypalrestsdk) for txns and disputes; Plaid integration for bank feed linking (link token creation, transactions sync).
  - *Deliverable:* `integrations/stripe_client.py`, `integrations/paypal_client.py`, `integrations/plaid_client.py` with functions: connect_account, get_invoice_status, list_transactions, and error handling.
- [x] **Task 3.2:** Build email automation system using SendGrid or SMTP (smtplib) with template rendering (Jinja2). Create follow-up sequences: 3-day reminder, 7-day late notice, 14-day final notice before dispute.
  - *Deliverable:* `email/sender.py` with send_followup_email(invoice, template_type), `email/templates/` directory with HTML templates for each follow-up stage, and queue system using Celery for scheduled sends.
- [x] **Task 3.3:** Integrate AI letter drafting using OpenAI GPT-4 or Anthropic Claude. Create prompts for formal dispute letters that include invoice details, payment evidence (dates, amounts, communication logs), and legal references (small claims requirements).
  - *Deliverable:* `ai/dispute_drafter.py` with function draft_dispute_letter(invoice, evidence_list) that calls OpenAI API with structured prompt, returns LaTeX or HTML letter content, and includes cost tracking.
- [x] **Task 3.4:** Implement PDF generation for dispute letters and small claims forms using WeasyPrint (HTML->PDF) or ReportLab. Create templates for common small claims forms (pre-filled with user/business info).
  - *Deliverable:* `pdf/generator.py` with generate_pdf(html_content, output_path) using WeasyPrint, `pdf/templates/` directory with base letter template and small claims form template, and storage to S3 or local filesystem.

## Phase 4: Dashboard & Analytics
- [x] **Task 4.1:** Build Streamlit dashboard for users to view invoice status, payment connections, campaign metrics, and AI letter drafts. Include authentication with JWT and real-time updates via FastAPI endpoints.
  - *Deliverable:* `dashboard/app.py` with pages: Overview (KPIs: overdue count, recovery rate), Invoices (table with filters), Campaigns (A/B test results), Settings (payment connections). Uses streamlit-authenticator for login.
- [x] **Task 4.2:** Implement A/B testing framework for follow-up templates and timing. Store template variants and send times, track opens (pixel tracking) and payments after send, calculate conversion rates.
  - *Deliverable:* `ab_testing/experiment.py` with ABTest model, assign_variant(user_id, test_name) function, tracking endpoints for email opens (/track/open/<campaign_id>), and analysis query to report winning variants.
- [x] **Task 4.3:** Create admin panel (FastAPI + simple HTML/JS or separate Streamlit page) for viewing all users, system health (Celery workers, API latency), and managing subscription tiers.
  - *Deliverable:* `admin/` directory with FastAPI routes under /admin/* (require admin role), dashboard showing user count, active connections, recent webhook events, and form to upgrade/downgrade users.
- [ ] **Task 4.4:** Implement billing integration with Stripe Billing or Paddle for subscription management. Create plans: Free (5 invoices/month), Pro ($19/mo unlimited), add-ons ($5 legal pack, $3 multi-currency). Webhook to handle subscription updates.
  - *Deliverable:* `billing/stripe_billing.py` with create_checkout_session(user, plan_id), webhook handler for customer.subscription.updated/deleted to update user.subscription_tier in DB, and plan definitions in FastAPI config.

## Phase 5: Testing & Deployment (Optional Bonus)
- [ ] **Task 5.1:** Write comprehensive test suite with pytest: unit tests for all services (email, AI, PDF), integration tests for API endpoints using TestClient, and mocked external API tests (Stripe/PayPal/OpenAI).
  - *Deliverable:* `tests/` directory with >80% coverage, `pytest.ini` configured, fixtures for database and mock clients, CI GitHub Actions workflow running tests on push.
- [ ] **Task 5.2:** Containerize application with Docker multi-stage build: separate images for FastAPI, Celery worker, Redis, PostgreSQL. Create docker-compose.prod.yml for deployment with secrets management.
  - *Deliverable:* `Dockerfile` for API, `Dockerfile.celery` for worker, `docker-compose.prod.yml` with all services, healthchecks, and volume mounts for logs/media.
- [ ] **Task 5.3:** Deploy to cloud (Heroku, Fly.io, or AWS) with SSL, automated backups (PostgreSQL), monitoring (Sentry for errors, Prometheus metrics), and CI/CD pipeline.
  - *Deliverable:* Deployment script (`deploy.sh`) or GitHub Actions workflow, sentry config, metrics endpoint at /metrics, and runbook for backup/restore procedures.
```

## NEXT TASK TO COMPLETE:
**Task 4.4:** Implement billing integration with Stripe Billing or Paddle for subscription management. Create plans: Free (5 invoices/month), Pro ($19/mo unlimited), add-ons ($5 legal pack, $3 multi-currency). Webhook to handle subscription updates.

**Instructions:** Complete this task. Mark [x] in TASKS.md when done. Create, modify, or delete files as needed. Execute commands as needed. Also update README.md to match this project (name, setup instructions, current progress). No permission needed—just act.
```

## OpenCode Output

```
[0m
> build · stepfun/step-3.5-flash:free
[0m
[0m→ [0mRead .
[0m→ [0mRead TASKS.md
[0m→ [0mRead README.md
I'll complete Task 4.4: Implement billing integration with Stripe Billing for subscription management. Let me start by checking the current project structure and understanding what's already in place.
Now let me check the existing models and config to understand the structure:
[0m→ [0mRead src/models.py
[0m✱ [0mGlob "**/*.py"[90m in src · 33 matches[0m
[0m→ [0mRead src/core/config.py
Let me check the requirements.txt and .env.example to understand the dependencies and environment setup:
[0m→ [0mRead requirements.txt
[0m→ [0mRead .env.example
Perfect! Stripe is already in dependencies. Now let me create the billing module. I'll start by creating the directory structure and implementing Stripe Billing integration:
[0m
[0m$ [0mmkdir -p src/billing tests
Now let me create the billing schemas:
[0m
[0m← [0mWrite src/billing/schemas.py
Wrote file successfully.
[0m
Now let me create the main Stripe billing implementation:
[0m← [0mWrite src/billing/stripe_billing.py
Wrote file successfully.
[0m
Now create the __init__.py for the billing module:
[0m← [0mWrite src/billing/__init__.py
Wrote file successfully.

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py">
ERROR [17:30] "SubscriptionStatus" is unknown import symbol
ERROR [170:19] "error" is not exported from module "stripe"
ERROR [168:17] Argument of type "str | None" cannot be assigned to parameter "url" of type "str" in function "__init__"
  Type "str | None" is not assignable to type "str"
    "None" is not assignable to "str"
ERROR [199:23] "error" is not exported from module "stripe"
ERROR [206:14] Argument of type "str | None" cannot be assigned to parameter "name" of type "str" in function "create"
  Type "str | None" is not assignable to type "str"
    "None" is not assignable to "str"
ERROR [239:20] "error" is not exported from module "stripe"
ERROR [256:12] Type "Any | None" is not assignable to return type "str"
  Type "Any | None" is not assignable to type "str"
    "None" is not assignable to "str"
ERROR [422:19] "error" is not exported from module "stripe"
ERROR [417:68] Cannot access attribute "current_period_end" for class "Subscription"
  Attribute "current_period_end" is unknown
</diagnostics>
[0m
I need to fix the type errors in stripe_billing.py:
[0m→ [0mRead src/billing/stripe_billing.py
Let me fix the stripe_billing.py with proper error handling and type fixes:
[0m
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -13,18 +13,17 @@
 from sqlalchemy.orm import Session
 from datetime import datetime
 
 from src.core.config import settings
-from src.models import User, SubscriptionStatus as models_SubscriptionStatus
+from src.models import User
 from src.billing.schemas import (
     CheckoutSessionRequest,
     CheckoutSessionResponse,
     SubscriptionStatus,
     StripePrice,
     SubscriptionUpdateWebhook,
 )
 
-
 # Stripe API configuration
 stripe.api_key = settings.stripe_api_key
 
 

[0m
Let me rewrite the file with proper error handling and type safety:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -124,9 +124,9 @@
     Returns:
         CheckoutSessionResponse with session ID and URL
 
     Raises:
-        stripe.error.StripeError: If Stripe API call fails
+        stripe.StripeError: If Stripe API call fails
         ValueError: If plan_id is invalid
     """
     plan = get_plan_by_price_id(plan_id)
     if not plan:
@@ -151,10 +151,11 @@
                     "quantity": 1,
                 }
             ],
             mode="subscription",
-            success_url=success_url,
-            cancel_url=cancel_url,
+            success_url=success_url
+            or f"{settings.api_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
+            cancel_url=cancel_url or f"{settings.api_base_url}/billing/cancel",
             metadata={
                 "user_id": user.id,
                 "plan_name": plan.name,
                 "invoice_limit": str(plan.invoice_limit),
@@ -163,11 +164,11 @@
         )
 
         return CheckoutSessionResponse(
             session_id=checkout_session.id,
-            url=checkout_session.url,
+            url=checkout_session.url or "",
         )
-    except stripe.error.StripeError as e:
+    except stripe.StripeError:
         raise
 
 
 def _get_or_create_customer(user: User) -> str:

[0m
Let me fix the remaining issues by editing specific sections:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -202,9 +202,9 @@
 
 # Create new customer
 customer = stripe.Customer.create(
     email=user.email,
-    name=user.full_name or user.company_name,
+    name=user.full_name or user.company_name or user.email,
     metadata={
         "user_id": user.id,
     },
 )

[0m
Let me add proper exception imports and fix the Stripe error handling:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -25,9 +25,17 @@
 
 # Stripe API configuration
 stripe.api_key = settings.stripe_api_key
 
+# Import Stripe exceptions
+try:
+    from stripe.error import StripeError, SignatureVerificationError
+except ImportError:
+    # Fallback for older stripe versions
+    StripeError = Exception
+    SignatureVerificationError = Exception
 
+
 # Plan definitions - these map to Stripe Price IDs
 # Prices should be created in Stripe Dashboard and their IDs set in environment variables
 PLANS = {
     "free": StripePrice(

[0m
Let me simplify the exception handling to work with the Stripe library by using the top-level exceptions:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -25,17 +25,9 @@
 
 # Stripe API configuration
 stripe.api_key = settings.stripe_api_key
 
-# Import Stripe exceptions
-try:
-    from stripe.error import StripeError, SignatureVerificationError
-except ImportError:
-    # Fallback for older stripe versions
-    StripeError = Exception
-    SignatureVerificationError = Exception
 
-
 # Plan definitions - these map to Stripe Price IDs
 # Prices should be created in Stripe Dashboard and their IDs set in environment variables
 PLANS = {
     "free": StripePrice(

[0m
Let me fix the remaining issues comprehensively:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -124,9 +124,9 @@
     Returns:
         CheckoutSessionResponse with session ID and URL
 
     Raises:
-        stripe.StripeError: If Stripe API call fails
+        Exception: If Stripe API call fails
         ValueError: If plan_id is invalid
     """
     plan = get_plan_by_price_id(plan_id)
     if not plan:
@@ -140,36 +140,32 @@
         success_url = f"{settings.api_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
     if not cancel_url:
         cancel_url = f"{settings.api_base_url}/billing/cancel"
 
-    try:
-        checkout_session = stripe.checkout.Session.create(
-            customer=customer_id,
-            billing_address_collection="required",
-            line_items=[
-                {
-                    "price": plan_id,
-                    "quantity": 1,
-                }
-            ],
-            mode="subscription",
-            success_url=success_url
-            or f"{settings.api_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
-            cancel_url=cancel_url or f"{settings.api_base_url}/billing/cancel",
-            metadata={
-                "user_id": user.id,
-                "plan_name": plan.name,
-                "invoice_limit": str(plan.invoice_limit),
-            },
-            allow_promotion_codes=True,
-        )
+    checkout_session = stripe.checkout.Session.create(
+        customer=customer_id,
+        billing_address_collection="required",
+        line_items=[
+            {
+                "price": plan_id,
+                "quantity": 1,
+            }
+        ],
+        mode="subscription",
+        success_url=success_url,
+        cancel_url=cancel_url,
+        metadata={
+            "user_id": user.id,
+            "plan_name": plan.name,
+            "invoice_limit": str(plan.invoice_limit),
+        },
+        allow_promotion_codes=True,
+    )
 
-        return CheckoutSessionResponse(
-            session_id=checkout_session.id,
-            url=checkout_session.url or "",
-        )
-    except stripe.StripeError:
-        raise
+    return CheckoutSessionResponse(
+        session_id=checkout_session.id,
+        url=checkout_session.url or "",
+    )
 
 
 def _get_or_create_customer(user: User) -> str:
     """

[0m
Let me fix all remaining issues by editing the problematic sections:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -191,9 +191,9 @@
     try:
         # Verify customer exists
         customer = stripe.Customer.retrieve(customer_id)
         return customer.id
-    except stripe.error.StripeError:
+    except Exception:
         # Customer doesn't exist, create a new one
         pass
 
 # Create new customer

[0m
Let me replace the handle_webhook_event function properly:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -224,19 +224,22 @@
 Returns:
     Event ID that was processed
 
 Raises:
-    stripe.error.SignatureVerificationError: If signature verification fails
-    ValueError: If event processing fails
+    ValueError: If signature verification fails or event processing fails
 """
 try:
     event = stripe.Webhook.construct_event(
         payload, signature, settings.stripe_webhook_secret
     )
-except (stripe.error.SignatureVerificationError, ValueError) as e:
-    raise
+except Exception as e:
+    # Handle signature verification errors and other construct issues
+    raise ValueError(f"Webhook verification failed: {e}") from e
 
 event_id = event.get("id")
+if not event_id:
+    raise ValueError("Event ID missing from webhook payload")
+
 event_type = event.get("type")
 
 # Process based on event type
 if event_type == "customer.subscription.updated":

[0m
Let me fix the last two errors in get_subscription_info:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -408,18 +408,21 @@
 
         price = items[0].get("price", {})
         plan = get_plan_by_price_id(price.get("id"))
 
+        # Stripe returns current_period_end as a Unix timestamp (int)
+        current_period_end = datetime.fromtimestamp(subscription.current_period_end)  # type: ignore
+
         return SubscriptionStatus(
             tier=user.subscription_tier,
             stripe_customer_id=customer_id,
             stripe_subscription_id=subscription.id,
-            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
+            current_period_end=current_period_end,
             cancel_at_period_end=subscription.cancel_at_period_end,
             status=subscription.status,
             plan=plan,
         )
-    except stripe.error.StripeError:
+    except Exception:
         return None
 
 
 def calculate_invoice_limit(tier: str) -> int:

[0m
Now let me create the API routes for billing:
[0m← [0mWrite src/api/billing.py
Wrote file successfully.
[0m
Now let me check main.py to see how to include the billing router:
[0m→ [0mRead src/main.py
Let me add the billing router to main.py:
[0m
[0m← [0mEdit src/main.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
@@ -6,8 +6,9 @@
 from .api.auth import router as auth_router
 from .api.invoices import router as invoices_router
 from .api.webhooks import router as webhooks_router
 from .api.ab_testing import router as ab_testing_router
+from .api.billing import router as billing_router
 from .admin import admin_router
 from .middleware import SubscriptionLimitCheckerMiddleware
 
 # Setup logging

[0m
[0m← [0mEdit src/main.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
@@ -39,8 +39,9 @@
 app.include_router(auth_router)
 app.include_router(invoices_router)
 app.include_router(webhooks_router)
 app.include_router(ab_testing_router)
+app.include_router(billing_router)
 app.include_router(admin_router)
 
 # Future routers (to be implemented in later tasks)
 # app.include_router(invoice_router, prefix="/api/invoices", tags=["invoices"])

[0m
Now let me update the .env.example to add Stripe price IDs:
[0m← [0mEdit .env.example
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/.env.example
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/.env.example
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/.env.example
@@ -14,8 +14,13 @@
 
 # Stripe
 STRIPE_API_KEY=sk_test_your_stripe_api_key
 STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
+# Stripe Price IDs for subscription plans (create these in Stripe Dashboard)
+STRIPE_PRICE_FREE=price_free_placeholder
+STRIPE_PRICE_PRO=price_pro_placeholder
+STRIPE_PRICE_LEGAL_PACK=price_legal_placeholder
+STRIPE_PRICE_MULTI_CURRENCY=price_mc_placeholder
 
 # PayPal
 PAYPAL_CLIENT_ID=your_paypal_client_id
 PAYPAL_CLIENT_SECRET=your_paypal_client_secret

[0m
Let me update config.py to include the Stripe price ID environment variables:
[0m← [0mEdit src/core/config.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py
@@ -23,8 +23,12 @@
 
 # Stripe
 stripe_api_key: Optional[str] = None
 stripe_webhook_secret: Optional[str] = None
+stripe_price_free: Optional[str] = None
+stripe_price_pro: Optional[str] = None
+stripe_price_legal_pack: Optional[str] = None
+stripe_price_multi_currency: Optional[str] = None
 
 # PayPal
 paypal_client_id: Optional[str] = None
 paypal_client_secret: Optional[str] = None

[0m
Now let me create comprehensive tests for the billing module:
[0m← [0mWrite tests/test_billing.py
Wrote file successfully.

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py">
ERROR [15:31] "get_db" is unknown import symbol
ERROR [122:41] Argument of type "bytes" cannot be assigned to parameter "payload" of type "Dict[str, Any]" in function "handle_webhook_event"
  "bytes" is not assignable to "Dict[str, Any]"
ERROR [150:9] "db" is not defined
</diagnostics>
[0m
[0m✗ [0medit failed
[91m[1mError: [0mNo changes to apply: oldString and newString are identical.
Let me fix the api/billing.py by adding the missing import and fixing function signatures:
Let me read the billing.py file to see the actual content and the imports:
[0m→ [0mRead src/api/billing.py[90m [limit=50][0m
Let me read more of billing.py to see the get_invoice_limit endpoint:
[0m→ [0mRead src/api/billing.py[90m [offset=140][0m
```

## TASKS.md After Iteration

```markdown
# invoice-resolver-ai
**Mission:** **Startup Idea: Invoiced – Autonomous Invoice Dispute Resolver for Freelancers & Micro-SaaS**

**Problem:** Freelancers and small SaaS founders waste hours chasing unpaid invoices, drafting dispute letters, and navigating payment platforms. Payment delays and chargebacks are common, but resolution is manual and frustrating.

**Solution:** An AI agent that monitors Stripe/PayPal/Bank feeds, detects overdue or disputed invoices, and automatically:
- Sends polite follow-ups with payment links
- Drafts formal dispute letters (with evidence attachments) for chargebacks
- Escalates to small claims paperwork if needed (pre-filled forms)
- Learns which templates and timing work best (A/B test)

**Tech Stack:** Python/FastAPI, PostgreSQL, Celery, Stripe/PayPal/Bank APIs (Plaid), OpenAI/Claude for letter drafting, PDF generation (WeasyPrint or ReportLab), optional web dashboard (Streamlit).

**Monetization:** Freemium – free for up to 5 invoices/month, then $19/mo for unlimited + AI dispute drafting. Add-ons: legal template packs, multi-currency support.

**Why Wiggum can build it:** Clear tasks (scrapers, API integrations, email automation, PDF generation, simple ML for timing optimization). Well-defined data model. Can launch MVP in a week. Sells to a huge market (independent creators, indie hackers).

## Phase 1: Planning & Setup
- [x] **Task 1.1:** Design complete database schema (PostgreSQL) for users, invoices, templates, campaigns, payment connections, and A/B test results. Create ER diagram and write migration SQL.
  - *Deliverable:* `schema.sql` with tables: users (subscription_tier, invoice_limit), invoices (status, due_date, amount, stripe_payment_intent_id, paypal_txn_id, plaid_account_id), payment_connections (provider, credentials_encrypted, user_id), templates (type, content, variables), campaigns (template_id, sent_at, opened_at, paid_after), ab_tests (variant, metric, result).
- [x] **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.
  - *Deliverable:* Project scaffold with `main.py`, `core/config.py`, `core/logger.py`, `requirements.txt` or `pyproject.toml` including: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv.
- [x] **Task 1.3:** Setup PostgreSQL database locally (docker-compose.yml) and implement SQLAlchemy models with Alembic migrations for the schema.
  - *Deliverable:* `docker-compose.yml` with PostgreSQL service, `models.py` with all SQLAlchemy models, Alembic setup with initial migration.
- [x] **Task 1.4:** Create comprehensive API documentation outline and define OpenAPI specs for all endpoints to be built (authentication, invoice CRUD, webhook receivers, admin endpoints).
  - *Deliverable:* `docs/api.md` with endpoint list, request/response schemas, authentication flow (JWT), and webhook payload examples for Stripe/PayPal.

## Phase 2: Core Backend & Data Model
- [x] **Task 2.1:** Implement FastAPI user authentication system with JWT tokens, password hashing (bcrypt), and subscription tier enforcement middleware (check invoice limits for freemium users).
  - *Deliverable:* `api/auth.py` with /register, /login, /refresh endpoints, `middleware.py` with SubscriptionLimitChecker, and protected route decorator.
- [x] **Task 2.2:** Build invoice management endpoints: create invoice (manual import), list invoices with filters (status, due_date range), update status (mark as paid/disputed), and soft delete. Integrate with database models.
  - *Deliverable:* `api/invoices.py` with CRUD operations, Pydantic schemas for InvoiceCreate/Update/Response, and integration tests using pytest.
- [x] **Task 2.3:** Implement webhook receivers for Stripe (invoice.payment_failed, charge.dispute.created) and PayPal (PAYMENT.DENIED, DISPUTE.CREATED) to automatically update invoice status in database.
  - *Deliverable:* `api/webhooks.py` with signature verification for Stripe (webhook secret) and PayPal (transmission ID + secret), endpoint at /webhooks/{provider}, event handler functions that update invoice records and trigger Celery tasks.
- [x] **Task 2.4:** Setup Celery with Redis broker, create worker processes, and implement background task for invoice status synchronization (periodic polling as fallback if webhooks fail).
  - *Deliverable:* `celery_app.py` configured with Redis, `tasks/sync.py` with periodic task (every 15 min) that queries Stripe/PayPal APIs for invoice status updates, and worker startup script.

## Phase 3: Integrations & AI Features
- [x] **Task 3.1:** Implement payment provider integration layer: Stripe API client (stripe-python) for retrieving invoices, payment intents, and customers; PayPal API client (paypalrestsdk) for txns and disputes; Plaid integration for bank feed linking (link token creation, transactions sync).
  - *Deliverable:* `integrations/stripe_client.py`, `integrations/paypal_client.py`, `integrations/plaid_client.py` with functions: connect_account, get_invoice_status, list_transactions, and error handling.
- [x] **Task 3.2:** Build email automation system using SendGrid or SMTP (smtplib) with template rendering (Jinja2). Create follow-up sequences: 3-day reminder, 7-day late notice, 14-day final notice before dispute.
  - *Deliverable:* `email/sender.py` with send_followup_email(invoice, template_type), `email/templates/` directory with HTML templates for each follow-up stage, and queue system using Celery for scheduled sends.
- [x] **Task 3.3:** Integrate AI letter drafting using OpenAI GPT-4 or Anthropic Claude. Create prompts for formal dispute letters that include invoice details, payment evidence (dates, amounts, communication logs), and legal references (small claims requirements).
  - *Deliverable:* `ai/dispute_drafter.py` with function draft_dispute_letter(invoice, evidence_list) that calls OpenAI API with structured prompt, returns LaTeX or HTML letter content, and includes cost tracking.
- [x] **Task 3.4:** Implement PDF generation for dispute letters and small claims forms using WeasyPrint (HTML->PDF) or ReportLab. Create templates for common small claims forms (pre-filled with user/business info).
  - *Deliverable:* `pdf/generator.py` with generate_pdf(html_content, output_path) using WeasyPrint, `pdf/templates/` directory with base letter template and small claims form template, and storage to S3 or local filesystem.

## Phase 4: Dashboard & Analytics
- [x] **Task 4.1:** Build Streamlit dashboard for users to view invoice status, payment connections, campaign metrics, and AI letter drafts. Include authentication with JWT and real-time updates via FastAPI endpoints.
  - *Deliverable:* `dashboard/app.py` with pages: Overview (KPIs: overdue count, recovery rate), Invoices (table with filters), Campaigns (A/B test results), Settings (payment connections). Uses streamlit-authenticator for login.
- [x] **Task 4.2:** Implement A/B testing framework for follow-up templates and timing. Store template variants and send times, track opens (pixel tracking) and payments after send, calculate conversion rates.
  - *Deliverable:* `ab_testing/experiment.py` with ABTest model, assign_variant(user_id, test_name) function, tracking endpoints for email opens (/track/open/<campaign_id>), and analysis query to report winning variants.
- [x] **Task 4.3:** Create admin panel (FastAPI + simple HTML/JS or separate Streamlit page) for viewing all users, system health (Celery workers, API latency), and managing subscription tiers.
  - *Deliverable:* `admin/` directory with FastAPI routes under /admin/* (require admin role), dashboard showing user count, active connections, recent webhook events, and form to upgrade/downgrade users.
- [ ] **Task 4.4:** Implement billing integration with Stripe Billing or Paddle for subscription management. Create plans: Free (5 invoices/month), Pro ($19/mo unlimited), add-ons ($5 legal pack, $3 multi-currency). Webhook to handle subscription updates.
  - *Deliverable:* `billing/stripe_billing.py` with create_checkout_session(user, plan_id), webhook handler for customer.subscription.updated/deleted to update user.subscription_tier in DB, and plan definitions in FastAPI config.

## Phase 5: Testing & Deployment (Optional Bonus)
- [ ] **Task 5.1:** Write comprehensive test suite with pytest: unit tests for all services (email, AI, PDF), integration tests for API endpoints using TestClient, and mocked external API tests (Stripe/PayPal/OpenAI).
  - *Deliverable:* `tests/` directory with >80% coverage, `pytest.ini` configured, fixtures for database and mock clients, CI GitHub Actions workflow running tests on push.
- [ ] **Task 5.2:** Containerize application with Docker multi-stage build: separate images for FastAPI, Celery worker, Redis, PostgreSQL. Create docker-compose.prod.yml for deployment with secrets management.
  - *Deliverable:* `Dockerfile` for API, `Dockerfile.celery` for worker, `docker-compose.prod.yml` with all services, healthchecks, and volume mounts for logs/media.
- [ ] **Task 5.3:** Deploy to cloud (Heroku, Fly.io, or AWS) with SSL, automated backups (PostgreSQL), monitoring (Sentry for errors, Prometheus metrics), and CI/CD pipeline.
  - *Deliverable:* Deployment script (`deploy.sh`) or GitHub Actions workflow, sentry config, metrics endpoint at /metrics, and runbook for backup/restore procedures.
```

**Completed at:** Fri Mar 20 11:53:12 PM EDT 2026
