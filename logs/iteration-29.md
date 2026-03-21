# Iteration 29 - invoice-resolver-ai

**Timestamp:** Fri Mar 20 11:17:18 PM EDT 2026
**Task:** **Task 3.4:** Implement PDF generation for dispute letters and small claims forms using WeasyPrint (HTML->PDF) or ReportLab. Create templates for common small claims forms (pre-filled with user/business info).

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
- Iteration: 29 / 64k Token Budget
- Attempt: 2 (previous attempts may have partial progress)
- **Mandate:** Operate efficiently. Use partial edits, not full file rewrites when possible.
- **Output:** Be concise and action-oriented.


## CURRENT PROJECT STATE (Iteration 29)

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
**Task 3.4:** Implement PDF generation for dispute letters and small claims forms using WeasyPrint (HTML->PDF) or ReportLab. Create templates for common small claims forms (pre-filled with user/business info).

**Instructions:** Complete this task. Mark [x] in TASKS.md when done. Create, modify, or delete files as needed. Execute commands as needed. Also update README.md to match this project (name, setup instructions, current progress). No permission needed—just act.
```

## OpenCode Output

```
[0m
> build · stepfun/step-3.5-flash:free
[0m
I'll help you complete Task 3.4: Implement PDF generation for dispute letters and small claims forms. Let me start by understanding the current project structure.
[0m✱ [0mGlob "**/*.py"[90m 36 matches[0m
[0m→ [0mRead TASKS.md
[0m→ [0mRead README.md
Now let me check the current PDF implementation and understand what needs to be completed:
[0m→ [0mRead src/pdf/generator.py
[0m→ [0mRead tests/test_pdf.py
[0m→ [0mRead requirements.txt
Let me check if the templates directory and files exist:
[0m→ [0mRead src/ai/dispute_drafter.py
[0m✱ [0mGlob "src/pdf/templates/*"[90m 2 matches[0m
[0m→ [0mRead src/pdf/templates/dispute_letter.html
[0m→ [0mRead src/pdf/templates/small_claims_form.html
Let me check the actual template files to ensure they're properly formatted:
Now let me verify that the tests pass and that everything is working correctly:
[0m
[0m$ [0mpython -m pytest tests/test_pdf.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
______________________ ERROR collecting tests/test_pdf.py ______________________
ImportError while importing test module '/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/tests/test_pdf.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_pdf.py:15: in <module>
    from src.pdf.generator import PDFGenerator, generate_pdf
src/pdf/__init__.py:3: in <module>
    from src.pdf.generator import PDFGenerator, generate_pdf
src/pdf/generator.py:13: in <module>
    from weasyprint import HTML, CSS
E   ModuleNotFoundError: No module named 'weasyprint'
------------------------------- Captured stdout --------------------------------
2026-03-20 23:17:49 - src.core.logger - INFO - Logging configured: level=INFO, file=None
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:55
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:55: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/test_pdf.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
========================= 4 warnings, 1 error in 0.24s =========================
[0m
The dependencies need to be installed. Let me install the requirements:
[0m$ [0mpip install weasyprint jinja2 -q
Now let me run the tests again:
[0m
[0m$ [0mpython -m pytest tests/test_pdf.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 11 items

tests/test_pdf.py::TestPDFGenerator::test_generator_initialization PASSED [  9%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_from_html PASSED  [ 18%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_returns_bytes PASSED [ 27%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_margins PASSED [ 36%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_page_size PASSED [ 45%]
tests/test_pdf.py::TestPDFGenerator::test_render_dispute_letter_template PASSED [ 54%]
tests/test_pdf.py::TestPDFGenerator::test_render_small_claims_template PASSED [ 63%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_missing_variable FAILED [ 72%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_not_found FAILED [ 81%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_additional_css PASSED [ 90%]
tests/test_pdf.py::TestPDFGenerator::test_multiple_generations_produce_different_files FAILED [100%]

=================================== FAILURES ===================================
____________ TestPDFGenerator.test_render_template_missing_variable ____________

self = <test_pdf.TestPDFGenerator object at 0x7fc280151b50>
dispute_letter_context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}

    def test_render_template_missing_variable(self, dispute_letter_context):
        """Test error handling when template variable is missing."""
        generator = PDFGenerator()
        context = dispute_letter_context.copy()
        del context["invoice_number"]  # Remove required variable
    
>       with pytest.raises(ValueError, match="Missing template variable"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'ValueError'>

tests/test_pdf.py:233: Failed
_______________ TestPDFGenerator.test_render_template_not_found ________________

self = <src.pdf.generator.PDFGenerator object at 0x7fc27c56ad50>
template_name = 'nonexistent.html', context = {}, output_path = None
kwargs = {}

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
        """
        try:
>           template = self.jinja_env.get_template(template_name)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

src/pdf/generator.py:177: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../venv/lib/python3.14/site-packages/jinja2/environment.py:1016: in get_template
    return self._load_template(name, globals)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/jinja2/environment.py:975: in _load_template
    template = self.loader.load(self, name, self.make_globals(globals))
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../venv/lib/python3.14/site-packages/jinja2/loaders.py:126: in load
    source, filename, uptodate = self.get_source(environment, name)
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <jinja2.loaders.FileSystemLoader object at 0x7fc27c56bd50>
environment = <jinja2.environment.Environment object at 0x7fc27c285e00>
template = 'nonexistent.html'

    def get_source(
        self, environment: "Environment", template: str
    ) -> t.Tuple[str, str, t.Callable[[], bool]]:
        pieces = split_template_path(template)
    
        for searchpath in self.searchpath:
            # Use posixpath even on Windows to avoid "drive:" or UNC
            # segments breaking out of the search directory.
            filename = posixpath.join(searchpath, *pieces)
    
            if os.path.isfile(filename):
                break
        else:
            plural = "path" if len(self.searchpath) == 1 else "paths"
            paths_str = ", ".join(repr(p) for p in self.searchpath)
>           raise TemplateNotFound(
                template,
                f"{template!r} not found in search {plural}: {paths_str}",
            )
E           jinja2.exceptions.TemplateNotFound: 'nonexistent.html' not found in search path: '/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates'

../../venv/lib/python3.14/site-packages/jinja2/loaders.py:209: TemplateNotFound

During handling of the above exception, another exception occurred:

self = <test_pdf.TestPDFGenerator object at 0x7fc27d8a3d50>

    def test_render_template_not_found(self):
        """Test error handling when template doesn't exist."""
        generator = PDFGenerator()
        with pytest.raises(FileNotFoundError):
>           generator.render_template("nonexistent.html", {})

tests/test_pdf.py:240: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.pdf.generator.PDFGenerator object at 0x7fc27c56ad50>
template_name = 'nonexistent.html', context = {}, output_path = None
kwargs = {}

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except Exception as e:
>           raise ValueError(f"Failed to render template {template_name}: {e}")
E           ValueError: Failed to render template nonexistent.html: 'nonexistent.html' not found in search path: '/home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates'

src/pdf/generator.py:180: ValueError
______ TestPDFGenerator.test_multiple_generations_produce_different_files ______

self = <test_pdf.TestPDFGenerator object at 0x7fc27d734f50>
dispute_letter_context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
tmp_path = PosixPath('/tmp/pytest-of-julien/pytest-192/test_multiple_generations_prod0')

    def test_multiple_generations_produce_different_files(
        self, dispute_letter_context, tmp_path
    ):
        """Test that multiple PDF generations produce unique files."""
        generator = PDFGenerator()
    
        output_path1 = tmp_path / "letter1.pdf"
        output_path2 = tmp_path / "letter2.pdf"
    
        # Modify context slightly between generations
        context1 = dispute_letter_context.copy()
        context2 = dispute_letter_context.copy()
        context2["amount"] = "999.99"
    
        result1 = generator.render_template(
            "dispute_letter.html", context1, output_path=output_path1
        )
        result2 = generator.render_template(
            "dispute_letter.html", context2, output_path=output_path2
        )
    
        assert result1.exists()
        assert result2.exists()
        # Files should be different sizes due to changed content
>       assert result1.stat().st_size != result2.stat().st_size
E       AssertionError: assert 15642 != 15642
E        +  where 15642 = os.stat_result(st_mode=33188, st_ino=534142, st_dev=49, st_nlink=1, st_uid=1000, st_gid=1000, st_size=15642, st_atime=1774063087, st_mtime=1774063087, st_ctime=1774063087).st_size
E        +    where os.stat_result(st_mode=33188, st_ino=534142, st_dev=49, st_nlink=1, st_uid=1000, st_gid=1000, st_size=15642, st_atime=1774063087, st_mtime=1774063087, st_ctime=1774063087) = stat()
E        +      where stat = PosixPath('/tmp/pytest-of-julien/pytest-192/test_multiple_generations_prod0/letter1.pdf').stat
E        +  and   15642 = os.stat_result(st_mode=33188, st_ino=534143, st_dev=49, st_nlink=1, st_uid=1000, st_gid=1000, st_size=15642, st_atime=1774063087, st_mtime=1774063087, st_ctime=1774063087).st_size
E        +    where os.stat_result(st_mode=33188, st_ino=534143, st_dev=49, st_nlink=1, st_uid=1000, st_gid=1000, st_size=15642, st_atime=1774063087, st_mtime=1774063087, st_ctime=1774063087) = stat()
E        +      where stat = PosixPath('/tmp/pytest-of-julien/pytest-192/test_multiple_generations_prod0/letter2.pdf').stat

tests/test_pdf.py:280: AssertionError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:55
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:55: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_pdf.py::TestPDFGenerator::test_render_template_missing_variable
FAILED tests/test_pdf.py::TestPDFGenerator::test_render_template_not_found - ...
FAILED tests/test_pdf.py::TestPDFGenerator::test_multiple_generations_produce_different_files
=================== 3 failed, 8 passed, 4 warnings in 2.33s ====================
[0m
Let me fix the failing tests. The issues are:

1. Test expects ValueError for missing template variables - need to use StrictUndefined
2. Test expects FileNotFoundError for missing template - should let TemplateNotFound bubble up
3. Test expects different file sizes - the amount may not affect PDF size significantly; we should check content differently or the amounts need to differ more

Let me update the generator to handle these cases properly:
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -10,9 +10,9 @@
 from typing import Optional, Union, Dict, Any
 from io import BytesIO
 
 from weasyprint import HTML, CSS
-from jinja2 import Environment, FileSystemLoader
+from jinja2 import Environment, FileSystemLoader, StrictUndefined
 
 from src.core.config import settings
 
 

[0m
Now update the Jinja2 environment to use StrictUndefined:
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -32,9 +32,11 @@
             os.path.dirname(os.path.abspath(__file__)), "templates"
         )
     self.templates_dir = Path(templates_dir)
     self.templates_dir.mkdir(parents=True, exist_ok=True)
-    self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
+    self.jinja_env = Environment(
+        loader=FileSystemLoader(str(self.templates_dir)), undefined=StrictUndefined
+    )
 
 def generate_pdf(
     self,
     html_content: str,

[0m
Now let's fix the exception handling:
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -11,8 +11,9 @@
 from io import BytesIO
 
 from weasyprint import HTML, CSS
 from jinja2 import Environment, FileSystemLoader, StrictUndefined
+from jinja2.exceptions import TemplateNotFound
 
 from src.core.config import settings
 
 

[0m
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -174,12 +174,20 @@
     **kwargs: Additional arguments passed to generate_pdf()
 
 Returns:
     PDF bytes or Path to saved file
+
+Raises:
+    FileNotFoundError: If the template file does not exist
+    ValueError: If template rendering fails for other reasons
 """
 try:
     template = self.jinja_env.get_template(template_name)
     html_content = template.render(**context)
+except TemplateNotFound:
+    raise FileNotFoundError(
+        f"Template '{template_name}' not found in {self.templates_dir}"
+    )
 except Exception as e:
     raise ValueError(f"Failed to render template {template_name}: {e}")
 
 return self.generate_pdf(html_content, output_path, **kwargs)

[0m
[0m← [0mEdit src/pdf/templates/dispute_letter.html
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
@@ -13,62 +13,62 @@
         <p>{{sender_phone}}</p>
     </div>
 
     <div class="date">
-        <strong>Date:</strong> {date}
+        <strong>Date:</strong> {{ date }}
     </div>
 
     <div class="recipient">
         <p><strong>To:</strong></p>
-        <p>{recipient_name}</p>
-        <p>{recipient_address}</p>
-        <p>{recipient_city_state_zip}</p>
+        <p>{{ recipient_name }}</p>
+        <p>{{ recipient_address }}</p>
+        <p>{{ recipient_city_state_zip }}</p>
     </div>
 
     <div class="subject">
-        <h2>Re: Dispute of Invoice #{invoice_number} - Amount Due: ${amount}</h2>
+        <h2>Re: Dispute of Invoice #{{ invoice_number }} - Amount Due: ${{ amount }}</h2>
     </div>
 
     <div class="content">
-        <p>Dear {recipient_name},</p>
+        <p>Dear {{ recipient_name }},</p>
 
-        <p>I am writing regarding invoice #{invoice_number} for the amount of ${amount}, which was issued on {issue_date} and became due on {due_date}. As of today, this invoice remains unpaid despite previous attempts to resolve this matter.</p>
+        <p>I am writing regarding invoice #{{ invoice_number }} for the amount of ${{ amount }}, which was issued on {{ issue_date }} and became due on {{ due_date }}. As of today, this invoice remains unpaid despite previous attempts to resolve this matter.</p>
 
         <h3>Invoice Details:</h3>
         <div class="invoice-details">
             <table>
-                <tr><th>Invoice Number</th><td>{invoice_number}</td></tr>
-                <tr><th>Amount</th><td>${amount} {currency}</td></tr>
-                <tr><th>Issue Date</th><td>{issue_date}</td></tr>
-                <tr><th>Due Date</th><td>{due_date}</td></tr>
-                <tr><th>Days Overdue</th><td>{days_overdue}</td></tr>
+                <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
+                <tr><th>Amount</th><td>${{ amount }} {{ currency }}</td></tr>
+                <tr><th>Issue Date</th><td>{{ issue_date }}</td></tr>
+                <tr><th>Due Date</th><td>{{ due_date }}</td></tr>
+                <tr><th>Days Overdue</th><td>{{ days_overdue }}</td></tr>
             </table>
         </div>
 
         {% if evidence_list %}
         <h3>Evidence of Communication and Service:</h3>
         {% for evidence in evidence_list %}
         <div class="evidence-item">
-            <strong>{{evidence.date}}:</strong> {{evidence.description}}
-            {% if evidence.amount %}(Amount: ${{evidence.amount}}){% endif %}
+            <strong>{{ evidence.date }}:</strong> {{ evidence.description }}
+            {% if evidence.amount %}(Amount: ${{ evidence.amount }}){% endif %}
         </div>
         {% endfor %}
         {% else %}
         <p><em>No detailed evidence provided.</em></p>
         {% endif %}
 
         <h3>Summary:</h3>
-        <p>The services/products were provided in full as described in the original agreement. All attempts to resolve this matter amicably have been exhausted. The payment is now past due by {days_overdue} days.</p>
+        <p>The services/products were provided in full as described in the original agreement. All attempts to resolve this matter amicably have been exhausted. The payment is now past due by {{ days_overdue }} days.</p>
 
         <h3>Demand for Payment:</h3>
-        <p>I formally demand payment of the full amount of <strong>${amount} {currency}</strong> within <strong>14 days</strong> from the date of this letter. The deadline for payment is <strong>{deadline_date}</strong>.</p>
+        <p>I formally demand payment of the full amount of <strong>${{ amount }} {{ currency }}</strong> within <strong>14 days</strong> from the date of this letter. The deadline for payment is <strong>{{ deadline_date }}</strong>.</p>
 
         <div class="payment-info">
             <h4>Accepted Payment Methods:</h4>
             <ul>
-                {% if payment_link %}<li>Online Payment Link: <a href="{payment_link}">{payment_link}</a></li>{% endif %}
-                {% if bank_details %}<li>Bank Transfer: {bank_details}</li>{% endif %}
-                {% if check_address %}<li>Check/Mail: {check_address}</li>{% endif %}
+                {% if payment_link %}<li>Online Payment Link: <a href="{{ payment_link }}">{{ payment_link }}</a></li>{% endif %}
+                {% if bank_details %}<li>Bank Transfer: {{ bank_details }}</li>{% endif %}
+                {% if check_address %}<li>Check/Mail: {{ check_address }}</li>{% endif %}
             </ul>
         </div>
 
         <h3>Consequences of Non-Payment:</h3>
@@ -77,14 +77,14 @@
         <p>I hope to resolve this matter without further action. Please contact me immediately to arrange for payment.</p>
 
         <p>Sincerely,</p>
 
-        <p><strong>{sender_name}</strong></p>
-        <p>{sender_title}</p>
+        <p><strong>{{ sender_name }}</strong></p>
+        <p>{{ sender_title }}</p>
     </div>
 
     <div class="footer">
         <p>This letter is sent without prejudice to any rights or remedies available under applicable law.</p>
-        <p>CC: {cc_parties}</p>
+        <p>CC: {{ cc_parties }}</p>
     </div>
 </body>
 </html>

[0m
I see the issue - the templates are using wrong variable syntax. They use `{amount}` instead of Jinja2's `{{ amount }}`. Let me fix both templates:
Now fix the small claims template:
[0m← [0mEdit src/pdf/templates/small_claims_form.html
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
@@ -7,16 +7,177 @@
 <body>
     <div class="header">
         <h1>Small Claims Court Preparation Document</h1>
         <h2>Case Summary & Evidence Packet</h2>
-        <p><strong>Prepared for:</strong> {user_name}</p>
-        <p><strong>Prepared Date:</strong> {prepared_date}</p>
+        <p><strong>Prepared for:</strong> {{ user_name }}</p>
+        <p><strong>Prepared Date:</strong> {{ prepared_date }}</p>
     </div>
 
     <h2>PART 1: CASE SUMMARY</h2>
 
     <h3>1.1 Parties Involved</h3>
     <table>
+        <tr><th>Plaintiff (You)</th><td>{{ user_name }}</td></tr>
+        <tr><th>Plaintiff Address</th><td>{{ user_address }}</td></tr>
+        <tr><th>Plaintiff Phone</th><td>{{ user_phone }}</td></tr>
+        <tr><th>Plaintiff Email</th><td>{{ user_email }}</td></tr>
+        <tr><th>Defendant</th><td>{{ defendant_name }}</td></tr>
+        <tr><th>Defendant Address</th><td>{{ defendant_address }}</td></tr>
+        {% if defendant_phone %}<tr><th>Defendant Phone</th><td>{{ defendant_phone }}</td></tr>{% endif %}
+        {% if defendant_email %}<tr><th>Defendant Email</th><td>{{ defendant_email }}</td></tr>{% endif %}
+    </table>
+
+    <h3>1.2 Case Information</h3>
+    <table>
+        <tr><th>Amount in Dispute</th><td>${{ amount }} {{ currency }}</td></tr>
+        <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
+        <tr><th>Date of Incident</th><td>{{ issue_date }}</td></tr>
+        <tr><th>Date Invoice Became Due</th><td>{{ due_date }}</td></tr>
+        <tr><th>Days Past Due</th><td>{{ days_overdue }}</td></tr>
+        <tr><th>Jurisdiction</th><td>{{ jurisdiction }}</td></tr>
+    </table>
+
+    <h3>1.3 Nature of Claim</h3>
+    <p><strong>Type of Case:</strong> Breach of Contract / Debt Collection</p>
+    <p><strong>Description:</strong></p>
+    <div class="highlight">
+        {{ description }}
+    </div>
+
+    <h2>PART 2: CHRONOLOGICAL TIMELINE</h2>
+
+    <table>
+        <thead>
+            <tr><th>Date</th><th>Event</th><th>Documentation</th></tr>
+        </thead>
+        <tbody>
+            {% for event in timeline %}
+            <tr>
+                <td>{{ event.date }}</td>
+                <td>{{ event.description }}</td>
+                <td>{% if event.document %}{{ event.document }}{% else %}N/A{% endif %}
+            </tr>
+            {% endfor %}
+        </tbody>
+    </table>
+
+    <h2>PART 3: EVIDENCE LIST</h2>
+
+    <div class="evidence-section">
+        {% for evidence in evidence_list %}
+        <div class="evidence-item">
+            <h4>{{ evidence.date }}: {{ evidence.type.title() }}</h4>
+            <p>{{ evidence.description }}</p>
+            {% if evidence.amount %}<p><strong>Amount:</strong> ${{ evidence.amount }}</p>{% endif %}
+            <p><strong>Document/Exhibit:</strong> {{ evidence.document or "See attached" }}</p>
+        </div>
+        {% endfor %}
+    </div>
+
+    <h2>PART 4: DAMAGES CALCULATION</h2>
+
+    <table>
+        <tr><th>Principal Amount (Invoice)</th><td>${{ amount }} {{ currency }}</td></tr>
+        <tr><th>Interest (if applicable)</th><td>${{ interest_amount }} {{ currency }}</td></tr>
+        <tr><th>Filing Fees</th><td>$50.00 USD (estimated)</td></tr>
+        <tr><th>Service of Process</th><td>$30.00 USD (estimated)</td></tr>
+        {% if additional_costs %}
+        <tr><th>Additional Costs</th><td>${{ additional_costs }} {{ currency }}</td></tr>
+        {% endif %}
+        <tr><th><strong>Total Claim Amount</strong></th><td><strong>${{ total_amount }} {{ currency }}</strong></td></tr>
+    </table>
+
+    <h2>PART 5: WITNESS INFORMATION</h2>
+
+    {% if witnesses %}
+    <table>
+        <thead>
+            <tr><th>Name</th><th>Contact</th><th>Relevance</th></tr>
+        </thead>
+        <tbody>
+            {% for witness in witnesses %}
+            <tr>
+                <td>{{ witness.name }}</td>
+                <td>{{ witness.contact }}</td>
+                <td>{{ witness.relevance }}</td>
+            </tr>
+            {% endfor %}
+        </tbody>
+    </table>
+    {% else %}
+    <p><em>No witness information available at this time.</em></p>
+    {% endif %}
+
+    <h2>PART 6: COURT FORMS & FILING INSTRUCTIONS</h2>
+
+    <div class="forms-section">
+        <h3>6.1 Required Forms</h3>
+        <ol>
+            <li><strong>Plaintiff's Claim and Information Sheet</strong> - Main filing form</li>
+            <li><strong>Summons</strong> - To be issued by the court</li>
+            <li><strong>Proof of Service</strong> - After serving the defendant</li>
+            <li><strong>Witness List</strong> - List of witnesses you plan to call</li>
+            <li><strong>Exhibit List</strong> - List of evidence documents</li>
+        </ol>
+
+        <h3>6.2 Filing Steps</h3>
+        <ol>
+            <li>Complete all forms with information from this packet</li>
+            <li>File at the appropriate small claims court in {{ jurisdiction }}</li>
+            <li>Pay the filing fee (approximately $50-$100)</li>
+            <li>Observe the statute of limitations: {{ statute_of_limitations }}</li>
+            <li>Serve the defendant with summons and complaint</li>
+            <li>Prepare for court hearing (bring this packet and all originals)</li>
+        </ol>
+
+        <h3>6.3 What to Bring to Court</h3>
+        <ul>
+            <li>Original signed contract/agreement</li>
+            <li>Copy of invoice #{{ invoice_number }}</li>
+            <li>All communication records (emails, texts, letters)</li>
+            <li>Payment records (if any partial payments were made)</li>
+            <li>This preparation document</li>
+            <li>Photo copies of all evidence for the judge and defendant</li>
+        </ul>
+    </div>
+
+    <h2>PART 7: TIPS FOR COURT PRESENTATION</h2>
+
+    <div class="tips-section">
+        <ul>
+            <li><strong>Be concise:</strong> Present your case clearly and without emotion</li>
+            <li><strong>Stick to facts:</strong> Bring evidence to support every claim</li>
+            <li><strong>Bring originals:</strong> Court requires originals, provide copies to all parties</li>
+            <li><strong>Practice:</strong> Rehearse your statement before the hearing</li>
+            <li><strong>Be respectful:</strong> Address the judge as "Your Honor"</li>
+            <li><strong>Bring witnesses:</strong> Have them wait outside until called</li>
+            <li><strong>Know your remedy:</strong> Clearly state the amount you are seeking</li>
+        </ul>
+    </div>
+
+    <h2>PART 8: LEGAL REFERENCES</h2>
+
+    <div class="legal-section">
+        <p><strong>Relevant Statutes:</strong></p>
+        <ul>
+            <li>Small Claims Court Jurisdiction: Amounts up to $10,000 (varies by jurisdiction)</li>
+            <li>Statute of Limitations for Written Contracts: Typically 4-6 years</li>
+            <li>Interest Rate: State statutory rate unless contract specifies</li>
+        </ul>
+
+        <p><strong>Note:</strong> This document is prepared for informational purposes and does not constitute legal advice. Consider consulting with an attorney for complex cases.</p>
+    </div>
+
+    <div class="footer">
+        <p><strong>Prepared by:</strong> Invoice Resolver AI</p>
+        <p><strong>Contact for Questions:</strong> {{ support_contact }}</p>
+        <p>Document generated on {{ generated_date }}</p>
+    </div>
+
+    <h2>PART 1: CASE SUMMARY</h2>
+
+    <h3>1.1 Parties Involved</h3>
+    <table>
         <tr><th>Plaintiff (You)</th><td>{user_name}</td></tr>
         <tr><th>Plaintiff Address</th><td>{user_address}</td></tr>
         <tr><th>Plaintiff Phone</th><td>{user_phone}</td></tr>
         <tr><th>Plaintiff Email</th><td>{user_email}</td></tr>

[0m
Now update the generator to properly handle UndefinedError:
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -11,9 +11,9 @@
 from io import BytesIO
 
 from weasyprint import HTML, CSS
 from jinja2 import Environment, FileSystemLoader, StrictUndefined
-from jinja2.exceptions import TemplateNotFound
+from jinja2.exceptions import TemplateNotFound, UndefinedError
 
 from src.core.config import settings
 
 

[0m
[0m← [0mEdit src/pdf/generator.py
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/generator.py
@@ -177,17 +177,19 @@
     PDF bytes or Path to saved file
 
 Raises:
     FileNotFoundError: If the template file does not exist
-    ValueError: If template rendering fails for other reasons
+    ValueError: If template rendering fails for other reasons (including missing variables)
 """
 try:
     template = self.jinja_env.get_template(template_name)
     html_content = template.render(**context)
 except TemplateNotFound:
     raise FileNotFoundError(
         f"Template '{template_name}' not found in {self.templates_dir}"
     )
+except UndefinedError as e:
+    raise ValueError(f"Missing template variable: {e}")
 except Exception as e:
     raise ValueError(f"Failed to render template {template_name}: {e}")
 
 return self.generate_pdf(html_content, output_path, **kwargs)

[0m
Now run the tests again:
[0m$ [0mpython -m pytest tests/test_pdf.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 11 items

tests/test_pdf.py::TestPDFGenerator::test_generator_initialization PASSED [  9%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_from_html PASSED  [ 18%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_returns_bytes PASSED [ 27%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_margins PASSED [ 36%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_page_size PASSED [ 45%]
tests/test_pdf.py::TestPDFGenerator::test_render_dispute_letter_template FAILED [ 54%]
tests/test_pdf.py::TestPDFGenerator::test_render_small_claims_template FAILED [ 63%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_missing_variable PASSED [ 72%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_not_found PASSED [ 81%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_additional_css PASSED [ 90%]
tests/test_pdf.py::TestPDFGenerator::test_multiple_generations_produce_different_files FAILED [100%]

=================================== FAILURES ===================================
_____________ TestPDFGenerator.test_render_dispute_letter_template _____________

self = <src.pdf.generator.PDFGenerator object at 0x7f8b01524a70>
template_name = 'dispute_letter.html'
context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_dispute_letter_tem0/dispute_letter.pdf')
kwargs = {}, template = <Template 'dispute_letter.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
>           html_content = template.render(**context)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^

src/pdf/generator.py:185: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../venv/lib/python3.14/site-packages/jinja2/environment.py:1295: in render
    self.environment.handle_exception()
../../venv/lib/python3.14/site-packages/jinja2/environment.py:942: in handle_exception
    raise rewrite_traceback_stack(source=source)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Dispute Letter - Invoice #{invoice_number}</title>
    </head>
    <body>
        <div class="header">
            <h1>{{sender_name}}</h1>
            <p>{{sender_address}}</p>
            <p>{{sender_city_state_zip}}</p>
            <p>{{sender_email}}</p>
            <p>{{sender_phone}}</p>
        </div>
    
        <div class="date">
            <strong>Date:</strong> {{ date }}
        </div>
    
        <div class="recipient">
            <p><strong>To:</strong></p>
            <p>{{ recipient_name }}</p>
            <p>{{ recipient_address }}</p>
            <p>{{ recipient_city_state_zip }}</p>
        </div>
    
        <div class="subject">
            <h2>Re: Dispute of Invoice #{{ invoice_number }} - Amount Due: ${{ amount }}</h2>
        </div>
    
        <div class="content">
            <p>Dear {{ recipient_name }},</p>
    
            <p>I am writing regarding invoice #{{ invoice_number }} for the amount of ${{ amount }}, which was issued on {{ issue_date }} and became due on {{ due_date }}. As of today, this invoice remains unpaid despite previous attempts to resolve this matter.</p>
    
            <h3>Invoice Details:</h3>
            <div class="invoice-details">
                <table>
                    <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
                    <tr><th>Amount</th><td>${{ amount }} {{ currency }}</td></tr>
                    <tr><th>Issue Date</th><td>{{ issue_date }}</td></tr>
                    <tr><th>Due Date</th><td>{{ due_date }}</td></tr>
                    <tr><th>Days Overdue</th><td>{{ days_overdue }}</td></tr>
                </table>
            </div>
    
            {% if evidence_list %}
            <h3>Evidence of Communication and Service:</h3>
            {% for evidence in evidence_list %}
            <div class="evidence-item">
                <strong>{{ evidence.date }}:</strong> {{ evidence.description }}
>               {% if evidence.amount %}(Amount: ${{ evidence.amount }}){% endif %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
E               jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'amount'

src/pdf/templates/dispute_letter.html:52: UndefinedError

During handling of the above exception, another exception occurred:

self = <test_pdf.TestPDFGenerator object at 0x7f8b02744c00>
dispute_letter_context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
tmp_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_dispute_letter_tem0')

    def test_render_dispute_letter_template(self, dispute_letter_context, tmp_path):
        """Test rendering dispute letter template."""
        generator = PDFGenerator()
        output_path = tmp_path / "dispute_letter.pdf"
>       result = generator.render_template(
            "dispute_letter.html", dispute_letter_context, output_path=output_path
        )

tests/test_pdf.py:209: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.pdf.generator.PDFGenerator object at 0x7f8b01524a70>
template_name = 'dispute_letter.html'
context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_dispute_letter_tem0/dispute_letter.pdf')
kwargs = {}, template = <Template 'dispute_letter.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            )
        except UndefinedError as e:
>           raise ValueError(f"Missing template variable: {e}")
E           ValueError: Missing template variable: 'dict object' has no attribute 'amount'

src/pdf/generator.py:191: ValueError
______________ TestPDFGenerator.test_render_small_claims_template ______________

self = <src.pdf.generator.PDFGenerator object at 0x7f8b01546580>
template_name = 'small_claims_form.html'
context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_small_claims_templ0/small_claims.pdf')
kwargs = {}, template = <Template 'small_claims_form.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
>           html_content = template.render(**context)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^

src/pdf/generator.py:185: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../venv/lib/python3.14/site-packages/jinja2/environment.py:1295: in render
    self.environment.handle_exception()
../../venv/lib/python3.14/site-packages/jinja2/environment.py:942: in handle_exception
    raise rewrite_traceback_stack(source=source)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Small Claims Court Preparation - Invoice #{invoice_number}</title>
    </head>
    <body>
        <div class="header">
            <h1>Small Claims Court Preparation Document</h1>
            <h2>Case Summary & Evidence Packet</h2>
            <p><strong>Prepared for:</strong> {{ user_name }}</p>
            <p><strong>Prepared Date:</strong> {{ prepared_date }}</p>
        </div>
    
        <h2>PART 1: CASE SUMMARY</h2>
    
        <h3>1.1 Parties Involved</h3>
        <table>
            <tr><th>Plaintiff (You)</th><td>{{ user_name }}</td></tr>
            <tr><th>Plaintiff Address</th><td>{{ user_address }}</td></tr>
            <tr><th>Plaintiff Phone</th><td>{{ user_phone }}</td></tr>
            <tr><th>Plaintiff Email</th><td>{{ user_email }}</td></tr>
            <tr><th>Defendant</th><td>{{ defendant_name }}</td></tr>
            <tr><th>Defendant Address</th><td>{{ defendant_address }}</td></tr>
            {% if defendant_phone %}<tr><th>Defendant Phone</th><td>{{ defendant_phone }}</td></tr>{% endif %}
            {% if defendant_email %}<tr><th>Defendant Email</th><td>{{ defendant_email }}</td></tr>{% endif %}
        </table>
    
        <h3>1.2 Case Information</h3>
        <table>
            <tr><th>Amount in Dispute</th><td>${{ amount }} {{ currency }}</td></tr>
            <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
            <tr><th>Date of Incident</th><td>{{ issue_date }}</td></tr>
            <tr><th>Date Invoice Became Due</th><td>{{ due_date }}</td></tr>
            <tr><th>Days Past Due</th><td>{{ days_overdue }}</td></tr>
            <tr><th>Jurisdiction</th><td>{{ jurisdiction }}</td></tr>
        </table>
    
        <h3>1.3 Nature of Claim</h3>
        <p><strong>Type of Case:</strong> Breach of Contract / Debt Collection</p>
        <p><strong>Description:</strong></p>
        <div class="highlight">
            {{ description }}
        </div>
    
        <h2>PART 2: CHRONOLOGICAL TIMELINE</h2>
    
        <table>
            <thead>
                <tr><th>Date</th><th>Event</th><th>Documentation</th></tr>
            </thead>
            <tbody>
                {% for event in timeline %}
                <tr>
                    <td>{{ event.date }}</td>
                    <td>{{ event.description }}</td>
                    <td>{% if event.document %}{{ event.document }}{% else %}N/A{% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    
        <h2>PART 3: EVIDENCE LIST</h2>
    
        <div class="evidence-section">
            {% for evidence in evidence_list %}
            <div class="evidence-item">
                <h4>{{ evidence.date }}: {{ evidence.type.title() }}</h4>
                <p>{{ evidence.description }}</p>
>               {% if evidence.amount %}<p><strong>Amount:</strong> ${{ evidence.amount }}</p>{% endif %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
E               jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'amount'

src/pdf/templates/small_claims_form.html:70: UndefinedError

During handling of the above exception, another exception occurred:

self = <test_pdf.TestPDFGenerator object at 0x7f8b02744e20>
small_claims_context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
tmp_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_small_claims_templ0')

    def test_render_small_claims_template(self, small_claims_context, tmp_path):
        """Test rendering small claims form template."""
        generator = PDFGenerator()
        output_path = tmp_path / "small_claims.pdf"
>       result = generator.render_template(
            "small_claims_form.html", small_claims_context, output_path=output_path
        )

tests/test_pdf.py:220: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.pdf.generator.PDFGenerator object at 0x7f8b01546580>
template_name = 'small_claims_form.html'
context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_render_small_claims_templ0/small_claims.pdf')
kwargs = {}, template = <Template 'small_claims_form.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            )
        except UndefinedError as e:
>           raise ValueError(f"Missing template variable: {e}")
E           ValueError: Missing template variable: 'dict object' has no attribute 'amount'

src/pdf/generator.py:191: ValueError
______ TestPDFGenerator.test_multiple_generations_produce_different_files ______

self = <src.pdf.generator.PDFGenerator object at 0x7f8b015e3b60>
template_name = 'dispute_letter.html'
context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_multiple_generations_prod0/letter1.pdf')
kwargs = {}, template = <Template 'dispute_letter.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
>           html_content = template.render(**context)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^

src/pdf/generator.py:185: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../venv/lib/python3.14/site-packages/jinja2/environment.py:1295: in render
    self.environment.handle_exception()
../../venv/lib/python3.14/site-packages/jinja2/environment.py:942: in handle_exception
    raise rewrite_traceback_stack(source=source)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Dispute Letter - Invoice #{invoice_number}</title>
    </head>
    <body>
        <div class="header">
            <h1>{{sender_name}}</h1>
            <p>{{sender_address}}</p>
            <p>{{sender_city_state_zip}}</p>
            <p>{{sender_email}}</p>
            <p>{{sender_phone}}</p>
        </div>
    
        <div class="date">
            <strong>Date:</strong> {{ date }}
        </div>
    
        <div class="recipient">
            <p><strong>To:</strong></p>
            <p>{{ recipient_name }}</p>
            <p>{{ recipient_address }}</p>
            <p>{{ recipient_city_state_zip }}</p>
        </div>
    
        <div class="subject">
            <h2>Re: Dispute of Invoice #{{ invoice_number }} - Amount Due: ${{ amount }}</h2>
        </div>
    
        <div class="content">
            <p>Dear {{ recipient_name }},</p>
    
            <p>I am writing regarding invoice #{{ invoice_number }} for the amount of ${{ amount }}, which was issued on {{ issue_date }} and became due on {{ due_date }}. As of today, this invoice remains unpaid despite previous attempts to resolve this matter.</p>
    
            <h3>Invoice Details:</h3>
            <div class="invoice-details">
                <table>
                    <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
                    <tr><th>Amount</th><td>${{ amount }} {{ currency }}</td></tr>
                    <tr><th>Issue Date</th><td>{{ issue_date }}</td></tr>
                    <tr><th>Due Date</th><td>{{ due_date }}</td></tr>
                    <tr><th>Days Overdue</th><td>{{ days_overdue }}</td></tr>
                </table>
            </div>
    
            {% if evidence_list %}
            <h3>Evidence of Communication and Service:</h3>
            {% for evidence in evidence_list %}
            <div class="evidence-item">
                <strong>{{ evidence.date }}:</strong> {{ evidence.description }}
>               {% if evidence.amount %}(Amount: ${{ evidence.amount }}){% endif %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
E               jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'amount'

src/pdf/templates/dispute_letter.html:52: UndefinedError

During handling of the above exception, another exception occurred:

self = <test_pdf.TestPDFGenerator object at 0x7f8b0272cf50>
dispute_letter_context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
tmp_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_multiple_generations_prod0')

    def test_multiple_generations_produce_different_files(
        self, dispute_letter_context, tmp_path
    ):
        """Test that multiple PDF generations produce unique files."""
        generator = PDFGenerator()
    
        output_path1 = tmp_path / "letter1.pdf"
        output_path2 = tmp_path / "letter2.pdf"
    
        # Modify context slightly between generations
        context1 = dispute_letter_context.copy()
        context2 = dispute_letter_context.copy()
        context2["amount"] = "999.99"
    
>       result1 = generator.render_template(
            "dispute_letter.html", context1, output_path=output_path1
        )

tests/test_pdf.py:270: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.pdf.generator.PDFGenerator object at 0x7f8b015e3b60>
template_name = 'dispute_letter.html'
context = {'amount': '1250.00', 'bank_details': 'Bank of Example, Account: 123456789, Routing: 987654321', 'cc_parties': 'Legal Department (if applicable)', 'check_address': '123 Main St, Anytown, CA 12345', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-193/test_multiple_generations_prod0/letter1.pdf')
kwargs = {}, template = <Template 'dispute_letter.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            )
        except UndefinedError as e:
>           raise ValueError(f"Missing template variable: {e}")
E           ValueError: Missing template variable: 'dict object' has no attribute 'amount'

src/pdf/generator.py:191: ValueError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:55
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:55: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_pdf.py::TestPDFGenerator::test_render_dispute_letter_template
FAILED tests/test_pdf.py::TestPDFGenerator::test_render_small_claims_template
FAILED tests/test_pdf.py::TestPDFGenerator::test_multiple_generations_produce_different_files
=================== 3 failed, 8 passed, 4 warnings in 1.36s ====================
[0m
The test contexts don't have `amount` in evidence items because they're optional. Need to fix templates to safely check optional fields. Use `evidence.amount is defined`:
[0m← [0mEdit src/pdf/templates/dispute_letter.html
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/dispute_letter.html
@@ -48,9 +48,9 @@
 <h3>Evidence of Communication and Service:</h3>
 {% for evidence in evidence_list %}
 <div class="evidence-item">
     <strong>{{ evidence.date }}:</strong> {{ evidence.description }}
-    {% if evidence.amount %}(Amount: ${{ evidence.amount }}){% endif %}
+    {% if evidence.amount is defined %}(Amount: ${{ evidence.amount }}){% endif %}
 </div>
 {% endfor %}
 {% else %}
 <p><em>No detailed evidence provided.</em></p>

[0m
Fix small claims template as well:
[0m← [0mEdit src/pdf/templates/small_claims_form.html
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
@@ -66,9 +66,9 @@
     {% for evidence in evidence_list %}
     <div class="evidence-item">
         <h4>{{ evidence.date }}: {{ evidence.type.title() }}</h4>
         <p>{{ evidence.description }}</p>
-        {% if evidence.amount %}<p><strong>Amount:</strong> ${{ evidence.amount }}</p>{% endif %}
+        {% if evidence.amount is defined %}<p><strong>Amount:</strong> ${{ evidence.amount }}</p>{% endif %}
         <p><strong>Document/Exhibit:</strong> {{ evidence.document or "See attached" }}</p>
     </div>
     {% endfor %}
 </div>

[0m
Now run tests again:
[0m$ [0mpython -m pytest tests/test_pdf.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /home/julien/Desktop/Free-Wiggum-opencode/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai
plugins: langsmith-0.7.16, anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, mock-3.15.1, dash-4.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 11 items

tests/test_pdf.py::TestPDFGenerator::test_generator_initialization PASSED [  9%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_from_html PASSED  [ 18%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_returns_bytes PASSED [ 27%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_margins PASSED [ 36%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_custom_page_size PASSED [ 45%]
tests/test_pdf.py::TestPDFGenerator::test_render_dispute_letter_template PASSED [ 54%]
tests/test_pdf.py::TestPDFGenerator::test_render_small_claims_template FAILED [ 63%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_missing_variable PASSED [ 72%]
tests/test_pdf.py::TestPDFGenerator::test_render_template_not_found PASSED [ 81%]
tests/test_pdf.py::TestPDFGenerator::test_generate_pdf_with_additional_css PASSED [ 90%]
tests/test_pdf.py::TestPDFGenerator::test_multiple_generations_produce_different_files PASSED [100%]

=================================== FAILURES ===================================
______________ TestPDFGenerator.test_render_small_claims_template ______________

self = <src.pdf.generator.PDFGenerator object at 0x7fa8d991b350>
template_name = 'small_claims_form.html'
context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-194/test_render_small_claims_templ0/small_claims.pdf')
kwargs = {}, template = <Template 'small_claims_form.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
>           html_content = template.render(**context)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^

src/pdf/generator.py:185: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
../../venv/lib/python3.14/site-packages/jinja2/environment.py:1295: in render
    self.environment.handle_exception()
../../venv/lib/python3.14/site-packages/jinja2/environment.py:942: in handle_exception
    raise rewrite_traceback_stack(source=source)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Small Claims Court Preparation - Invoice #{invoice_number}</title>
    </head>
    <body>
        <div class="header">
            <h1>Small Claims Court Preparation Document</h1>
            <h2>Case Summary & Evidence Packet</h2>
            <p><strong>Prepared for:</strong> {{ user_name }}</p>
            <p><strong>Prepared Date:</strong> {{ prepared_date }}</p>
        </div>
    
        <h2>PART 1: CASE SUMMARY</h2>
    
        <h3>1.1 Parties Involved</h3>
        <table>
            <tr><th>Plaintiff (You)</th><td>{{ user_name }}</td></tr>
            <tr><th>Plaintiff Address</th><td>{{ user_address }}</td></tr>
            <tr><th>Plaintiff Phone</th><td>{{ user_phone }}</td></tr>
            <tr><th>Plaintiff Email</th><td>{{ user_email }}</td></tr>
            <tr><th>Defendant</th><td>{{ defendant_name }}</td></tr>
            <tr><th>Defendant Address</th><td>{{ defendant_address }}</td></tr>
            {% if defendant_phone %}<tr><th>Defendant Phone</th><td>{{ defendant_phone }}</td></tr>{% endif %}
            {% if defendant_email %}<tr><th>Defendant Email</th><td>{{ defendant_email }}</td></tr>{% endif %}
        </table>
    
        <h3>1.2 Case Information</h3>
        <table>
            <tr><th>Amount in Dispute</th><td>${{ amount }} {{ currency }}</td></tr>
            <tr><th>Invoice Number</th><td>{{ invoice_number }}</td></tr>
            <tr><th>Date of Incident</th><td>{{ issue_date }}</td></tr>
            <tr><th>Date Invoice Became Due</th><td>{{ due_date }}</td></tr>
            <tr><th>Days Past Due</th><td>{{ days_overdue }}</td></tr>
            <tr><th>Jurisdiction</th><td>{{ jurisdiction }}</td></tr>
        </table>
    
        <h3>1.3 Nature of Claim</h3>
        <p><strong>Type of Case:</strong> Breach of Contract / Debt Collection</p>
        <p><strong>Description:</strong></p>
        <div class="highlight">
            {{ description }}
        </div>
    
        <h2>PART 2: CHRONOLOGICAL TIMELINE</h2>
    
        <table>
            <thead>
                <tr><th>Date</th><th>Event</th><th>Documentation</th></tr>
            </thead>
            <tbody>
                {% for event in timeline %}
                <tr>
                    <td>{{ event.date }}</td>
                    <td>{{ event.description }}</td>
                    <td>{% if event.document %}{{ event.document }}{% else %}N/A{% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    
        <h2>PART 3: EVIDENCE LIST</h2>
    
        <div class="evidence-section">
            {% for evidence in evidence_list %}
            <div class="evidence-item">
                <h4>{{ evidence.date }}: {{ evidence.type.title() }}</h4>
                <p>{{ evidence.description }}</p>
                {% if evidence.amount is defined %}<p><strong>Amount:</strong> ${{ evidence.amount }}</p>{% endif %}
                <p><strong>Document/Exhibit:</strong> {{ evidence.document or "See attached" }}</p>
            </div>
            {% endfor %}
        </div>
    
        <h2>PART 4: DAMAGES CALCULATION</h2>
    
        <table>
            <tr><th>Principal Amount (Invoice)</th><td>${{ amount }} {{ currency }}</td></tr>
            <tr><th>Interest (if applicable)</th><td>${{ interest_amount }} {{ currency }}</td></tr>
            <tr><th>Filing Fees</th><td>$50.00 USD (estimated)</td></tr>
            <tr><th>Service of Process</th><td>$30.00 USD (estimated)</td></tr>
            {% if additional_costs %}
            <tr><th>Additional Costs</th><td>${{ additional_costs }} {{ currency }}</td></tr>
            {% endif %}
            <tr><th><strong>Total Claim Amount</strong></th><td><strong>${{ total_amount }} {{ currency }}</strong></td></tr>
        </table>
    
        <h2>PART 5: WITNESS INFORMATION</h2>
    
        {% if witnesses %}
        <table>
            <thead>
                <tr><th>Name</th><th>Contact</th><th>Relevance</th></tr>
            </thead>
            <tbody>
                {% for witness in witnesses %}
                <tr>
                    <td>{{ witness.name }}</td>
                    <td>{{ witness.contact }}</td>
                    <td>{{ witness.relevance }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p><em>No witness information available at this time.</em></p>
        {% endif %}
    
        <h2>PART 6: COURT FORMS & FILING INSTRUCTIONS</h2>
    
        <div class="forms-section">
            <h3>6.1 Required Forms</h3>
            <ol>
                <li><strong>Plaintiff's Claim and Information Sheet</strong> - Main filing form</li>
                <li><strong>Summons</strong> - To be issued by the court</li>
                <li><strong>Proof of Service</strong> - After serving the defendant</li>
                <li><strong>Witness List</strong> - List of witnesses you plan to call</li>
                <li><strong>Exhibit List</strong> - List of evidence documents</li>
            </ol>
    
            <h3>6.2 Filing Steps</h3>
            <ol>
                <li>Complete all forms with information from this packet</li>
                <li>File at the appropriate small claims court in {{ jurisdiction }}</li>
                <li>Pay the filing fee (approximately $50-$100)</li>
                <li>Observe the statute of limitations: {{ statute_of_limitations }}</li>
                <li>Serve the defendant with summons and complaint</li>
                <li>Prepare for court hearing (bring this packet and all originals)</li>
            </ol>
    
            <h3>6.3 What to Bring to Court</h3>
            <ul>
                <li>Original signed contract/agreement</li>
                <li>Copy of invoice #{{ invoice_number }}</li>
                <li>All communication records (emails, texts, letters)</li>
                <li>Payment records (if any partial payments were made)</li>
                <li>This preparation document</li>
                <li>Photo copies of all evidence for the judge and defendant</li>
            </ul>
        </div>
    
        <h2>PART 7: TIPS FOR COURT PRESENTATION</h2>
    
        <div class="tips-section">
            <ul>
                <li><strong>Be concise:</strong> Present your case clearly and without emotion</li>
                <li><strong>Stick to facts:</strong> Bring evidence to support every claim</li>
                <li><strong>Bring originals:</strong> Court requires originals, provide copies to all parties</li>
                <li><strong>Practice:</strong> Rehearse your statement before the hearing</li>
                <li><strong>Be respectful:</strong> Address the judge as "Your Honor"</li>
                <li><strong>Bring witnesses:</strong> Have them wait outside until called</li>
                <li><strong>Know your remedy:</strong> Clearly state the amount you are seeking</li>
            </ul>
        </div>
    
        <h2>PART 8: LEGAL REFERENCES</h2>
    
        <div class="legal-section">
            <p><strong>Relevant Statutes:</strong></p>
            <ul>
                <li>Small Claims Court Jurisdiction: Amounts up to $10,000 (varies by jurisdiction)</li>
                <li>Statute of Limitations for Written Contracts: Typically 4-6 years</li>
                <li>Interest Rate: State statutory rate unless contract specifies</li>
            </ul>
    
            <p><strong>Note:</strong> This document is prepared for informational purposes and does not constitute legal advice. Consider consulting with an attorney for complex cases.</p>
        </div>
    
        <div class="footer">
            <p><strong>Prepared by:</strong> Invoice Resolver AI</p>
            <p><strong>Contact for Questions:</strong> {{ support_contact }}</p>
            <p>Document generated on {{ generated_date }}</p>
        </div>
    
        <h2>PART 1: CASE SUMMARY</h2>
    
        <h3>1.1 Parties Involved</h3>
        <table>
            <tr><th>Plaintiff (You)</th><td>{user_name}</td></tr>
            <tr><th>Plaintiff Address</th><td>{user_address}</td></tr>
            <tr><th>Plaintiff Phone</th><td>{user_phone}</td></tr>
            <tr><th>Plaintiff Email</th><td>{user_email}</td></tr>
            <tr><th>Defendant</th><td>{defendant_name}</td></tr>
            <tr><th>Defendant Address</th><td>{defendant_address}</td></tr>
            {% if defendant_phone %}<tr><th>Defendant Phone</th><td>{defendant_phone}</td></tr>{% endif %}
            {% if defendant_email %}<tr><th>Defendant Email</th><td>{defendant_email}</td></tr>{% endif %}
        </table>
    
        <h3>1.2 Case Information</h3>
        <table>
            <tr><th>Amount in Dispute</th><td>${amount} {currency}</td></tr>
            <tr><th>Invoice Number</th><td>{invoice_number}</td></tr>
            <tr><th>Date of Incident</th><td>{issue_date}</td></tr>
            <tr><th>Date Invoice Became Due</th><td>{due_date}</td></tr>
            <tr><th>Days Past Due</th><td>{days_overdue}</td></tr>
            <tr><th>Jurisdiction</th><td>{jurisdiction}</td></tr>
        </table>
    
        <h3>1.3 Nature of Claim</h3>
        <p><strong>Type of Case:</strong> Breach of Contract / Debt Collection</p>
        <p><strong>Description:</strong></p>
        <div class="highlight">
            {description}
        </div>
    
        <h2>PART 2: CHRONOLOGICAL TIMELINE</h2>
    
        <table>
            <thead>
                <tr><th>Date</th><th>Event</th><th>Documentation</th></tr>
            </thead>
            <tbody>
                {% for event in timeline %}
                <tr>
                    <td>{event.date}</td>
                    <td>{event.description}</td>
                    <td>{% if event.document %}{{event.document}}{% else %}N/A{% endif %}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    
        <h2>PART 3: EVIDENCE LIST</h2>
    
        <div class="evidence-section">
            {% for evidence in evidence_list %}
            <div class="evidence-item">
                <h4>{evidence.date}: {evidence.type.title()}</h4>
                <p>{evidence.description}</p>
>               {% if evidence.amount %}<p><strong>Amount:</strong> ${evidence.amount}</p>{% endif %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
E               jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'amount'

src/pdf/templates/small_claims_form.html:231: UndefinedError

During handling of the above exception, another exception occurred:

self = <test_pdf.TestPDFGenerator object at 0x7fa8dab14e20>
small_claims_context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
tmp_path = PosixPath('/tmp/pytest-of-julien/pytest-194/test_render_small_claims_templ0')

    def test_render_small_claims_template(self, small_claims_context, tmp_path):
        """Test rendering small claims form template."""
        generator = PDFGenerator()
        output_path = tmp_path / "small_claims.pdf"
>       result = generator.render_template(
            "small_claims_form.html", small_claims_context, output_path=output_path
        )

tests/test_pdf.py:220: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <src.pdf.generator.PDFGenerator object at 0x7fa8d991b350>
template_name = 'small_claims_form.html'
context = {'additional_costs': '75.00', 'amount': '1250.00', 'currency': 'USD', 'days_overdue': '30', ...}
output_path = PosixPath('/tmp/pytest-of-julien/pytest-194/test_render_small_claims_templ0/small_claims.pdf')
kwargs = {}, template = <Template 'small_claims_form.html'>

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[bytes, Path]:
        """
        Render an HTML template with context and generate PDF.
    
        Args:
            template_name: Name of template file (e.g., 'dispute_letter.html')
            context: Dictionary of variables to inject into template
            output_path: Optional path to save PDF
            **kwargs: Additional arguments passed to generate_pdf()
    
        Returns:
            PDF bytes or Path to saved file
    
        Raises:
            FileNotFoundError: If the template file does not exist
            ValueError: If template rendering fails for other reasons (including missing variables)
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            )
        except UndefinedError as e:
>           raise ValueError(f"Missing template variable: {e}")
E           ValueError: Missing template variable: 'dict object' has no attribute 'amount'

src/pdf/generator.py:191: ValueError
=============================== warnings summary ===============================
src/core/config.py:5
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/core/config.py:5: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/models.py:32
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/models.py:32: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/api/auth.py:55
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/auth.py:55: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class UserResponse(BaseModel):

src/api/invoices.py:60
  /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/api/invoices.py:60: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class InvoiceResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_pdf.py::TestPDFGenerator::test_render_small_claims_template
=================== 1 failed, 10 passed, 4 warnings in 1.74s ===================
[0m
[0m→ [0mRead src/pdf/templates/small_claims_form.html[90m [limit=20, offset=220][0m
The test failure points to line 231 in small_claims_form.html, but my edit should have fixed that. Let me check the current state of the file and see if there is another occurrence of the problematic pattern:
It seems the small_claims_form.html still has old syntax in places. I need to re-read the entire file and rewrite it completely with proper Jinja2 syntax:
[0m→ [0mRead src/pdf/templates/small_claims_form.html
I see! The file has duplicate content - the corrected version (lines 1-175) followed by the old buggy version (lines 176-337). Let me delete the duplicate portion:
[0m
[0m← [0mEdit src/pdf/templates/small_claims_form.html
Index: /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
===================================================================
--- /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
+++ /home/julien/Desktop/Free-Wiggum-opencode/projects/invoice-resolver-ai/src/pdf/templates/small_claims_form.html
@@ -171,167 +171,6 @@
         <p><strong>Prepared by:</strong> Invoice Resolver AI</p>
         <p><strong>Contact for Questions:</strong> {{ support_contact }}</p>
         <p>Document generated on {{ generated_date }}</p>
     </div>
-
-    <h2>PART 1: CASE SUMMARY</h2>
-
-    <h3>1.1 Parties Involved</h3>
-    <table>
-        <tr><th>Plaintiff (You)</th><td>{user_name}</td></tr>
-        <tr><th>Plaintiff Address</th><td>{user_address}</td></tr>
-        <tr><th>Plaintiff Phone</th><td>{user_phone}</td></tr>
-        <tr><th>Plaintiff Email</th><td>{user_email}</td></tr>
-        <tr><th>Defendant</th><td>{defendant_name}</td></tr>
-        <tr><th>Defendant Address</th><td>{defendant_address}</td></tr>
-        {% if defendant_phone %}<tr><th>Defendant Phone</th><td>{defendant_phone}</td></tr>{% endif %}
-        {% if defendant_email %}<tr><th>Defendant Email</th><td>{defendant_email}</td></tr>{% endif %}
-    </table>
-
-    <h3>1.2 Case Information</h3>
-    <table>
-        <tr><th>Amount in Dispute</th><td>${amount} {currency}</td></tr>
-        <tr><th>Invoice Number</th><td>{invoice_number}</td></tr>
-        <tr><th>Date of Incident</th><td>{issue_date}</td></tr>
-        <tr><th>Date Invoice Became Due</th><td>{due_date}</td></tr>
-        <tr><th>Days Past Due</th><td>{days_overdue}</td></tr>
-        <tr><th>Jurisdiction</th><td>{jurisdiction}</td></tr>
-    </table>
-
-    <h3>1.3 Nature of Claim</h3>
-    <p><strong>Type of Case:</strong> Breach of Contract / Debt Collection</p>
-    <p><strong>Description:</strong></p>
-    <div class="highlight">
-        {description}
-    </div>
-
-    <h2>PART 2: CHRONOLOGICAL TIMELINE</h2>
-
-    <table>
-        <thead>
-            <tr><th>Date</th><th>Event</th><th>Documentation</th></tr>
-        </thead>
-        <tbody>
-            {% for event in timeline %}
-            <tr>
-                <td>{event.date}</td>
-                <td>{event.description}</td>
-                <td>{% if event.document %}{{event.document}}{% else %}N/A{% endif %}</td>
-            </tr>
-            {% endfor %}
-        </tbody>
-    </table>
-
-    <h2>PART 3: EVIDENCE LIST</h2>
-
-    <div class="evidence-section">
-        {% for evidence in evidence_list %}
-        <div class="evidence-item">
-            <h4>{evidence.date}: {evidence.type.title()}</h4>
-            <p>{evidence.description}</p>
-            {% if evidence.amount %}<p><strong>Amount:</strong> ${evidence.amount}</p>{% endif %}
-            <p><strong>Document/Exhibit:</strong> {evidence.document or "See attached"}</p>
-        </div>
-        {% endfor %}
-    </div>
-
-    <h2>PART 4: DAMAGES CALCULATION</h2>
-
-    <table>
-        <tr><th>Principal Amount (Invoice)</th><td>${amount} {currency}</td></tr>
-        <tr><th>Interest (if applicable)</th><td>${interest_amount} {currency}</td></tr>
-        <tr><th>Filing Fees</th><td>$50.00 USD (estimated)</td></tr>
-        <tr><th>Service of Process</th><td>$30.00 USD (estimated)</td></tr>
-        {% if additional_costs %}
-        <tr><th>Additional Costs</th><td>${additional_costs} {currency}</td></tr>
-        {% endif %}
-        <tr><th><strong>Total Claim Amount</strong></th><td><strong>${total_amount} {currency}</strong></td></tr>
-    </table>
-
-    <h2>PART 5: WITNESS INFORMATION</h2>
-
-    {% if witnesses %}
-    <table>
-        <thead>
-            <tr><th>Name</th><th>Contact</th><th>Relevance</th></tr>
-        </thead>
-        <tbody>
-            {% for witness in witnesses %}
-            <tr>
-                <td>{witness.name}</td>
-                <td>{witness.contact}</td>
-                <td>{witness.relevance}</td>
-            </tr>
-            {% endfor %}
-        </tbody>
-    </table>
-    {% else %}
-    <p><em>No witness information available at this time.</em></p>
-    {% endif %}
-
-    <h2>PART 6: COURT FORMS & FILING INSTRUCTIONS</h2>
-
-    <div class="forms-section">
-        <h3>6.1 Required Forms</h3>
-        <ol>
-            <li><strong>Plaintiff's Claim and Information Sheet</strong> - Main filing form</li>
-            <li><strong>Summons</strong> - To be issued by the court</li>
-            <li><strong>Proof of Service</strong> - After serving the defendant</li>
-            <li><strong>Witness List</strong> - List of witnesses you plan to call</li>
-            <li><strong>Exhibit List</strong> - List of evidence documents</li>
-        </ol>
-
-        <h3>6.2 Filing Steps</h3>
-        <ol>
-            <li>Complete all forms with information from this packet</li>
-            <li>File at the appropriate small claims court in {jurisdiction}</li>
-            <li>Pay the filing fee (approximately $50-$100)</li>
-            <li>Observe the statute of limitations: {statute_of_limitations}</li>
-            <li>Serve the defendant with summons and complaint</li>
-            <li>Prepare for court hearing (bring this packet and all originals)</li>
-        </ol>
-
-        <h3>6.3 What to Bring to Court</h3>
-        <ul>
-            <li>Original signed contract/agreement</li>
-            <li>Copy of invoice #{invoice_number}</li>
-            <li>All communication records (emails, texts, letters)</li>
-            <li>Payment records (if any partial payments were made)</li>
-            <li>This preparation document</li>
-            <li>Photo copies of all evidence for the judge and defendant</li>
-        </ul>
-    </div>
-
-    <h2>PART 7: TIPS FOR COURT PRESENTATION</h2>
-
-    <div class="tips-section">
-        <ul>
-            <li><strong>Be concise:</strong> Present your case clearly and without emotion</li>
-            <li><strong>Stick to facts:</strong> Bring evidence to support every claim</li>
-            <li><strong>Bring originals:</strong> Court requires originals, provide copies to all parties</li>
-            <li><strong>Practice:</strong> Rehearse your statement before the hearing</li>
-            <li><strong>Be respectful:</strong> Address the judge as "Your Honor"</li>
-            <li><strong>Bring witnesses:</strong> Have them wait outside until called</li>
-            <li><strong>Know your remedy:</strong> Clearly state the amount you are seeking</li>
-        </ul>
-    </div>
-
-    <h2>PART 8: LEGAL REFERENCES</h2>
-
-    <div class="legal-section">
-        <p><strong>Relevant Statutes:</strong></p>
-        <ul>
-            <li>Small Claims Court Jurisdiction: Amounts up to $10,000 (varies by jurisdiction)</li>
-            <li>Statute of Limitations for Written Contracts: Typically 4-6 years</li>
-            <li>Interest Rate: State statutory rate unless contract specifies</li>
-        </ul>
-
-        <p><strong>Note:</strong> This document is prepared for informational purposes and does not constitute legal advice. Consider consulting with an attorney for complex cases.</p>
-    </div>
-
-    <div class="footer">
-        <p><strong>Prepared by:</strong> Invoice Resolver AI</p>
-        <p><strong>Contact for Questions:</strong> {support_contact}</p>
-        <p>Document generated on {generated_date}</p>
-    </div>
 </body>
 </html>

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

**Completed at:** Fri Mar 20 11:22:37 PM EDT 2026
