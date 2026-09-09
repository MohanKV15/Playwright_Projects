# IDOT Outdoor Advertising (ODA) Staff Portal - Playwright Automation Framework

An enterprise-grade, end-to-end test automation framework for the **Illinois Department of Transportation (IDOT) Outdoor Advertising Staff Portal**, built using **Playwright (Python)** and **Pytest**.

---

## 🏛 Framework Architecture

```text
IDOT_ODA_Staff_Portal/
├── conftest.py               # Enterprise session storage, parallel auth locks, zoom init, failure diagnostics
├── pytest.ini                # Pytest configuration, reporters (HTML, Allure, JUnit XML), custom markers
├── requirements.txt          # Framework dependencies (Playwright, Pytest, Xdist, Allure, Faker)
├── .gitignore                # Protects test artifacts, auth tokens, cache, and reports
│
├── fixtures/                 # Fixture Dependency Injection Layer
│   ├── page_fixtures.py      # Page Object Model fixtures & authenticated state injection
│   └── __init__.py
│
├── pages/                    # Page Object Model (POM) layer
│   ├── core/
│   │   ├── base_page.py      # Core actions, loader synchronization, sticky header offsets, dialog handlers
│   │   ├── kendo_controls.py # Polymorphic Kendo widgets (KendoDropdown, KendoDatePicker, KendoNumericTextBox)
│   │   └── __init__.py
│   ├── login/
│   │   ├── login_page.py     # Login page object (PIN, Email, Password, alert dismissal)
│   │   └── __init__.py
│   ├── dashboard/
│   │   ├── dashboard_page.py # Staff dashboard, ADTrak navigation, dynamic status search, permit verification
│   │   └── __init__.py
│   ├── add_paper_application/
│   │   ├── primary_highway_page.py          # Primary Highway workflow, company modal, form fill, submission
│   │   ├── interstate_highway_page.py       # Interstate Highway workflow (inherits PrimaryHighwayPage)
│   │   ├── advertising_registration_page.py # Advertising Registration workflow (inherits PrimaryHighwayPage)
│   │   ├── directional_sign_page.py         # Directional Sign workflow (inherits PrimaryHighwayPage)
│   │   └── __init__.py
│   ├── GIS_navigation/
│   │   ├── GIS_page.py       # GIS Map navigation, iframe, toolbar, and display verification
│   │   └── __init__.py
│   └── application_permit/
│       ├── application_details_page.py      # Application search & full details view
│       ├── inspection_page.py               # Inspection workflow, reports, logs & cancellations
│       ├── documents_and_log_page.py        # Reusable attachments, communication logs, email modals
│       ├── customer_action_items_page.py    # Customer Action Items listing, creation & detail verification
│       ├── review_page.py                   # Reviewer assignments, date picker, role assignments
│       ├── amendment_page.py                # Amendment / Modification Requests workflow & modal alerts
│       └── __init__.py
│
├── tests/                    # Test suite layer
│   ├── login/
│   │   └── test_login.py                    # 5 comprehensive login & authentication test scenarios
│   ├── dashboard/
│   │   └── test_dashboard.py                # Full dashboard navigation, dynamic status search & detail verification
│   ├── add_paper_application/
│   │   ├── test_primary_highway.py          # Primary Highway creation & validation (with Faker test data)
│   │   ├── test_interstate_highway.py       # Interstate Highway creation & validation
│   │   ├── test_advertising_registration.py # Advertising Registration creation & validation
│   │   └── test_directional_sign.py         # Directional Sign creation & validation
│   ├── GIS_navigation/
│   │   └── test_GIS_navigation.py           # GIS map loading, controls & coordinates
│   └── application_permit/
│       ├── test_application_details.py      # Application details inspection & saving
│       ├── test_inspection.py               # End-to-end 11-step inspection lifecycle
│       ├── test_customer_action_items.py    # Customer Action Items creation, attach, & verification
│       ├── test_review.py                   # Reviewer assignment & grid verification
│       └── test_amendment.py                # Amendment alert validation & modal dismissal
│
├── testdata/                 # Test data fixtures
│   ├── login_data.json       # Credential sets (valid, invalid, boundary cases)
│   └── dummy.pdf             # Real PDF sample for file attachment uploads
│
└── utils/                    # Framework utilities
    ├── config.py             # Environment configuration (URLs, timeouts, zoom percentages)
    ├── data_reader.py        # JSON test data loader utility
    ├── logger.py             # Structured logger with console and file handlers
    └── __init__.py
```

---

## 🚀 Key Design Patterns & Engineering Highlights

1. **Decoupled Fixture Architecture (`fixtures/page_fixtures.py`)**:
   - Eliminates monolithic `conftest.py` bloat by keeping page instantiation and authenticated state injection modular and cleanly maintainable.
2. **Modular Kendo Component Abstraction (`pages/core/kendo_controls.py`)**:
   - Encapsulates Kendo UI widgets (`KendoDropdown`, `KendoDatePicker`, `KendoNumericTextBox`).
   - Supports polymorphic dropdown selection via either element ID (using Kendo internal JS API with async retry polling) or Playwright `Locator` (UI listbox traversal).
   - Eliminates `.k-animation-container` hanging popups and UI overlay freezes.
3. **Reusable Sub-Page Composition (`DocumentsAndLogPage`)**:
   - Encapsulates common file attachments, date selection, Faker log entries, and email dialogs, plugged cleanly into `InspectionPage` and future permit tabs.
4. **Resilient Concurrency & Session Reuse (`conftest.py`)**:
   - Employs atomic file locks (`login.lock`) across parallel `pytest-xdist` workers.
   - Built-in 60-second stale-lock auto-clearing eliminates deadlocks on worker timeouts or unexpected termination.
   - Self-healing re-authentication automatically recovers expired sessions without test failure.
5. **Automated Screen Zooming (67% Sweet Spot)**:
   - Configured via autouse fixture `configure_zoom` evaluating on browser context creation before page script execution, preventing UI layout distortions.
6. **Adaptive UI Synchronization**:
   - `_wait_for_loader()` automatically dismisses unexpected server error dialogs, waits for Kendo spinners, and synchronizes `.k-overlay` backdrops.
   - `safe_click()` includes automatic scroll adjustments to prevent occlusion by sticky portal navigation headers.
7. **Dynamic Test Data Generation**:
   - All tests leverage `Faker` to generate unique names, addresses, subjects, and comments on every execution, preventing duplicate key violations and database locks.

---

## ⚙️ Installation & Setup

1. **Clone repository and navigate to portal directory**:
   ```bash
   cd IDOT_ODA_Staff_Portal
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browser binaries**:
   ```bash
   playwright install chromium
   ```

---

## 🧪 Test Execution Commands

### 1. Run all tests in parallel (4 workers)
```bash
pytest -n 4
```

### 2. Run all tests in Headed mode
```bash
pytest --headed
```

### 3. Run specific domain suites using markers
```bash
# Smoke tests only
pytest -m smoke

# Application & Permit workflows
pytest -m application_permit

# Specific permit sub-features
pytest -m inspection
pytest -m customer_action_items
pytest -m review
pytest -m amendment

# GIS Navigation workflows
pytest -m gis

# Add Paper Application workflows only
pytest -m add_paper_application

# Authentication scenarios
pytest -m login
```

### 4. Run with custom credentials via CLI
```bash
pytest --staff-email "your_email@domain.com" --staff-password "your_password" --staff-pin "11"
```

---

## 📊 Reports & Artifacts

- **HTML Report**: Automatically written to `reports/test_report.html` (self-contained with embedded failure screenshots).
- **Allure Report**: Results generated in `reports/allure-results`. View via:
  ```bash
  allure serve reports/allure-results
  ```
- **Playwright Traces**: Stored on test failure in `reports/debug_artifacts/<test_name>_<worker>.zip`. View via:
  ```bash
  playwright show-trace reports/debug_artifacts/<trace_file>.zip
  ```
