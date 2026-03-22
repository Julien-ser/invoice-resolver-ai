# Iteration 34 - invoice-resolver-ai

**Timestamp:** Fri Mar 20 11:37:32 PM EDT 2026
**Task:** **Task 4.3:** Create admin panel (FastAPI + simple HTML/JS or separate Streamlit page) for viewing all users, system health (Celery workers, API latency), and managing subscription tiers.

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
- Iteration: 34 / 64k Token Budget
- Attempt: 1 (previous attempts may have partial progress)
- **Mandate:** Operate efficiently. Use partial edits, not full file rewrites when possible.
- **Output:** Be concise and action-oriented.


## CURRENT PROJECT STATE (Iteration 34)

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
**Task 4.3:** Create admin panel (FastAPI + simple HTML/JS or separate Streamlit page) for viewing all users, system health (Celery workers, API latency), and managing subscription tiers.

**Instructions:** Complete this task. Mark [x] in TASKS.md when done. Create, modify, or delete files as needed. Execute commands as needed. Also update README.md to match this project (name, setup instructions, current progress). No permission needed—just act.
```

## OpenCode Output

```
[0m
> build · stepfun/step-3.5-flash:free
[0m
[0m• [0mExplore codebase structure[90m Explore Agent[0m
I'll complete Task 4.3 by creating the admin panel. Let me start by exploring the current codebase to understand the structure.
[0m✓ [0mExplore codebase structure[90m Explore Agent[0m
Let me examine the existing files more closely to implement the admin panel correctly.
[0m→ [0mRead src/api/deps.py
[0m→ [0mRead src/models.py[90m [limit=150, offset=1][0m
[0m→ [0mRead src/main.py
Let me check for SystemMetric and WebhookEvent models to understand what health data we have:
[0m✱ [0mGrep "class SystemMetric|class WebhookEvent"[90m in src/models.py · 2 matches[0m
[0m→ [0mRead src/models.py[90m [limit=80, offset=415][0m
Perfect! Now I'll create the admin panel. Let me start by creating the admin directory and routes:
[0m
[0m$ [0mmkdir -p /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin
Now I'll create the admin schemas and routes:
[0m
[0m← [0mWrite src/admin/schemas.py
Wrote file successfully.

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/dashboard/app.py">
ERROR [73:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [75:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [77:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [229:55] Cannot access attribute "apply" for class "ndarray[_AnyShape, dtype[Any]]"
  Attribute "apply" is unknown
ERROR [332:23] Cannot access attribute "apply" for class "DatetimeIndex"
  Attribute "apply" is unknown
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/celery_app.py">
ERROR [9:6] Import "celery" could not be resolved
ERROR [10:6] Import "celery.schedules" could not be resolved
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/deps.py">
ERROR [26:15] Return type of generator function must be compatible with "Generator[Generator[Session, Any, None], Any, Any]"
  "Generator[Generator[Session, Any, None], Unknown, Unknown]" is not assignable to "Generator[Session, None, None]"
    Type parameter "_YieldT_co@Generator" is covariant, but "Generator[Session, Any, None]" is not a subtype of "Session"
      "Generator[Session, Any, None]" is not assignable to "Session"
ERROR [50:24] Type "Any | None" is not assignable to declared type "str"
  Type "Any | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py">
ERROR [347:25] Argument of type "Tuple[str, dict[Unknown, Unknown]] | None" cannot be assigned to parameter "winning_variant" of type "Dict[str, Any] | None" in function "__init__"
  Type "Tuple[str, dict[Unknown, Unknown]] | None" is not assignable to type "Dict[str, Any] | None"
    Type "Tuple[str, dict[Unknown, Unknown]]" is not assignable to type "Dict[str, Any] | None"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "Dict[str, Any]"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "None"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/webhooks.py">
ERROR [143:20] No overloads for "compare_digest" match the provided arguments
ERROR [143:60] Argument of type "str | None" cannot be assigned to parameter "b" of type "AnyStr@compare_digest" in function "compare_digest"
  Type "str | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>
[0m
Now let me create the main admin routes file:
[0m← [0mWrite src/admin/routes.py
Wrote file successfully.

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/dashboard/app.py">
ERROR [73:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [75:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [77:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [229:55] Cannot access attribute "apply" for class "ndarray[_AnyShape, dtype[Any]]"
  Attribute "apply" is unknown
ERROR [332:23] Cannot access attribute "apply" for class "DatetimeIndex"
  Attribute "apply" is unknown
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/celery_app.py">
ERROR [9:6] Import "celery" could not be resolved
ERROR [10:6] Import "celery.schedules" could not be resolved
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/deps.py">
ERROR [26:15] Return type of generator function must be compatible with "Generator[Generator[Session, Any, None], Any, Any]"
  "Generator[Generator[Session, Any, None], Unknown, Unknown]" is not assignable to "Generator[Session, None, None]"
    Type parameter "_YieldT_co@Generator" is covariant, but "Generator[Session, Any, None]" is not a subtype of "Session"
      "Generator[Session, Any, None]" is not assignable to "Session"
ERROR [50:24] Type "Any | None" is not assignable to declared type "str"
  Type "Any | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py">
ERROR [347:25] Argument of type "Tuple[str, dict[Unknown, Unknown]] | None" cannot be assigned to parameter "winning_variant" of type "Dict[str, Any] | None" in function "__init__"
  Type "Tuple[str, dict[Unknown, Unknown]] | None" is not assignable to type "Dict[str, Any] | None"
    Type "Tuple[str, dict[Unknown, Unknown]]" is not assignable to type "Dict[str, Any] | None"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "Dict[str, Any]"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "None"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/webhooks.py">
ERROR [143:20] No overloads for "compare_digest" match the provided arguments
ERROR [143:60] Argument of type "str | None" cannot be assigned to parameter "b" of type "AnyStr@compare_digest" in function "compare_digest"
  Type "str | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>
[0m
Now create the admin/__init__.py to export the router:
[0m← [0mWrite src/admin/__init__.py
Wrote file successfully.

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/dashboard/app.py">
ERROR [73:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [75:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [77:9] Argument of type "str" cannot be assigned to parameter "value" of type "int" in function "__setitem__"
  "str" is not assignable to "int"
ERROR [229:55] Cannot access attribute "apply" for class "ndarray[_AnyShape, dtype[Any]]"
  Attribute "apply" is unknown
ERROR [332:23] Cannot access attribute "apply" for class "DatetimeIndex"
  Attribute "apply" is unknown
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/celery_app.py">
ERROR [9:6] Import "celery" could not be resolved
ERROR [10:6] Import "celery.schedules" could not be resolved
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/deps.py">
ERROR [26:15] Return type of generator function must be compatible with "Generator[Generator[Session, Any, None], Any, Any]"
  "Generator[Generator[Session, Any, None], Unknown, Unknown]" is not assignable to "Generator[Session, None, None]"
    Type parameter "_YieldT_co@Generator" is covariant, but "Generator[Session, Any, None]" is not a subtype of "Session"
      "Generator[Session, Any, None]" is not assignable to "Session"
ERROR [50:24] Type "Any | None" is not assignable to declared type "str"
  Type "Any | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/ab_testing.py">
ERROR [347:25] Argument of type "Tuple[str, dict[Unknown, Unknown]] | None" cannot be assigned to parameter "winning_variant" of type "Dict[str, Any] | None" in function "__init__"
  Type "Tuple[str, dict[Unknown, Unknown]] | None" is not assignable to type "Dict[str, Any] | None"
    Type "Tuple[str, dict[Unknown, Unknown]]" is not assignable to type "Dict[str, Any] | None"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "Dict[str, Any]"
      "Tuple[str, dict[Unknown, Unknown]]" is not assignable to "None"
</diagnostics>

LSP errors detected in other files:
<diagnostics file="/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/webhooks.py">
ERROR [143:20] No overloads for "compare_digest" match the provided arguments
ERROR [143:60] Argument of type "str | None" cannot be assigned to parameter "b" of type "AnyStr@compare_digest" in function "compare_digest"
  Type "str | None" is not assignable to type "str"
    "None" is not assignable to "str"
</diagnostics>
[0m
Now update main.py to include the admin router:
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
+from .admin import admin_router
 from .middleware import SubscriptionLimitCheckerMiddleware
 
 # Setup logging
 setup_logging(log_level="INFO", log_file=None)

[0m
[0m← [0mEdit src/main.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/main.py
@@ -38,8 +38,9 @@
 app.include_router(auth_router)
 app.include_router(invoices_router)
 app.include_router(webhooks_router)
 app.include_router(ab_testing_router)
+app.include_router(admin_router)
 
 # Future routers (to be implemented in later tasks)
 # app.include_router(invoice_router, prefix="/api/invoices", tags=["invoices"])
 # app.include_router(webhook_router, prefix="/api/webhooks", tags=["webhooks"])

[0m
[0m✱ [0mGrep "^class Template"[90m in src/models.py · 1 match[0m
Let me fix the template count issue in routes.py (I need to check the Template model name):
[0m✗ [0medit failed
[91m[1mError: [0mThe edit tool was called with invalid arguments: [
  {
    "expected": "string",
    "code": "invalid_type",
    "path": [
      "oldString"
    ],
    "message": "Invalid input: expected string, received undefined"
  },
  {
    "expected": "string",
    "code": "invalid_type",
    "path": [
      "newString"
    ],
    "message": "Invalid input: expected string, received undefined"
  }
].
Please rewrite the input so it satisfies the expected schema.
[0m
[0m← [0mEdit src/admin/routes.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/admin/routes.py
@@ -12,9 +12,16 @@
 from sqlalchemy import func, desc, asc, text
 from pydantic import BaseModel
 
 from src.api.deps import get_current_admin_user, get_db
-from src.models import User, PaymentConnection, WebhookEvent, SystemMetric, Invoice
+from src.models import (
+    User,
+    PaymentConnection,
+    WebhookEvent,
+    SystemMetric,
+    Invoice,
+    Template,
+)
 from src.core.config import settings
 from .schemas import (
     UserSummary,
     UserDetail,

[0m
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

**Completed at:** Fri Mar 20 11:41:28 PM EDT 2026
