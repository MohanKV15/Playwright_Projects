# NCDOT ROW Portal - Test Automation Framework

Enterprise Test Automation Framework for the North Carolina Department of Transportation (**NCDOT**) Right of Way (**ROW**) Customer Portal, developed using **Playwright (Python)** and **Pytest**.

---

## 1. Architecture & Design Principles

The framework mirrors the robust Page Object Model (POM) and Component Object Model architecture implemented in `IDOT_ODA_Customer_Portal`:

- **Page Object Model (POM):** Decouples test specifications from UI locators and DOM interactions.
- **Component Object Model (Kendo UI):** Centralizes all Telerik/Kendo controls (`KendoDropdown`, `KendoDatePicker`, `KendoNumericTextBox`, `KendoCheckbox`, `KendoDialog`) into `pages/core/kendo_controls.py`.
- **Dynamic Test Data:** Dynamic data generation using `Faker` alongside standardized baseline JSON data in `testdata/login_data.json`.
- **Session Auth Reuse:** Session authentication caching via `.auth/` storage states with file locks for parallel test execution.
- **Diagnostics & Reporting:** Automatic full-page failure screenshot and Playwright trace capture with Allure report integration.

---

## 2. Project Structure

```
NCDOT/
├── .auth/                        # Preserved browser session states & locks
├── .env                          # Local environment settings
├── .env.example                  # Template environment variables
├── pytest.ini                    # Pytest configuration with allure, markers, addopts
├── requirements.txt              # Standardized dependencies
├── README.md                     # Framework documentation & run guide
├── conftest.py                   # Master session & browser context fixture, allure auto-report, failure hooks
├── utils/
│   ├── config.py                 # Centralized configuration (URLs, timeouts, zoom, credentials)
│   ├── logger.py                 # Formatted console & file logger
│   └── data_reader.py            # JSON/CSV test data reader
├── fixtures/
│   └── page_fixtures.py          # Pytest fixtures for Page Objects (login_page, dashboard_page)
├── pages/
│   ├── core/
│   │   ├── base_page.py          # Universal base page (navigation, zoom, loaders, alerts, validation helpers)
│   │   └── kendo_controls.py     # Component objects (KendoDropdown, KendoDatePicker, KendoNumericTextBox, etc.)
│   ├── login/
│   │   └── login_page.py         # NCDOT LoginPage POM (Email, Password, Login button, PIN, ROW validation)
│   └── dashboard/
│       └── dashboard_page.py     # NCDOT Dashboard/Landing POM ("ROW" verification, navigation)
├── testdata/
│   ├── login_data.json           # Valid, invalid email, invalid password, empty data sets
│   └── test_data_factory.py      # Dynamic data generator with Faker
└── tests/
    └── login/
        └── test_login.py         # Full test suite (Valid, Invalid Password, Invalid Email, Empty, etc.)
```

---

## 3. Getting Started

### Prerequisites
- Python 3.10+
- Allure CLI (optional for manual report serving)

### Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 4. Test Execution

### Run all login tests (Headed)
```bash
pytest tests/login/test_login.py -v -s --headed
```

### Run by Pytest Marker
```bash
pytest -m smoke -v
pytest -m login -v
pytest -m regression -v
```

### Run in Parallel (Multi-worker)
```bash
pytest tests/ -n auto -v
```

---

## 5. Allure Reporting

Allure reports are automatically generated at `reports/allure-report/index.html` after test runs.

To view interactively:
```bash
allure serve reports/allure-results
```

