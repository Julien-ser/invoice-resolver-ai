# Iteration 37 - invoice-resolver-ai

**Timestamp:** Fri Mar 20 11:53:15 PM EDT 2026
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
- Iteration: 37 / 64k Token Budget
- Attempt: 2 (previous attempts may have partial progress)
- **Mandate:** Operate efficiently. Use partial edits, not full file rewrites when possible.
- **Output:** Be concise and action-oriented.


## CURRENT PROJECT STATE (Iteration 37)

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
I'll implement the billing integration with Stripe Billing for subscription management. Let me first check the current project structure and existing files.
[0m✗ [0mread failed
[91m[1mError: [0mFile not found: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/models.py
[0m✱ [0mGlob "**/*.py"[90m 49 matches[0m
[0m→ [0mRead requirements.txt
[0m→ [0mRead src/models.py
[0m→ [0mRead src/billing/stripe_billing.py
[0m→ [0mRead src/api/billing.py
[0m→ [0mRead src/core/config.py
[0m→ [0mRead src/billing/schemas.py
[0m→ [0mRead tests/test_billing.py
Now let me check the billing schemas and test file to understand what's expected:
I can see the billing integration is mostly implemented but there are critical gaps: the `SubscriptionUpdater` class methods are just stubs (empty `pass` statements). These need to actually update the database. Let me also check the database module:
[0m→ [0mRead src/core/database.py
[0m
[0m# [0mTodos
[ ] Implement SubscriptionUpdater.update_user_tier() to update user subscription in DB
[ ] Implement SubscriptionUpdater.downgrade_to_free() to downgrade user to free tier
[ ] Modify webhook handlers to accept DB session and pass to SubscriptionUpdater
[ ] Update handle_webhook_event signature to accept DB session
[ ] Update FastAPI webhook endpoint to pass DB session
[ ] Add imports for Session in stripe_billing.py
[ ] Write tests for database update logic
[ ] Verify all billing tests pass
[ ] Update README with billing setup instructions
[0m
Now I'll create a todo list and implement the missing functionality for the billing integration:
[0m# [0mTodos
[ ] Implement SubscriptionUpdater.update_user_tier() to update user subscription in DB
[ ] Implement SubscriptionUpdater.downgrade_to_free() to downgrade user to free tier
[ ] Modify webhook handlers to accept DB session and pass to SubscriptionUpdater
[ ] Update handle_webhook_event signature to accept DB session
[ ] Update FastAPI webhook endpoint to pass DB session
[ ] Add imports for Session in stripe_billing.py
[ ] Write tests for database update logic
[ ] Verify all billing tests pass
[ ] Update README with billing setup instructions
[0m
[0m✗ [0medit failed
[91m[1mError: [0mNo changes to apply: oldString and newString are identical.
Let me start implementing the missing functionality in `stripe_billing.py`. I'll need to modify the file to add the database session and implement the updater methods:
Good, the import is already there. Now let me implement the `SubscriptionUpdater` methods:
[0m
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -342,35 +342,67 @@
 class SubscriptionUpdater:
     """Helper class for updating subscription status in database."""
 
     @staticmethod
-    def update_user_tier(user_id: str, tier: str, subscription: Dict[str, Any]) -> None:
+    def update_user_tier(
+        db: Session, user_id: str, tier: str, subscription: Dict[str, Any]
+    ) -> None:
         """
         Update user's subscription tier in database.
 
-        This method should be called with a proper SQLAlchemy session.
-        It is separated from _handle_subscription_updated to allow proper session management.
-
         Args:
+            db: SQLAlchemy database session
             user_id: User UUID
             tier: New subscription tier (free, pro, enterprise)
             subscription: Full Stripe subscription object
         """
-        # This will be implemented in the webhook route with proper DB session
-        pass
+        from src.models import User
 
+        user = db.query(User).filter(User.id == user_id).first()
+        if not user:
+            return
+
+        # Update subscription tier
+        user.subscription_tier = tier
+
+        # Update invoice limit based on tier
+        plan = get_plan_by_tier(tier)
+        if plan:
+            user.invoice_limit = plan.invoice_limit
+
+        # Store Stripe customer ID in extra_data if not already present
+        customer_id = subscription.get("customer")
+        if customer_id:
+            if not hasattr(user, "extra_data") or user.extra_data is None:
+                user.extra_data = {}
+            user.extra_data["stripe_customer_id"] = customer_id
+
+        db.commit()
+
     @staticmethod
-    def downgrade_to_free(user_id: str) -> None:
+    def downgrade_to_free(db: Session, user_id: str) -> None:
         """
         Downgrade user to free tier.
 
         Args:
+            db: SQLAlchemy database session
             user_id: User UUID
         """
-        # This will be implemented in the webhook route with proper DB session
-        pass
+        from src.models import User
 
+        user = db.query(User).filter(User.id == user_id).first()
+        if not user:
+            return
 
+        user.subscription_tier = "free"
+        user.invoice_limit = 5  # Free tier limit
+
+        # Note: We don't remove stripe_customer_id from extra_data
+        # because it's useful for future re-subscriptions
+
+        db.commit()
+
+
 def get_subscription_info(user: User) -> Optional[SubscriptionStatus]:
     """
     Get current subscription information for a user.
 

[0m
Now I need to update the webhook handler functions to accept and use the DB session:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -254,18 +254,18 @@
 
     return event_id
 
 
-def _handle_subscription_updated(subscription: Dict[str, Any]) -> None:
+def _handle_subscription_updated(db: Session, subscription: Dict[str, Any]) -> None:
     """
     Handle subscription update event from Stripe.
 
     Updates the user's subscription tier based on the subscription's price.
 
     Args:
+        db: SQLAlchemy database session
         subscription: Stripe subscription object
     """
-    db: Optional[Session] = None
     try:
         # Get user_id from metadata
         user_id = subscription.get("metadata", {}).get("user_id")
         if not user_id:
@@ -296,11 +296,9 @@
             else plan.name.lower()
         )
 
         # Update user in database
-        # This function should be called with a proper DB session from the webhook endpoint
-        # The actual update happens in the webhook route handler
-        SubscriptionUpdater.update_user_tier(user_id, tier, subscription)
+        SubscriptionUpdater.update_user_tier(db, user_id, tier, subscription)
 
     except Exception as e:
         # Log error but don't fail webhook (already processed by Stripe)
         import sys

[0m
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -305,22 +305,22 @@
 
         print(f"Error handling subscription update: {e}", file=sys.stderr)
 
 
-def _handle_subscription_deleted(subscription: Dict[str, Any]) -> None:
+def _handle_subscription_deleted(db: Session, subscription: Dict[str, Any]) -> None:
     """
     Handle subscription deletion/cancellation.
 
     Args:
+        db: SQLAlchemy database session
         subscription: Stripe subscription object
     """
     user_id = subscription.get("metadata", {}).get("user_id")
     if not user_id:
         return
 
     # Downgrade user to free tier
-    # The actual update happens in the webhook route handler
-    SubscriptionUpdater.downgrade_to_free(user_id)
+    SubscriptionUpdater.downgrade_to_free(db, user_id)
 
 
 def _handle_checkout_session_completed(session: Dict[str, Any]) -> None:
     """

[0m
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -212,13 +212,14 @@
 
     return customer.id
 
 
-def handle_webhook_event(payload: Dict[str, Any], signature: str) -> str:
+def handle_webhook_event(db: Session, payload: Dict[str, Any], signature: str) -> str:
     """
     Verify and process a Stripe webhook event.
 
     Args:
+        db: SQLAlchemy database session
         payload: Raw webhook payload (bytes decoded to dict)
         signature: Stripe-Signature header value
 
     Returns:
@@ -243,12 +244,12 @@
 
     # Process based on event type
     if event_type == "customer.subscription.updated":
         subscription = event["data"]["object"]
-        _handle_subscription_updated(subscription)
+        _handle_subscription_updated(db, subscription)
     elif event_type == "customer.subscription.deleted":
         subscription = event["data"]["object"]
-        _handle_subscription_deleted(subscription)
+        _handle_subscription_deleted(db, subscription)
     elif event_type == "checkout.session.completed":
         session = event["data"]["object"]
         _handle_checkout_session_completed(session)
 

[0m
The LSP errors are expected since I haven't updated the calls yet. Now let me update the FastAPI webhook endpoint to pass the DB session:
[0m← [0mEdit src/api/billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
@@ -118,9 +118,9 @@
         detail="Missing Stripe-Signature header",
     )
 
 try:
-    event_id = handle_webhook_event(payload, signature)
+    event_id = handle_webhook_event(db, payload, signature)
     return {"status": "success", "event_id": event_id}
 except ValueError as e:
     # Signature verification failed or invalid payload
     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

[0m
I see there are multiple LSP errors. Let me address them:

1. The `handle_webhook_event` should accept `bytes` for payload, not `Dict[str, Any]`
2. The import error for `get_db` might be an LSP issue - let me verify the import in billing.py
3. Line 150 issue: `db` is not defined in `get_invoice_limit` endpoint

Let me check the import in `billing.py` more carefully:
[0m→ [0mRead src/api/billing.py[90m [limit=20][0m
[0m✗ [0medit failed
[91m[1mError: [0mCould not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
I see the issues:

1. The `get_invoice_limit` endpoint needs `db` parameter
2. `handle_webhook_event` should accept `bytes` for payload (Stripe expects raw bytes)

Let me fix these:
[0m
[0m← [0mEdit src/api/billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/billing.py
@@ -133,8 +133,9 @@
 
 @router.get("/invoice-limit")
 async def get_invoice_limit(
     current_user: User = Depends(get_current_user),
+    db: Session = Depends(get_db),
 ) -> dict:
     """
     Get current user's invoice limit based on subscription tier.
 

[0m
[0m→ [0mRead src/api/billing.py[90m [limit=25, offset=130][0m
[0m→ [0mRead src/billing/stripe_billing.py[90m [limit=30, offset=210][0m
Let me read the current state of the files and make the edits more carefully:
Good! I see the `get_invoice_limit` already has `db` parameter (line 137), so that's fixed. Now I need to fix the `handle_webhook_event` signature to accept `bytes` for payload:
[0m
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -212,9 +212,9 @@
 
     return customer.id
 
 
-def handle_webhook_event(db: Session, payload: Dict[str, Any], signature: str) -> str:
+def handle_webhook_event(db: Session, payload: bytes, signature: str) -> str:
     """
     Verify and process a Stripe webhook event.
 
     Args:

[0m
Now let me also fix the docstring to reflect bytes:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -218,9 +218,9 @@
 Verify and process a Stripe webhook event.
 
 Args:
     db: SQLAlchemy database session
-    payload: Raw webhook payload (bytes decoded to dict)
+    payload: Raw webhook payload (bytes)
     signature: Stripe-Signature header value
 
 Returns:
     Event ID that was processed

[0m
[0m# [0mTodos
[x] Implement SubscriptionUpdater.update_user_tier() to update user subscription in DB
[x] Implement SubscriptionUpdater.downgrade_to_free() to downgrade user to free tier
[x] Modify webhook handlers to accept DB session and pass to SubscriptionUpdater
[x] Update handle_webhook_event signature to accept DB session
[x] Update FastAPI webhook endpoint to pass DB session
[x] Add imports for Session in stripe_billing.py
[ ] Write tests for database update logic
[ ] Verify all billing tests pass
[ ] Update README with billing setup instructions
[0m
Now I need to update the tests to account for the new db parameter. Let me update the test file:
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -279,28 +279,31 @@
         ) as mock_update:
             # Manually set the env var for plan
             os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"
 
-            _handle_subscription_updated(subscription)
+            _handle_subscription_updated(mock_db, subscription)
 
-            # Should call update_user_tier with pro tier
+            # Should call update_user_tier with db, user_id, tier, subscription
             mock_update.assert_called_once()
             call_args = mock_update.call_args
-            assert call_args[0][0] == "user_123"  # user_id
-            assert call_args[0][1] == "pro"  # tier
+            assert call_args[0][0] == mock_db  # db session
+            assert call_args[0][1] == "user_123"  # user_id
+            assert call_args[0][2] == "pro"  # tier
+            assert call_args[0][3] == subscription  # subscription
 
 def test_handle_subscription_deleted(self):
     """Test subscription deletion webhook downgrades to free."""
+    mock_db = MagicMock(spec=Session)
     with patch(
         "src.billing.stripe_billing.SubscriptionUpdater.downgrade_to_free"
     ) as mock_downgrade:
         subscription = {
             "metadata": {"user_id": "user_123"},
         }
 
-        _handle_subscription_deleted(subscription)
+        _handle_subscription_deleted(mock_db, subscription)
 
-        mock_downgrade.assert_called_once_with("user_123")
+        mock_downgrade.assert_called_once_with(mock_db, "user_123")
 
 @patch("src.billing.stripe_billing.stripe")
 def test_handle_webhook_event_success(self, mock_stripe):
     """Test successful webhook event processing."""

[0m
The test file may have import issues. Let me check the imports:
[0m→ [0mRead tests/test_billing.py[90m [limit=35][0m
The imports seem fine. Let me check the test functions that use `handle_webhook_event`:
[0m→ [0mRead tests/test_billing.py[90m [limit=40, offset=305][0m
I see the tests call `handle_webhook_event` without importing it and without passing a db parameter. I need to fix both issues:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -25,8 +25,9 @@
 )
 from src.billing.stripe_billing import (
     _handle_subscription_updated,
     _handle_subscription_deleted,
+    handle_webhook_event,
 )
 from src.billing.schemas import CheckoutSessionResponse, SubscriptionStatus
 
 

[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -307,15 +307,16 @@
 
 @patch("src.billing.stripe_billing.stripe")
 def test_handle_webhook_event_success(self, mock_stripe):
     """Test successful webhook event processing."""
+    mock_db = MagicMock(spec=Session)
     payload = {"type": "customer.subscription.updated", "data": {"object": {}}}
     signature = "valid_signature"
 
     # Mock Webhook.construct_event
     mock_stripe.Webhook.construct_event.return_value = payload
 
-    event_id = handle_webhook_event(payload, signature)
+    event_id = handle_webhook_event(mock_db, payload, signature)
 
     assert (
         event_id is None
     )  # payload has no id, returns None (that's a bug but payload missing)
@@ -324,9 +325,9 @@
         "id": "evt_123",
         "type": "customer.subscription.updated",
         "data": {"object": {}},
     }
-    event_id = handle_webhook_event(payload_with_id, signature)
+    event_id = handle_webhook_event(mock_db, payload_with_id, signature)
     assert event_id == "evt_123"
 
 def test_handle_webhook_event_invalid_signature(self):
     """Test webhook with invalid signature raises ValueError."""

[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -330,8 +330,9 @@
     assert event_id == "evt_123"
 
 def test_handle_webhook_event_invalid_signature(self):
     """Test webhook with invalid signature raises ValueError."""
+    mock_db = MagicMock(spec=Session)
     payload = {}
     signature = "invalid"
 
     with patch("src.billing.stripe_billing.stripe") as mock_stripe:
@@ -339,5 +340,5 @@
             "Invalid signature"
         )
 
         with pytest.raises(ValueError, match="Webhook verification failed"):
-            handle_webhook_event(payload, signature)
+            handle_webhook_event(mock_db, payload, signature)

[0m
Now I need to fix the payload type in tests (should be bytes). Also, let me check the billing __init__.py to see if `get_plan_by_price_id` and `get_plan_by_tier` are exported:
[0m→ [0mRead src/billing/__init__.py
I see the problem - `get_plan_by_price_id` and `get_plan_by_tier` are not exported from `src/billing/__init__.py`. I need to add them. Also I need to fix the test payloads to be bytes. Let me update:
[0m✗ [0medit failed
[91m[1mError: [0mCould not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
[0m
[0m← [0mEdit src/billing/__init__.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/__init__.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/__init__.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/__init__.py
@@ -4,8 +4,10 @@
 create_checkout_session,
 handle_webhook_event,
 get_subscription_info,
 calculate_invoice_limit,
+get_plan_by_price_id,
+get_plan_by_tier,
 PLANS,
 StripePrice,
 CheckoutSessionRequest,
 CheckoutSessionResponse,
@@ -16,8 +18,10 @@
 "create_checkout_session",
 "handle_webhook_event",
 "get_subscription_info",
 "calculate_invoice_limit",
+"get_plan_by_price_id",
+"get_plan_by_tier",
 "PLANS",
 "StripePrice",
 "CheckoutSessionRequest",
 "CheckoutSessionResponse",

[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -9,8 +9,9 @@
 - Webhook processing
 """
 
 import os
+import json
 from unittest.mock import Mock, patch, MagicMock
 import pytest
 from sqlalchemy.orm import Session
 

[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -309,15 +309,20 @@
 @patch("src.billing.stripe_billing.stripe")
 def test_handle_webhook_event_success(self, mock_stripe):
     """Test successful webhook event processing."""
     mock_db = MagicMock(spec=Session)
-    payload = {"type": "customer.subscription.updated", "data": {"object": {}}}
+    payload_dict = {
+        "type": "customer.subscription.updated",
+        "data": {"object": {}},
+    }
     signature = "valid_signature"
 
-    # Mock Webhook.construct_event
-    mock_stripe.Webhook.construct_event.return_value = payload
+    # Mock Webhook.construct_event to return the parsed event
+    mock_stripe.Webhook.construct_event.return_value = payload_dict
 
-    event_id = handle_webhook_event(mock_db, payload, signature)
+    # Pass payload as bytes (simulating raw request body)
+    payload_bytes = json.dumps(payload_dict).encode()
+    event_id = handle_webhook_event(mock_db, payload_bytes, signature)
 
     assert (
         event_id is None
     )  # payload has no id, returns None (that's a bug but payload missing)
@@ -326,9 +331,10 @@
         "id": "evt_123",
         "type": "customer.subscription.updated",
         "data": {"object": {}},
     }
-    event_id = handle_webhook_event(mock_db, payload_with_id, signature)
+    payload_with_id_bytes = json.dumps(payload_with_id).encode()
+    event_id = handle_webhook_event(mock_db, payload_with_id_bytes, signature)
     assert event_id == "evt_123"
 
 def test_handle_webhook_event_invalid_signature(self):
     """Test webhook with invalid signature raises ValueError."""

[0m
The tests are failing to match exactly. Let me just run the tests to see if the LSP errors are just false positives or actual issues:
[0m$ [0mpython -m pytest tests/test_billing.py -v
ImportError while loading conftest '/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/conftest.py'.
tests/conftest.py:18: in <module>
    from src.main import app as fastapi_app
src/main.py:10: in <module>
    from .api.billing import router as billing_router
src/api/billing.py:15: in <module>
    from src.core.database import get_db
E   ImportError: cannot import name 'get_db' from 'src.core.database' (/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/database.py)
[0m
Ah, I see the problem! The database module exports `get_session` but the code is trying to import `get_db`. Let me add an alias:
[0m← [0mEdit src/core/database.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/database.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/database.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/database.py
@@ -37,8 +37,12 @@
     finally:
         session.close()
 
 
+# Alias for compatibility with code expecting get_db
+get_db = get_session
+
+
 def init_db():
     """Initialize database tables (for development/testing)."""
     from src.models import Base
 

[0m
Now let's run the tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan FAILED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success ERROR [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer ERROR [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan ERROR [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription ERROR [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription ERROR [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id FAILED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error ERROR [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated FAILED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success FAILED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

==================================== ERRORS ====================================
_ ERROR at setup of TestCreateCheckoutSession.test_create_checkout_session_success _

self = <test_billing.TestCreateCheckoutSession object at 0x7f79bc317610>

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
>       user = User(
            id="user_123",
            email="test@example.com",
            full_name="Test User",
            company_name=None,
            subscription_tier="free",
            invoice_limit=5,
            extra_data={},
        )

tests/test_billing.py:98: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bc3c4ad0>
kwargs = {'company_name': None, 'email': 'test@example.com', 'extra_data': {}, 'full_name': 'Test User', ...}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_ ERROR at setup of TestCreateCheckoutSession.test_create_checkout_session_uses_existing_customer _

self = <test_billing.TestCreateCheckoutSession object at 0x7f79bc317750>

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
>       user = User(
            id="user_123",
            email="test@example.com",
            full_name="Test User",
            company_name=None,
            subscription_tier="free",
            invoice_limit=5,
            extra_data={},
        )

tests/test_billing.py:98: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bc3dd590>
kwargs = {'company_name': None, 'email': 'test@example.com', 'extra_data': {}, 'full_name': 'Test User', ...}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_ ERROR at setup of TestCreateCheckoutSession.test_create_checkout_session_invalid_plan _

self = <test_billing.TestCreateCheckoutSession object at 0x7f79bc356780>

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
>       user = User(
            id="user_123",
            email="test@example.com",
            full_name="Test User",
            company_name=None,
            subscription_tier="free",
            invoice_limit=5,
            extra_data={},
        )

tests/test_billing.py:98: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bc3de5d0>
kwargs = {'company_name': None, 'email': 'test@example.com', 'extra_data': {}, 'full_name': 'Test User', ...}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_ ERROR at setup of TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription _

self = <test_billing.TestGetSubscriptionInfo object at 0x7f79bc317890>

    @pytest.fixture
    def mock_user_with_customer(self):
        """Create a mock user with Stripe customer ID."""
>       user = User(
            id="user_123",
            email="test@example.com",
            subscription_tier="pro",
            extra_data={"stripe_customer_id": "cus_123"},
        )

tests/test_billing.py:182: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bbe01e00>
kwargs = {'email': 'test@example.com', 'extra_data': {'stripe_customer_id': 'cus_123'}, 'id': 'user_123', 'subscription_tier': 'pro'}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_ ERROR at setup of TestGetSubscriptionInfo.test_get_subscription_info_no_subscription _

self = <test_billing.TestGetSubscriptionInfo object at 0x7f79bc3179d0>

    @pytest.fixture
    def mock_user_with_customer(self):
        """Create a mock user with Stripe customer ID."""
>       user = User(
            id="user_123",
            email="test@example.com",
            subscription_tier="pro",
            extra_data={"stripe_customer_id": "cus_123"},
        )

tests/test_billing.py:182: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bbe02520>
kwargs = {'email': 'test@example.com', 'extra_data': {'stripe_customer_id': 'cus_123'}, 'id': 'user_123', 'subscription_tier': 'pro'}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_ ERROR at setup of TestGetSubscriptionInfo.test_get_subscription_info_handles_stripe_error _

self = <test_billing.TestGetSubscriptionInfo object at 0x7f79bc3569e0>

    @pytest.fixture
    def mock_user_with_customer(self):
        """Create a mock user with Stripe customer ID."""
>       user = User(
            id="user_123",
            email="test@example.com",
            subscription_tier="pro",
            extra_data={"stripe_customer_id": "cus_123"},
        )

tests/test_billing.py:182: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bc37ae00>
kwargs = {'email': 'test@example.com', 'extra_data': {'stripe_customer_id': 'cus_123'}, 'id': 'user_123', 'subscription_tier': 'pro'}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
=================================== FAILURES ===================================
________ TestPlanLookups.test_get_plan_by_price_id_returns_correct_plan ________

self = <test_billing.TestPlanLookups object at 0x7f79bc316c10>

    def test_get_plan_by_price_id_returns_correct_plan(self):
        """Test retrieving plan by price ID."""
        plan = get_plan_by_price_id("price_pro_123")
>       assert plan is not None
E       assert None is not None

tests/test_billing.py:47: AssertionError
______ TestGetSubscriptionInfo.test_get_subscription_info_no_customer_id _______

self = <test_billing.TestGetSubscriptionInfo object at 0x7f79bc3568b0>

    def test_get_subscription_info_no_customer_id(self):
        """Test returning None when user has no Stripe customer ID."""
>       user = User(
            id="user_123",
            email="test@example.com",
            extra_data={},  # No customer ID
        )

tests/test_billing.py:237: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:4: in __init__
    ???
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:596: in _initialize_instance
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/sqlalchemy/util/langhelpers.py:121: in __exit__
    raise exc_value.with_traceback(exc_tb)
../../venv/lib/python3.14/site-packages/sqlalchemy/orm/state.py:594: in _initialize_instance
    manager.original_init(*mixed[1:], **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.models.User object at 0x7f79bbee44d0>
kwargs = {'email': 'test@example.com', 'extra_data': {}, 'id': 'user_123'}
cls_ = <class 'src.models.User'>, k = 'extra_data'

    def _declarative_constructor(self: Any, **kwargs: Any) -> None:
        """A simple constructor that allows initialization from kwargs.
    
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
    
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
>               raise TypeError(
                    "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
                )
E               TypeError: 'extra_data' is an invalid keyword argument for User

../../venv/lib/python3.14/site-packages/sqlalchemy/orm/decl_base.py:2179: TypeError
_____________ TestWebhookHandling.test_handle_subscription_updated _____________

self = <test_billing.TestWebhookHandling object at 0x7f79bc317b10>
mock_stripe = <MagicMock name='stripe' id='140160825842992'>

    @patch("src.billing.stripe_billing.stripe")
    def test_handle_subscription_updated(self, mock_stripe):
        """Test subscription update webhook updates user tier."""
        # Create a mock DB session
        mock_db = MagicMock(spec=Session)
    
        # Mock subscription payload
        subscription = {
            "id": "sub_123",
            "metadata": {"user_id": "user_123"},
            "items": {"data": [{"price": {"id": "price_pro_123"}}]},
        }
    
        # Mock plan lookup
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock(name="Pro", invoice_limit=-1)
            mock_get_plan.return_value = mock_plan
    
            # We need to mock the SubscriptionUpdater.update_user_tier
            with patch(
                "src.billing.stripe_billing.SubscriptionUpdater.update_user_tier"
            ) as mock_update:
                # Manually set the env var for plan
                os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"
    
                _handle_subscription_updated(mock_db, subscription)
    
                # Should call update_user_tier with db, user_id, tier, subscription
                mock_update.assert_called_once()
                call_args = mock_update.call_args
                assert call_args[0][0] == mock_db  # db session
                assert call_args[0][1] == "user_123"  # user_id
>               assert call_args[0][2] == "pro"  # tier
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               AssertionError: assert <Mock name='Pro.name.lower()' id='140160825847024'> == 'pro'

tests/test_billing.py:292: AssertionError
____________ TestWebhookHandling.test_handle_webhook_event_success _____________

self = <test_billing.TestWebhookHandling object at 0x7f79bc356b10>
mock_stripe = <MagicMock name='stripe' id='140160825849040'>

    @patch("src.billing.stripe_billing.stripe")
    def test_handle_webhook_event_success(self, mock_stripe):
        """Test successful webhook event processing."""
        mock_db = MagicMock(spec=Session)
        payload_dict = {
            "type": "customer.subscription.updated",
            "data": {"object": {}},
        }
        signature = "valid_signature"
    
        # Mock Webhook.construct_event to return the parsed event
        mock_stripe.Webhook.construct_event.return_value = payload_dict
    
        # Pass payload as bytes (simulating raw request body)
        payload_bytes = json.dumps(payload_dict).encode()
>       event_id = handle_webhook_event(mock_db, payload_bytes, signature)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_billing.py:324: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

db = <MagicMock spec='Session' id='140160825849376'>
payload = b'{"type": "customer.subscription.updated", "data": {"object": {}}}'
signature = 'valid_signature'

    def handle_webhook_event(db: Session, payload: bytes, signature: str) -> str:
        """
        Verify and process a Stripe webhook event.
    
        Args:
            db: SQLAlchemy database session
            payload: Raw webhook payload (bytes)
            signature: Stripe-Signature header value
    
        Returns:
            Event ID that was processed
    
        Raises:
            ValueError: If signature verification fails or event processing fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.stripe_webhook_secret
            )
        except Exception as e:
            # Handle signature verification errors and other construct issues
            raise ValueError(f"Webhook verification failed: {e}") from e
    
        event_id = event.get("id")
        if not event_id:
>           raise ValueError("Event ID missing from webhook payload")
E           ValueError: Event ID missing from webhook payload

src/billing/stripe_billing.py:241: ValueError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success
ERROR tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success
ERROR tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer
ERROR tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan
ERROR tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
ERROR tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription
ERROR tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error
============== 4 failed, 9 passed, 10 warnings, 6 errors in 0.88s ==============
[0m
There are several issues to fix:

1. **User model missing `extra_data` column** - tests and code use `user.extra_data` but it's not in the model
2. **Env vars set after module import** - PLANS loads before env vars are set in tests
3. **Case-sensitivity bug** in tier determination
4. **Test expectations need updating** for the new behavior

Let me fix the User model first by adding `extra_data` column:
[0m← [0mEdit src/models.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py
@@ -71,8 +71,9 @@
 email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
 is_active: Mapped[bool] = mapped_column(Boolean, default=True)
 is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
 last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
+extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
 
 # Relationships
 payment_connections: Mapped[List["PaymentConnection"]] = relationship(
     "PaymentConnection", back_populates="user", cascade="all, delete-orphan"

[0m
Now fix the case-sensitivity issue in tier determination:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -292,9 +292,9 @@
 # In a real implementation, you'd handle add-ons differently (separate subscription items)
 
 tier = (
     "pro"
-    if plan.name in ["pro", "legal_pack", "multi_currency"]
+    if plan.name.lower() in ["pro", "legal_pack", "multi_currency"]
     else plan.name.lower()
 )
 
 # Update user in database

[0m
Now let me fix the test file to set env vars before imports and adjust the webhook test:
[0m→ [0mRead tests/test_billing.py[90m [limit=40][0m
I'll move the environment setup to before the imports:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -14,8 +14,13 @@
 from unittest.mock import Mock, patch, MagicMock
 import pytest
 from sqlalchemy.orm import Session
 
+# Mock Stripe settings for testing - MUST be set BEFORE importing billing module
+os.environ["STRIPE_API_KEY"] = "sk_test_123"
+os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"
+os.environ["STRIPE_PRICE_FREE"] = "price_free_123"
+
 from src.models import User
 from src.billing import (
     create_checkout_session,
     get_subscription_info,
@@ -31,14 +36,8 @@
 )
 from src.billing.schemas import CheckoutSessionResponse, SubscriptionStatus
 
 
-# Mock Stripe settings for testing
-os.environ["STRIPE_API_KEY"] = "sk_test_123"
-os.environ["STRIPE_PRICE_PRO"] = "price_pro_123"
-os.environ["STRIPE_PRICE_FREE"] = "price_free_123"
-
-
 class TestPlanLookups:
     """Test plan lookup functions."""
 
     def test_get_plan_by_price_id_returns_correct_plan(self):

[0m
Let me check the test around line 350 to see where payload (dict) is still being used:
[0m→ [0mRead tests/test_billing.py[90m [limit=40, offset=330][0m
Found it! Line 350 passes `payload` (dict) instead of bytes. Let me fix:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -337,14 +337,15 @@
 
 def test_handle_webhook_event_invalid_signature(self):
     """Test webhook with invalid signature raises ValueError."""
     mock_db = MagicMock(spec=Session)
-    payload = {}
+    payload_dict = {}
     signature = "invalid"
 
     with patch("src.billing.stripe_billing.stripe") as mock_stripe:
         mock_stripe.Webhook.construct_event.side_effect = Exception(
             "Invalid signature"
         )
 
+        payload_bytes = json.dumps(payload_dict).encode()
         with pytest.raises(ValueError, match="Webhook verification failed"):
-            handle_webhook_event(mock_db, payload, signature)
+            handle_webhook_event(mock_db, payload_bytes, signature)

[0m
Now run the tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan FAILED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success FAILED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer FAILED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated FAILED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success FAILED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
________ TestPlanLookups.test_get_plan_by_price_id_returns_correct_plan ________
tests/test_billing.py:46: in test_get_plan_by_price_id_returns_correct_plan
    assert plan is not None
E   assert None is not None
________ TestCreateCheckoutSession.test_create_checkout_session_success ________
tests/test_billing.py:120: in test_create_checkout_session_success
    response = create_checkout_session(
src/billing/stripe_billing.py:133: in create_checkout_session
    raise ValueError(f"Invalid plan ID: {plan_id}")
E   ValueError: Invalid plan ID: price_pro_123
_ TestCreateCheckoutSession.test_create_checkout_session_uses_existing_customer _
tests/test_billing.py:157: in test_create_checkout_session_uses_existing_customer
    response = create_checkout_session(
src/billing/stripe_billing.py:133: in create_checkout_session
    raise ValueError(f"Invalid plan ID: {plan_id}")
E   ValueError: Invalid plan ID: price_pro_123
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __
tests/test_billing.py:217: in test_get_subscription_info_with_active_subscription
    assert subscription is not None
E   assert None is not None
_____________ TestWebhookHandling.test_handle_subscription_updated _____________
tests/test_billing.py:291: in test_handle_subscription_updated
    assert call_args[0][2] == "pro"  # tier
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: assert <Mock name='Pro.name.lower()' id='140328584697504'> == 'pro'
____________ TestWebhookHandling.test_handle_webhook_event_success _____________
tests/test_billing.py:323: in test_handle_webhook_event_success
    event_id = handle_webhook_event(mock_db, payload_bytes, signature)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/billing/stripe_billing.py:241: in handle_webhook_event
    raise ValueError("Event ID missing from webhook payload")
E   ValueError: Event ID missing from webhook payload
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan
FAILED tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success
FAILED tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success
================== 6 failed, 13 passed, 10 warnings in 0.28s ===================
[0m
The issue is that conftest imports `src.main` before the test file sets env vars. I'll set the env vars in conftest.py early:
[0m→ [0mRead tests/conftest.py[90m [limit=30][0m
I'll add env var settings before the import of src.main:
[0m
[0m← [0mEdit tests/conftest.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/conftest.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/conftest.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/conftest.py
@@ -12,8 +12,14 @@
 from sqlalchemy import create_engine
 from sqlalchemy.orm import sessionmaker, Session
 from sqlalchemy.pool import StaticPool
 
+# Set test environment variables BEFORE importing app
+# These are needed because billing module loads PLANS at import time
+os.environ.setdefault("STRIPE_API_KEY", "sk_test_123")
+os.environ.setdefault("STRIPE_PRICE_PRO", "price_pro_123")
+os.environ.setdefault("STRIPE_PRICE_FREE", "price_free_123")
+
 from src.core.config import Settings
 from src.models import Base
 from src.main import app as fastapi_app
 

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated FAILED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success FAILED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __
tests/test_billing.py:217: in test_get_subscription_info_with_active_subscription
    assert subscription is not None
E   assert None is not None
_____________ TestWebhookHandling.test_handle_subscription_updated _____________
tests/test_billing.py:291: in test_handle_subscription_updated
    assert call_args[0][2] == "pro"  # tier
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: assert <Mock name='Pro.name.lower()' id='139665703146160'> == 'pro'
____________ TestWebhookHandling.test_handle_webhook_event_success _____________
tests/test_billing.py:323: in test_handle_webhook_event_success
    event_id = handle_webhook_event(mock_db, payload_bytes, signature)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/billing/stripe_billing.py:241: in handle_webhook_event
    raise ValueError("Event ID missing from webhook payload")
E   ValueError: Event ID missing from webhook payload
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated
FAILED tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success
================== 3 failed, 16 passed, 10 warnings in 0.31s ===================
[0m
[0m→ [0mRead tests/test_billing.py[90m [limit=40, offset=174][0m
Good progress! Now fix the remaining 3 test failures:
Let me fix this test by using dict for subscription and properly setting plan attributes:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -190,27 +190,23 @@
 def test_get_subscription_info_with_active_subscription(
     self, mock_stripe, mock_user_with_customer
 ):
     """Test retrieving subscription info when user has active subscription."""
-    # Mock subscription with items
-    mock_subscription = Mock(
-        id="sub_123",
-        status="active",
-        current_period_end=1700000000,  # Unix timestamp
-        cancel_at_period_end=False,
-        items=Mock(data=[Mock(price=Mock(id="price_pro_123"))]),
-    )
+    # Mock subscription with items as dict (Stripe objects are dict-like)
+    mock_subscription = {
+        "id": "sub_123",
+        "status": "active",
+        "current_period_end": 1700000000,  # Unix timestamp
+        "cancel_at_period_end": False,
+        "items": {"data": [{"price": {"id": "price_pro_123"}}]},
+    }
     mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
 
     # Mock plan lookup by patching get_plan_by_price_id
     with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
-        mock_plan = Mock(
-            name="Pro",
-            price_monthly=1900,
-            invoice_limit=-1,
-            includes_legal_pack=False,
-            includes_multi_currency=False,
-        )
+        mock_plan = Mock()
+        mock_plan.name = "Pro"
+        mock_plan.invoice_limit = -1
         mock_get_plan.return_value = mock_plan
 
         subscription = get_subscription_info(mock_user_with_customer)
 

[0m
[0m→ [0mRead tests/test_billing.py[90m [limit=30, offset=258][0m
Now fix the `test_handle_subscription_updated` mock_plan:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -266,9 +266,11 @@
 }
 
 # Mock plan lookup
 with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
-    mock_plan = Mock(name="Pro", invoice_limit=-1)
+    mock_plan = Mock()
+    mock_plan.name = "Pro"
+    mock_plan.invoice_limit = -1
     mock_get_plan.return_value = mock_plan
 
     # We need to mock the SubscriptionUpdater.update_user_tier
     with patch(

[0m
Now fix the `test_handle_webhook_event_success` test to expect ValueError when event ID is missing:
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -306,32 +306,20 @@
 @patch("src.billing.stripe_billing.stripe")
 def test_handle_webhook_event_success(self, mock_stripe):
     """Test successful webhook event processing."""
     mock_db = MagicMock(spec=Session)
-    payload_dict = {
-        "type": "customer.subscription.updated",
-        "data": {"object": {}},
-    }
     signature = "valid_signature"
 
-    # Mock Webhook.construct_event to return the parsed event
-    mock_stripe.Webhook.construct_event.return_value = payload_dict
-
-    # Pass payload as bytes (simulating raw request body)
-    payload_bytes = json.dumps(payload_dict).encode()
-    event_id = handle_webhook_event(mock_db, payload_bytes, signature)
-
-    assert (
-        event_id is None
-    )  # payload has no id, returns None (that's a bug but payload missing)
-    # Actually our function now raises if no id, so adjust test to include id
+    # Mock Webhook.construct_event to return a valid event with ID
     payload_with_id = {
         "id": "evt_123",
         "type": "customer.subscription.updated",
         "data": {"object": {}},
     }
-    payload_with_id_bytes = json.dumps(payload_with_id).encode()
-    event_id = handle_webhook_event(mock_db, payload_with_id_bytes, signature)
+    mock_stripe.Webhook.construct_event.return_value = payload_with_id
+
+    payload_bytes = json.dumps(payload_with_id).encode()
+    event_id = handle_webhook_event(mock_db, payload_bytes, signature)
     assert event_id == "evt_123"
 
 def test_handle_webhook_event_invalid_signature(self):
     """Test webhook with invalid signature raises ValueError."""

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated PASSED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success PASSED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __

self = <test_billing.TestGetSubscriptionInfo object at 0x7f78fc1fb9d0>
mock_stripe = <MagicMock name='stripe' id='140157598193648'>
mock_user_with_customer = <src.models.User object at 0x7f78fb954d60>

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_with_active_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test retrieving subscription info when user has active subscription."""
        # Mock subscription with items as dict (Stripe objects are dict-like)
        mock_subscription = {
            "id": "sub_123",
            "status": "active",
            "current_period_end": 1700000000,  # Unix timestamp
            "cancel_at_period_end": False,
            "items": {"data": [{"price": {"id": "price_pro_123"}}]},
        }
        mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
    
        # Mock plan lookup by patching get_plan_by_price_id
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock()
            mock_plan.name = "Pro"
            mock_plan.invoice_limit = -1
            mock_get_plan.return_value = mock_plan
    
            subscription = get_subscription_info(mock_user_with_customer)
    
>       assert subscription is not None
E       assert None is not None

tests/test_billing.py:213: AssertionError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
================== 1 failed, 18 passed, 10 warnings in 0.28s ===================
[0m
[0m→ [0mRead src/billing/stripe_billing.py[90m [limit=50, offset=373][0m
Let me check the `get_subscription_info` function to see why it returns None:
[0m→ [0mRead src/billing/stripe_billing.py[90m [limit=30, offset=423][0m
I see the issue: `get_subscription_info` uses attribute access (`subscription.current_period_end`, `subscription.id`, etc.) but we provided a dict. We need to use a Mock with attributes. Let me fix the test:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -190,16 +190,16 @@
 def test_get_subscription_info_with_active_subscription(
     self, mock_stripe, mock_user_with_customer
 ):
     """Test retrieving subscription info when user has active subscription."""
-    # Mock subscription with items as dict (Stripe objects are dict-like)
-    mock_subscription = {
-        "id": "sub_123",
-        "status": "active",
-        "current_period_end": 1700000000,  # Unix timestamp
-        "cancel_at_period_end": False,
-        "items": {"data": [{"price": {"id": "price_pro_123"}}]},
-    }
+    # Mock subscription as object with attributes (Stripe objects have attributes)
+    mock_subscription = Mock()
+    mock_subscription.id = "sub_123"
+    mock_subscription.status = "active"
+    mock_subscription.current_period_end = 1700000000  # Unix timestamp
+    mock_subscription.cancel_at_period_end = False
+    mock_subscription.items = {"data": [{"price": {"id": "price_pro_123"}}]}
+
     mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
 
     # Mock plan lookup by patching get_plan_by_price_id
     with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated PASSED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success PASSED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __

self = <test_billing.TestGetSubscriptionInfo object at 0x7f755790bb10>
mock_stripe = <MagicMock name='stripe' id='140141957699568'>
mock_user_with_customer = <src.models.User object at 0x7f7557594d60>

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_with_active_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test retrieving subscription info when user has active subscription."""
        # Mock subscription as object with attributes (Stripe objects have attributes)
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1700000000  # Unix timestamp
        mock_subscription.cancel_at_period_end = False
        mock_subscription.items = {"data": [{"price": {"id": "price_pro_123"}}]}
    
        mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
    
        # Mock plan lookup by patching get_plan_by_price_id
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock()
            mock_plan.name = "Pro"
            mock_plan.invoice_limit = -1
            mock_get_plan.return_value = mock_plan
    
            subscription = get_subscription_info(mock_user_with_customer)
    
>       assert subscription is not None
E       assert None is not None

tests/test_billing.py:213: AssertionError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
================== 1 failed, 18 passed, 10 warnings in 0.27s ===================
[0m
I see the problem: The test now uses a Mock with attributes, but the code uses `subscription.get("items")`. Mock objects don't have a `.get` that returns the attribute; they return Mocks. I need to change the code to use attribute access for items as well. Let me update `get_subscription_info` to use attribute-based access, which is correct for Stripe objects:
[0m← [0mEdit src/billing/stripe_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/billing/stripe_billing.py
@@ -431,16 +431,21 @@
     return None
 
 subscription = subscriptions.data[0]
 
-# Get the price
-items = subscription.get("items", {}).get("data", [])
-if not items:
+# Get the price - use attribute access for Stripe objects
+# subscription.items is a ListObject with .data attribute containing list
+items_data = getattr(subscription.items, "data", subscription.items)
+if not items_data:
     return None
 
-price = items[0].get("price", {})
-plan = get_plan_by_price_id(price.get("id"))
+# First item's price
+price = items_data[0].price
+plan = get_plan_by_price_id(price.id)
 
+if not plan:
+    return None
+
 # Stripe returns current_period_end as a Unix timestamp (int)
 current_period_end = datetime.fromtimestamp(subscription.current_period_end)  # type: ignore
 
 return SubscriptionStatus(

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated PASSED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success PASSED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __

self = <test_billing.TestGetSubscriptionInfo object at 0x7f53d3313b10>
mock_stripe = <MagicMock name='stripe' id='139998002916256'>
mock_user_with_customer = <src.models.User object at 0x7f53d2f51220>

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_with_active_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test retrieving subscription info when user has active subscription."""
        # Mock subscription as object with attributes (Stripe objects have attributes)
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1700000000  # Unix timestamp
        mock_subscription.cancel_at_period_end = False
        mock_subscription.items = {"data": [{"price": {"id": "price_pro_123"}}]}
    
        mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
    
        # Mock plan lookup by patching get_plan_by_price_id
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock()
            mock_plan.name = "Pro"
            mock_plan.invoice_limit = -1
            mock_get_plan.return_value = mock_plan
    
            subscription = get_subscription_info(mock_user_with_customer)
    
>       assert subscription is not None
E       assert None is not None

tests/test_billing.py:213: AssertionError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
================== 1 failed, 18 passed, 10 warnings in 0.24s ===================
[0m
The test mock_subscription.items is a dict `{"data": [...]}` but the code now expects `subscription.items.data`. I need to adjust the test to use a Mock object with a `.data` attribute. Let me fix the test:
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -196,10 +196,16 @@
 mock_subscription.id = "sub_123"
 mock_subscription.status = "active"
 mock_subscription.current_period_end = 1700000000  # Unix timestamp
 mock_subscription.cancel_at_period_end = False
-mock_subscription.items = {"data": [{"price": {"id": "price_pro_123"}}]}
 
+# Mock items as a ListObject with .data containing price objects
+mock_price = Mock()
+mock_price.id = "price_pro_123"
+mock_items = Mock()
+mock_items.data = [mock_price]
+mock_subscription.items = mock_items
+
 mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
 
 # Mock plan lookup by patching get_plan_by_price_id
 with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated PASSED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success PASSED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __

self = <test_billing.TestGetSubscriptionInfo object at 0x7f50a230f9d0>
mock_stripe = <MagicMock name='stripe' id='139984295926080'>
mock_user_with_customer = <src.models.User object at 0x7f50a1f70e90>

    @patch("src.billing.stripe_billing.stripe")
    def test_get_subscription_info_with_active_subscription(
        self, mock_stripe, mock_user_with_customer
    ):
        """Test retrieving subscription info when user has active subscription."""
        # Mock subscription as object with attributes (Stripe objects have attributes)
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1700000000  # Unix timestamp
        mock_subscription.cancel_at_period_end = False
    
        # Mock items as a ListObject with .data containing price objects
        mock_price = Mock()
        mock_price.id = "price_pro_123"
        mock_items = Mock()
        mock_items.data = [mock_price]
        mock_subscription.items = mock_items
    
        mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
    
        # Mock plan lookup by patching get_plan_by_price_id
        with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
            mock_plan = Mock()
            mock_plan.name = "Pro"
            mock_plan.invoice_limit = -1
            mock_get_plan.return_value = mock_plan
    
            subscription = get_subscription_info(mock_user_with_customer)
    
>       assert subscription is not None
E       assert None is not None

tests/test_billing.py:219: AssertionError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
================== 1 failed, 18 passed, 10 warnings in 0.25s ===================
[0m
Found it! The code expects `items_data[0].price.id`, but the test set `items_data[0].id` directly. We need a nested price object. Let me fix:
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -197,13 +197,15 @@
 mock_subscription.status = "active"
 mock_subscription.current_period_end = 1700000000  # Unix timestamp
 mock_subscription.cancel_at_period_end = False
 
-# Mock items as a ListObject with .data containing price objects
+# Mock items as a ListObject with .data containing items that have .price.id
 mock_price = Mock()
 mock_price.id = "price_pro_123"
+mock_item = Mock()
+mock_item.price = mock_price
 mock_items = Mock()
-mock_items.data = [mock_price]
+mock_items.data = [mock_item]
 mock_subscription.items = mock_items
 
 mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
 

[0m
Run tests again:
[0m$ [0mpython -m pytest tests/test_billing.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_correct_plan PASSED [  5%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_price_id_returns_none_for_unknown PASSED [ 10%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_correct_plan PASSED [ 15%]
tests/test_billing.py::TestPlanLookups::test_get_plan_by_tier_returns_none_for_unknown PASSED [ 21%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_free_tier_limit PASSED [ 26%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_pro_tier_limit_unlimited PASSED [ 31%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_legal_pack_tier_limit_zero PASSED [ 36%]
tests/test_billing.py::TestCalculateInvoiceLimit::test_unknown_tier_returns_default PASSED [ 42%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_success PASSED [ 47%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_uses_existing_customer PASSED [ 52%]
tests/test_billing.py::TestCreateCheckoutSession::test_create_checkout_session_invalid_plan PASSED [ 57%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription FAILED [ 63%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_subscription PASSED [ 68%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_no_customer_id PASSED [ 73%]
tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_handles_stripe_error PASSED [ 78%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_updated PASSED [ 84%]
tests/test_billing.py::TestWebhookHandling::test_handle_subscription_deleted PASSED [ 89%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_success PASSED [ 94%]
tests/test_billing.py::TestWebhookHandling::test_handle_webhook_event_invalid_signature PASSED [100%]

=================================== FAILURES ===================================
_ TestGetSubscriptionInfo.test_get_subscription_info_with_active_subscription __
tests/test_billing.py:221: in test_get_subscription_info_with_active_subscription
    assert subscription is not None
E   assert None is not None
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:56
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:56: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

src/api/ab_testing.py:65
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py:65: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class ExperimentResponse(BaseModel):

src/admin/schemas.py:11
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:11: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserSummary(BaseModel):

src/admin/schemas.py:25
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:25: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserDetail(UserSummary):

src/admin/schemas.py:72
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:72: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class PaymentConnectionInfo(BaseModel):

src/admin/schemas.py:86
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/schemas.py:86: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class WebhookEventInfo(BaseModel):

src/admin/routes.py:130
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py:130: FastAPIDeprecationWarning: `regex` has been deprecated, please use `pattern` instead
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_billing.py::TestGetSubscriptionInfo::test_get_subscription_info_with_active_subscription
================== 1 failed, 18 passed, 10 warnings in 0.27s ===================
[0m
Let me read the current implementation of `get_subscription_info` to ensure it's correct:
[0m→ [0mRead src/billing/stripe_billing.py[90m [limit=50, offset=404][0m
Let's simplify the test by removing the patch for `get_plan_by_price_id` and relying on the real PLANS (which should be configured via conftest). This might fix the issue:
[0m
[0m← [0mEdit tests/test_billing.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_billing.py
@@ -208,17 +208,11 @@
 mock_subscription.items = mock_items
 
 mock_stripe.Subscription.list.return_value = Mock(data=[mock_subscription])
 
-# Mock plan lookup by patching get_plan_by_price_id
-with patch("src.billing.stripe_billing.get_plan_by_price_id") as mock_get_plan:
-    mock_plan = Mock()
-    mock_plan.name = "Pro"
-    mock_plan.invoice_limit = -1
-    mock_get_plan.return_value = mock_plan
+# Use real get_plan_by_price_id (PLANS should be configured via conftest env vars)
+subscription = get_subscription_info(mock_user_with_customer)
 
-    subscription = get_subscription_info(mock_user_with_customer)
-
 assert subscription is not None
 assert subscription.stripe_subscription_id == "sub_123"
 assert subscription.status == "active"
 assert subscription.tier == "pro"

[0m
Run tests again:
