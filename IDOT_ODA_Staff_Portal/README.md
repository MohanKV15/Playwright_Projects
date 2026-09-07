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
│   └── add_paper_application/
│       ├── primary_highway_page.py          # Primary Highway workflow, company modal, form fill, submission
│       ├── interstate_highway_page.py       # Interstate Highway workflow (inherits PrimaryHighwayPage)
│       ├── advertising_registration_page.py # Advertising Registration workflow (inherits PrimaryHighwayPage)
│       └── __init__.py
│
├── tests/                    # Test suite layer
│   ├── login/
│   │   └── test_login.py                    # 5 comprehensive login & authentication test scenarios
│   ├── dashboard/
│   │   └── test_dashboard.py                # Full dashboard navigation, dynamic status search & detail verification
│   └── add_paper_application/
│       ├── test_primary_highway.py          # Primary Highway creation & validation (with Faker test data)
│       ├── test_interstate_highway.py       # Interstate Highway creation & validation
│       └── test_advertising_registration.py # Advertising Registration creation & validation
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

1. **Modular Kendo Component Abstraction (`pages/core/kendo_controls.py`)**:
   - Encapsulates Kendo UI widgets (`KendoDropdown`, `KendoDatePicker`, `KendoNumericTextBox`).
   - Supports polymorphic dropdown selection via either element ID (using Kendo internal JS API) or Playwright `Locator` (UI listbox traversal).
2. **Resilient Concurrency & Session Reuse (`conftest.py`)**:
   - Employs atomic file locks (`login.lock`) across parallel `pytest-xdist` workers.
   - Built-in 60-second stale-lock auto-clearing eliminates deadlocks on worker timeouts or unexpected termination.
   - Self-healing re-authentication automatically recovers expired sessions without test failure.
3. **Automated Screen Zooming (67% Sweet Spot)**:
   - Configured via autouse fixture `configure_zoom` evaluating on browser context creation before page script execution, preventing UI layout distortions.
4. **Adaptive UI Synchronization**:
   - `_wait_for_loader()` automatically dismisses unexpected server error dialogs, waits for Kendo spinners, and synchronizes `.k-overlay` backdrops.
   - `safe_click()` includes automatic scroll adjustments (`window.scrollBy(0, -100)`) to prevent occlusion by sticky portal navigation headers.
5. **Dynamic Search Iteration**:
   - `DashboardPage.search_until_records_found()` iterates through application statuses dynamically until valid data is loaded in the table, preventing empty table flakiness.

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

### 3. Run specific test suites using markers
```bash
# Smoke tests only
pytest -m smoke

# Login tests only
pytest -m login

# Add Paper Application workflows only
pytest -m add_paper_application
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
