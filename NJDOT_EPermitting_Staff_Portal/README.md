# NJDOT E-Permitting Staff Portal - Playwright Automation Framework

An enterprise-grade, end-to-end test automation framework for the **New Jersey Department of Transportation (NJDOT) E-Permitting Staff Portal**, built using **Playwright (Python)** and **Pytest**.

---

## 🏛 Framework Architecture

```text
NJDOT_EPermitting_Staff_Portal/
├── conftest.py               # Enterprise session storage, parallel auth locks, self-healing login, Allure hooks
├── pytest.ini                # Pytest configuration, reporters (HTML, Allure, JUnit XML), domain markers
├── requirements.txt          # Framework dependencies (Playwright, Pytest, Xdist, Allure, Faker)
├── .gitignore                # Protects test artifacts, auth tokens, cache, and reports
│
├── fixtures/                 # Fixture Dependency Injection Layer
│   ├── page_fixtures.py      # Page Object Model fixtures & authenticated state injection
│   └── __init__.py
│
├── pages/                    # Page Object Model (POM) layer
│   ├── base_page.py          # Core actions, loader synchronization, lazy sub-component proxies
│   ├── document_page.py      # Document attachments, package generation, file uploads
│   ├── log_page.py           # Communication logs, audit entries, email modals
│   ├── login/                # Authentication page objects
│   ├── dashboard/            # Staff dashboard and navigation
│   ├── application_permit_info/ # Permit lifecycle domain POMs
│   │   ├── permit_listing_page.py
│   │   ├── applicant_information_page.py
│   │   ├── general_information_page.py
│   │   ├── inspection_page.py
│   │   ├── checklist_page.py
│   │   ├── completeness_check_page.py
│   │   ├── lot_development_page.py
│   │   ├── mt_121_page.py
│   │   └── waiver_page.py
│   └── account_management/   # Account and contact administration
│
├── tests/                    # Test suite layer
│   ├── test_applicant_information.py    # Applicant & Permittee workflow
│   ├── test_permit_listing.py           # Permit search & listing validation
│   ├── test_general_information.py      # General information updates
│   ├── test_inspection.py               # Field inspection lifecycle
│   ├── test_checklist.py                # Checklist verification
│   ├── test_lot_development.py          # Lot development scenarios
│   └── account_management/              # Admin and user scenarios
│
├── testdata/                 # Test data fixtures
│   └── login_data.json       # Credential sets
│
└── utils/                    # Shared utilities
    ├── config.py             # Environment configuration (URLs, timeouts, viewport)
    ├── kendo_controls.py     # Kendo UI automation drivers
    └── logger.py             # Structured logging utility
```

---

## 🚀 Key Design Patterns & Highlights

1. **Decoupled Fixture Architecture (`fixtures/page_fixtures.py`)**:
   - Page fixtures are injected via Pytest dependency injection, eliminating repetitive manual page instantiation inside tests.
2. **Lazy Evaluated BasePage Sub-Components**:
   - `DocumentPage` and `LogPage` are lazily instantiated on first access rather than eagerly constructed on every single page object, preventing unnecessary DOM querying.
3. **Executive Allure Step Contexts**:
   - All tests leverage `with allure.step(...)` context managers, providing clear timeline breakdowns and failure trace attachments in Allure reports.
4. **Self-Healing Session Management**:
   - `conftest.py` monitors for session expiration or logout redirects and automatically re-authenticates on the fly, keeping tests 100% resilient.

---

## 🧪 Test Execution Commands

### 1. Run all tests in parallel (4 workers)
```bash
pytest -n 4
```

### 2. Run in Headed mode
```bash
pytest --headed
```

### 3. Run specific test suites using domain markers
```bash
# Smoke tests only
pytest -m smoke

# Applicant & Permittee workflow only
pytest -m applicant_information

# Permit search and listing
pytest -m permit_listing

# Inspection tests
pytest -m inspection

# Document workflows
pytest -m document
```

---

## 📊 Reports & Artifacts

- **HTML Report**: Automatically generated at `reports/test_report.html`.
- **Allure Report**: Results generated in `reports/allure-results`. View via:
  ```bash
  allure serve reports/allure-results
  ```
- **Playwright Traces**: Stored on failure in `reports/debug_artifacts/`. View via:
  ```bash
  playwright show-trace reports/debug_artifacts/<trace_file>.zip
  ```
