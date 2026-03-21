# Iteration 3 - invoice-resolver-ai

**Timestamp:** Fri Mar 20 10:02:02 PM EDT 2026
**Task:** **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.

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
- Iteration: 3 / 64k Token Budget
- Attempt: 2 (previous attempts may have partial progress)
- **Mandate:** Operate efficiently. Use partial edits, not full file rewrites when possible.
- **Output:** Be concise and action-oriented.


## CURRENT PROJECT STATE (Iteration 3)

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
- [ ] **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.
  - *Deliverable:* Project scaffold with `main.py`, `core/config.py`, `core/logger.py`, `requirements.txt` or `pyproject.toml` including: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv.
- [ ] **Task 1.3:** Setup PostgreSQL database locally (docker-compose.yml) and implement SQLAlchemy models with Alembic migrations for the schema.
  - *Deliverable:* `docker-compose.yml` with PostgreSQL service, `models.py` with all SQLAlchemy models, Alembic setup with initial migration.
- [ ] **Task 1.4:** Create comprehensive API documentation outline and define OpenAPI specs for all endpoints to be built (authentication, invoice CRUD, webhook receivers, admin endpoints).
  - *Deliverable:* `docs/api.md` with endpoint list, request/response schemas, authentication flow (JWT), and webhook payload examples for Stripe/PayPal.

## Phase 2: Core Backend & Data Model
- [ ] **Task 2.1:** Implement FastAPI user authentication system with JWT tokens, password hashing (bcrypt), and subscription tier enforcement middleware (check invoice limits for freemium users).
  - *Deliverable:* `api/auth.py` with /register, /login, /refresh endpoints, `middleware.py` with SubscriptionLimitChecker, and protected route decorator.
- [ ] **Task 2.2:** Build invoice management endpoints: create invoice (manual import), list invoices with filters (status, due_date range), update status (mark as paid/disputed), and soft delete. Integrate with database models.
  - *Deliverable:* `api/invoices.py` with CRUD operations, Pydantic schemas for InvoiceCreate/Update/Response, and integration tests using pytest.
- [ ] **Task 2.3:** Implement webhook receivers for Stripe (invoice.payment_failed, charge.dispute.created) and PayPal (PAYMENT.DENIED, DISPUTE.CREATED) to automatically update invoice status in database.
  - *Deliverable:* `api/webhooks.py` with signature verification for Stripe (webhook secret) and PayPal (transmission ID + secret), endpoint at /webhooks/{provider}, event handler functions that update invoice records and trigger Celery tasks.
- [ ] **Task 2.4:** Setup Celery with Redis broker, create worker processes, and implement background task for invoice status synchronization (periodic polling as fallback if webhooks fail).
  - *Deliverable:* `celery_app.py` configured with Redis, `tasks/sync.py` with periodic task (every 15 min) that queries Stripe/PayPal APIs for invoice status updates, and worker startup script.

## Phase 3: Integrations & AI Features
- [ ] **Task 3.1:** Implement payment provider integration layer: Stripe API client (stripe-python) for retrieving invoices, payment intents, and customers; PayPal API client (paypalrestsdk) for txns and disputes; Plaid integration for bank feed linking (link token creation, transactions sync).
  - *Deliverable:* `integrations/stripe_client.py`, `integrations/paypal_client.py`, `integrations/plaid_client.py` with functions: connect_account, get_invoice_status, list_transactions, and error handling.
- [ ] **Task 3.2:** Build email automation system using SendGrid or SMTP (smtplib) with template rendering (Jinja2). Create follow-up sequences: 3-day reminder, 7-day late notice, 14-day final notice before dispute.
  - *Deliverable:* `email/sender.py` with send_followup_email(invoice, template_type), `email/templates/` directory with HTML templates for each follow-up stage, and queue system using Celery for scheduled sends.
- [ ] **Task 3.3:** Integrate AI letter drafting using OpenAI GPT-4 or Anthropic Claude. Create prompts for formal dispute letters that include invoice details, payment evidence (dates, amounts, communication logs), and legal references (small claims requirements).
  - *Deliverable:* `ai/dispute_drafter.py` with function draft_dispute_letter(invoice, evidence_list) that calls OpenAI API with structured prompt, returns LaTeX or HTML letter content, and includes cost tracking.
- [ ] **Task 3.4:** Implement PDF generation for dispute letters and small claims forms using WeasyPrint (HTML->PDF) or ReportLab. Create templates for common small claims forms (pre-filled with user/business info).
  - *Deliverable:* `pdf/generator.py` with generate_pdf(html_content, output_path) using WeasyPrint, `pdf/templates/` directory with base letter template and small claims form template, and storage to S3 or local filesystem.

## Phase 4: Dashboard & Analytics
- [ ] **Task 4.1:** Build Streamlit dashboard for users to view invoice status, payment connections, campaign metrics, and AI letter drafts. Include authentication with JWT and real-time updates via FastAPI endpoints.
  - *Deliverable:* `dashboard/app.py` with pages: Overview (KPIs: overdue count, recovery rate), Invoices (table with filters), Campaigns (A/B test results), Settings (payment connections). Uses streamlit-authenticator for login.
- [ ] **Task 4.2:** Implement A/B testing framework for follow-up templates and timing. Store template variants and send times, track opens (pixel tracking) and payments after send, calculate conversion rates.
  - *Deliverable:* `ab_testing/experiment.py` with ABTest model, assign_variant(user_id, test_name) function, tracking endpoints for email opens (/track/open/<campaign_id>), and analysis query to report winning variants.
- [ ] **Task 4.3:** Create admin panel (FastAPI + simple HTML/JS or separate Streamlit page) for viewing all users, system health (Celery workers, API latency), and managing subscription tiers.
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
**Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.

**Instructions:** Complete this task. Mark [x] in TASKS.md when done. Create, modify, or delete files as needed. Execute commands as needed. Also update README.md to match this project (name, setup instructions, current progress). No permission needed—just act.
```

## OpenCode Output

```
[0m
> build · stepfun/step-3.5-flash:free
[0m
I'll help you complete Task 1.2: Initialize Python/FastAPI project structure. Let me start by checking the current state of the project.
[0m→ [0mRead .agent_role
[0m→ [0mRead TASKS.md
[0m
[0m$ [0mls -la
total 124
drwxr-xr-x  8 julien julien  4096 Mar 20 22:01 .
drwxr-xr-x 30 julien julien  4096 Mar 20 21:57 ..
-rw-r--r--  1 julien julien     8 Mar 20 21:58 .agent_role
drwxr-xr-x  2 julien julien  4096 Mar 20 21:59 docs
-rw-r--r--  1 julien julien  1021 Mar 20 22:01 .env.example
drwxr-xr-x  7 julien julien  4096 Mar 20 21:58 .git
drwxr-xr-x  3 julien julien  4096 Mar 20 21:57 .github
-rw-r--r--  1 julien julien     4 Mar 20 21:57 .gitignore
drwxr-xr-x  2 julien julien  4096 Mar 20 22:02 logs
-rw-r--r--  1 julien julien  9218 Mar 20 21:57 prompt.txt
-rw-r--r--  1 julien julien  9336 Mar 20 22:01 README.md
-rw-r--r--  1 julien julien   216 Mar 20 22:00 requirements.txt
drwxr-xr-x  3 julien julien  4096 Mar 20 22:00 .ruff_cache
-rw-r--r--  1 julien julien 20731 Mar 20 21:58 schema.sql
drwxr-xr-x  3 julien julien  4096 Mar 20 22:01 src
-rw-r--r--  1 julien julien  9440 Mar 20 21:59 TASKS.md
-rw-r--r--  1 julien julien  9440 Mar 20 21:58 TASKS_original.md
-rw-r--r--  1 julien julien     6 Mar 20 21:58 .worker_persistent_mode
[0m
Let me check what's already in the src directory and the existing files:
[0m$ [0mfind src -type f
src/main.py
src/core/config.py
src/core/logger.py
[0m
[0m→ [0mRead requirements.txt
[0m→ [0mRead .env.example
[0m→ [0mRead src/main.py
[0m→ [0mRead src/core/config.py
[0m→ [0mRead src/core/logger.py
Let me check what's already in the existing files:
Let me check the project structure and see if there are any __init__.py files needed:
[0m
[0m$ [0mfind src -name "*.py" -o -name "__init__.py"
src/main.py
src/core/config.py
src/core/logger.py
[0m
[0m→ [0mRead README.md
I can see the project structure is already largely complete. Let me verify if there are missing __init__.py files and test that everything works:
[0m
[0m$ [0mls -la src/ && ls -la src/core/
total 16
drwxr-xr-x 3 julien julien 4096 Mar 20 22:01 .
drwxr-xr-x 8 julien julien 4096 Mar 20 22:01 ..
drwxr-xr-x 2 julien julien 4096 Mar 20 22:01 core
-rw-r--r-- 1 julien julien 1293 Mar 20 22:01 main.py
total 16
drwxr-xr-x 2 julien julien 4096 Mar 20 22:01 .
drwxr-xr-x 3 julien julien 4096 Mar 20 22:01 ..
-rw-r--r-- 1 julien julien 1535 Mar 20 22:00 config.py
-rw-r--r-- 1 julien julien 2043 Mar 20 22:01 logger.py
[0m
[0m$ [0mpython3 -c "import sys; sys.path.insert(0, '.'); from src.main import app; from src.core.config import settings; from src.core.logger import setup_logging; print('All imports successful')"
2026-03-20 22:02:37 - src.core.logger - INFO - Logging configured: level=INFO, file=None
All imports successful
[0m
Perfect! The imports work successfully. Now I need to add missing __init__.py files to make it a proper Python package structure and mark the task as complete. Let me create the __init__.py files:
[0m← [0mWrite src/core/__init__.py
Wrote file successfully.
[0m
[0m← [0mWrite src/__init__.py
Wrote file successfully.
[0m
Now I'll mark Task 1.2 as complete in TASKS.md:
[0m← [0mEdit TASKS.md
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/TASKS.md
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/TASKS.md
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/TASKS.md
@@ -17,9 +17,9 @@
 
 ## Phase 1: Planning & Setup
 - [x] **Task 1.1:** Design complete database schema (PostgreSQL) for users, invoices, templates, campaigns, payment connections, and A/B test results. Create ER diagram and write migration SQL.
   - *Deliverable:* `schema.sql` with tables: users (subscription_tier, invoice_limit), invoices (status, due_date, amount, stripe_payment_intent_id, paypal_txn_id, plaid_account_id), payment_connections (provider, credentials_encrypted, user_id), templates (type, content, variables), campaigns (template_id, sent_at, opened_at, paid_after), ab_tests (variant, metric, result).
-- [ ] **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.
+- [x] **Task 1.2:** Initialize Python/FastAPI project structure with Poetry/pip, setup logging configuration, environment variable management (python-dotenv), and core settings module.
   - *Deliverable:* Project scaffold with `main.py`, `core/config.py`, `core/logger.py`, `requirements.txt` or `pyproject.toml` including: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv.
 - [ ] **Task 1.3:** Setup PostgreSQL database locally (docker-compose.yml) and implement SQLAlchemy models with Alembic migrations for the schema.
   - *Deliverable:* `docker-compose.yml` with PostgreSQL service, `models.py` with all SQLAlchemy models, Alembic setup with initial migration.
 - [ ] **Task 1.4:** Create comprehensive API documentation outline and define OpenAPI specs for all endpoints to be built (authentication, invoice CRUD, webhook receivers, admin endpoints).

[0m
Let me check if the GitHub Actions workflow exists and create it if needed (Task 0):
[0m$ [0mls -la .github/workflows/
total 40
drwxr-xr-x 2 julien julien 4096 Mar 20 21:57 .
drwxr-xr-x 3 julien julien 4096 Mar 20 21:57 ..
-rw-r--r-- 1 julien julien 6143 Mar 20 21:57 deploy-production.yml
-rw-r--r-- 1 julien julien 4295 Mar 20 21:57 deploy-staging.yml
-rw-r--r-- 1 julien julien 3218 Mar 20 21:57 report-ci-errors.yml
-rw-r--r-- 1 julien julien 3227 Mar 20 21:57 test.yml
-rw-r--r-- 1 julien julien 6783 Mar 20 21:57 wiggum-system-check.yml
[0m
Good! The test.yml workflow already exists, so Task 0 is already done. Now let me commit the changes for Task 1.2. First, let me see what changes we have:
[0m$ [0mgit status
On branch wiggum/session-1774058292
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   README.md
	modified:   TASKS.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.agent_role
	.env.example
	.worker_persistent_mode
	TASKS_original.md
	docs/
	logs/
	requirements.txt
	schema.sql
	src/

no changes added to commit (use "git add" and/or "git commit -a")
[0m
Let me check what changed in README.md:
[0m$ [0mgit diff README.md
diff --git a/README.md b/README.md
index a6529f7..8abdabd 100644
--- a/README.md
+++ b/README.md
@@ -1,29 +1,259 @@
-# Project Template
+# Invoice Resolver AI
 
-This is a template for new projects created via `wiggum_master.sh create`.
+**An autonomous AI agent for resolving invoice disputes and recovering unpaid invoices.**
 
-Each project:
-- Lives in `projects/<project-name>/`
-- Has its own GitHub repository
-- Runs its own autonomous OpenCode agent loop
-- Tracks progress in TASKS.md
+---
 
-## Setup
+## Problem
 
-1. Create: `bash wiggum_master.sh create "my-project" "Description"`
-2. View: `cat projects/my-project/README.md`
-3. Initialize: `cd projects/my-project && opencode /init --yes`
-4. Run: `cd projects/my-project && bash wiggum.sh`
+Freelancers and small SaaS founders waste hours chasing unpaid invoices, drafting dispute letters, and navigating payment platforms. Payment delays and chargebacks are common, but resolution is manual and frustrating.
 
-## Files
+## Solution
 
-- **README.md** - Project documentation
-- **TASKS.md** - Development task list
-- **prompt.txt** - Agent instructions (project-specific)
-- **AGENTS.md** - Project context (auto-generated)
-- **src/** - Source code directory
-- **tests/** - Test files
+An intelligent AI agent that monitors Stripe/PayPal/Bank feeds, detects overdue or disputed invoices, and automatically:
 
-## Customization
+- Sends polite follow-ups with payment links
+- Drafts formal dispute letters (with evidence attachments) for chargebacks
+- Escalates to small claims paperwork if needed (pre-filled forms)
+- Learns which templates and timing work best (A/B testing)
 
-Update TASKS.md with your project goals, then let the agent handle it!
+## Features
+
+- **Multi-provider Integration**: Stripe, PayPal, and Plaid (bank feeds)
+- **AI-Powered Dispute Drafting**: GPT-4/Claude integration for legal letters
+- **Automated Email Campaigns**: Follow-up sequences (3, 7, 14 days)
+- **PDF Generation**: Dispute letters and small claims forms
+- **A/B Testing**: Optimize templates and timing
+- **Analytics Dashboard**: Recovery rates, campaign performance
+- **Admin Panel**: User management, system health monitoring
+- **Freemium Model**: 5 free invoices/month, $19/mo unlimited
+
+## Tech Stack
+
+- **Backend**: Python 3.11+, FastAPI, PostgreSQL
+- **Task Queue**: Celery + Redis
+- **AI Integration**: OpenAI GPT-4 / Anthropic Claude
+- **Payment APIs**: Stripe, PayPal REST SDK, Plaid
+- **Email**: SendGrid / SMTP with Jinja2 templates
+- **Dashboard**: Streamlit
+- **PDF**: WeasyPrint or ReportLab
+- **Deployment**: Docker, GitHub Actions CI/CD
+
+## Project Structure
+
+```
+.
+├── README.md              # Project documentation
+├── TASKS.md               # Development task list (track progress)
+├── schema.sql             # PostgreSQL database schema
+├── docs/
+│   └── database-er-diagram.md  # ER diagram and table docs
+├── .github/
+│   └── workflows/
+│       └── test.yml       # CI pipeline (to be created)
+├── src/                   # Source code (to be created)
+│   ├── api/              # FastAPI endpoints
+│   ├── core/             # Configuration, logging
+│   ├── models/           # SQLAlchemy models
+│   ├── integrations/     # Stripe/PayPal/Plaid clients
+│   ├── email/            # Email automation
+│   ├── ai/               # AI dispute drafter
+│   ├── pdf/              # PDF generator
+│   ├── dashboard/        # Streamlit app
+│   ├── ab_testing/       # A/B testing framework
+│   ├── admin/            # Admin panel
+│   ├── billing/          # Stripe billing
+│   ├── tasks/            # Celery tasks
+│   └── utils/            # Helper functions
+├── tests/                 # Test suite (pytest)
+├── docker-compose.yml     # Local development (PostgreSQL, Redis)
+├── Dockerfile             # API container
+├── Dockerfile.celery      # Celery worker container
+├── pyproject.toml         # Dependencies (Poetry) or requirements.txt
+└── .env.example           # Environment variables template
+```
+
+## Current Progress
+
+### Phase 1: Planning & Setup
+
+- [x] **Task 1.1**: Database schema design
+  - 11 core tables with relationships
+  - Comprehensive indexes for performance
+  - Row Level Security (RLS) policies
+  - Database functions and views
+  - Full ER diagram with table documentation
+- [x] **Task 1.2**: FastAPI project structure initialization
+  - Core configuration module (`src/core/config.py`) with environment-based settings
+  - Logging setup (`src/core/logger.py`) with console and file handlers
+  - Main FastAPI application (`src/main.py`) with health check and CORS
+  - Dependencies in `requirements.txt`: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, python-dotenv, bcrypt, python-jose, passlib
+  - Environment variable template (`.env.example`)
+- [ ] Task 1.3: PostgreSQL setup with SQLAlchemy + Alembic
+- [ ] Task 1.4: API documentation outline
+
+### Completed Deliverables
+
+1. **`schema.sql`**: Complete PostgreSQL migration script with:
+   - Users, invoices, payment connections, templates
+   - Campaigns, A/B tests, email events, webhooks
+   - Audit logs, refresh tokens, system metrics
+   - Triggers for auto-updating timestamps
+   - Functions for business logic (`check_invoice_limit`, `calculate_recovery_rate`, `get_overdue_count`)
+   - Materialized views for common queries
+   - Encryption extension support for security
+
+2. **`docs/database-er-diagram.md`**: Detailed documentation including:
+   - Visual ER diagram with relationship cardinalities
+   - Table descriptions with column types and purposes
+   - Index strategy and performance notes
+   - Security policies (RLS)
+   - Migration and rollback instructions
+
+## Getting Started (Local Development)
+
+### Prerequisites
+
+- Python 3.11+
+- Git
+
+### Setup
+
+The project foundation is now in place. To get started:
+
+```bash
+# 1. Clone and install dependencies
+pip install -r requirements.txt
+
+# 2. Set up environment configuration
+cp .env.example .env
+# Edit .env with your database and API credentials (see Configuration section)
+
+# 3. Start the development server
+python -m src.main
+# or
+uvicorn src.main:app --reload
+
+# 4. Access the API
+# API documentation: http://localhost:8000/docs
+# Health check: http://localhost:8000/health
+```
+
+### Configuration
+
+Create a `.env` file from `.env.example` and configure:
+
+- **Database**: `DATABASE_URL` (PostgreSQL connection string)
+- **JWT**: `SECRET_KEY` for token signing
+- **Payment APIs**: Stripe, PayPal, Plaid credentials
+- **AI**: `OPENAI_API_KEY` for dispute letter generation
+- **Email**: SMTP settings for sending follow-ups
+- **Redis**: `REDIS_URL` for Celery task queue
+
+See `.env.example` for all available options.
+
+### Project Structure
+
+```
+.
+├── .env.example            # Environment variables template
+├── requirements.txt        # Python dependencies
+├── src/
+│   ├── main.py            # FastAPI application entry point
+│   └── core/
+│       ├── config.py      # Settings management (pydantic-settings)
+│       └── logger.py      # Logging configuration
+├── docs/                  # Documentation
+├── schema.sql             # Database schema (Phase 1.1)
+└── TASKS.md               # Development task list
+```
+
+### Current Status
+
+- ✅ Phase 1.1: Database schema design complete
+- ✅ Phase 1.2: FastAPI project structure initialized
+- 🔄 Phase 1.3: PostgreSQL setup (next task)
+- 🔄 Phase 1.4: API documentation outline (pending)
+
+## API Overview (Planned)
+
+### Public Endpoints
+
+- `POST /register` - User registration
+- `POST /login` - JWT authentication
+- `POST /refresh` - Refresh token rotation
+
+### Protected Endpoints
+
+- `GET|POST /invoices` - Invoice CRUD with filters
+- `GET /invoices/{id}` - Retrieve invoice details
+- `PATCH /invoices/{id}/status` - Update payment status
+- `POST /templates` - Create custom email templates
+- `GET|POST /campaigns` - Campaign management
+- `GET /analytics/recovery-rate` - KPI metrics
+
+### Webhook Endpoints
+
+- `POST /webhooks/stripe` - Stripe event receiver
+- `POST /webhooks/paypal` - PayPal IPN handler
+- `POST /webhooks/plaid` - Plaid transaction sync
+
+### Admin Endpoints (Admin only)
+
+- `GET /admin/users` - List all users
+- `GET /admin/metrics` - System health metrics
+- `POST /admin/users/{id}/tier` - Change subscription tier
+
+## Database Schema Highlights
+
+### Tables (11 core tables)
+
+| Table | Purpose | Key Columns |
+|-------|---------|-------------|
+| `users` | Account management | subscription_tier, invoice_limit |
+| `payment_connections` | Encrypted credentials | provider (stripe/paypal/plaid) |
+| `invoices` | Invoice records | status, stripe_payment_intent_id |
+| `templates` | Email/document templates | type, variables (JSON) |
+| `campaigns` | Campaign tracking | ab_test_variant, paid_after_send |
+| `ab_tests` | Experiment definitions | test_type, variants (JSON) |
+| `email_events` | Engagement tracking | event_type, occurred_at |
+| `webhook_events` | Idempotency store | provider, event_id (unique) |
+| `audit_logs` | Compliance logging | action, old_values, new_values |
+| `refresh_tokens` | JWT rotation | token_hash, expires_at |
+| `system_metrics` | Time-series data | metric_name, metric_value |
+
+### Key Features
+
+- **UUID primary keys** for security and distributed systems
+- **JSONB columns** for flexible metadata storage
+- **Partial indexes** on frequently queried external IDs
+- **Row Level Security** for multi-tenant isolation
+- **Encrypted credentials** for payment provider integrations
+- **Audit trail** for all data changes
+- **Idempotent webhook processing** via unique constraints
+- **Automatic timestamp updates** via triggers
+- **Materialized views** for dashboard performance
+
+## Environment Variables
+
+To be documented once implemented (after Task 1.2).
+
+## Testing
+
+Test suite will be implemented in Phase 5 using pytest with >80% coverage.
+
+```bash
+pytest tests/ -v --cov=src --cov-report=html
+```
+
+## Deployment
+
+Production deployment instructions will be added in Phase 5 (Docker, cloud hosting, CI/CD).
+
+## License
+
+To be determined.
+
+## Contact
+
+For questions or feedback about this project, please open an issue on GitHub.
[0m
Let me check the git branches:
[0m$ [0mgit branch -a
main
* wiggum/session-1774058292
[0m
