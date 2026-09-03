# IDOT Outdoor Advertising Customer Portal Automation Suite

This project contains automated test suites for the **Illinois Department of Transportation (IDOT) Outdoor Advertising Customer Portal** built using **Playwright Python** and **pytest**.

---

## Directory Structure

```text
IDOT_ODA_Customer_Portal/
├── conftest.py               # Fixtures, conditional Playwright tracing, authentication, and reporting hooks
├── pytest.ini                # Pytest command-line options, report targets, and marker registrations
├── requirements.txt          # Python dependencies
├── utils/
│   └── config.py             # Standard Config class (URLs, timeouts, and root paths)
├── pages/                    # Page Object Model (POM) layer
│   ├── core/
│   │   └── base_page.py      # Base page with Kendo UI helpers, zoom handling, and safe actions
│   └── login/
│       ├── login_page.py
│       └── create_an_account_page.py
├── testdata/                 # Test credentials and input data
│   └── login_data.json
├── tests/                    # Automated test scenarios
│   └── login/
│       ├── test_login.py
│       └── test_create_account.py
└── reports/                  # Generated HTML, JUnit XML, Allure results, and failure artifacts
    ├── allure-results/
    ├── debug_artifacts/
    └── test_report.html
```

---

## Test Execution

### 1. Run all tests
```powershell
python -m pytest -v
```

### 2. Run Smoke tests only
```powershell
python -m pytest -m smoke -v
```

### 3. Run with parallel execution (`pytest-xdist`)
```powershell
python -m pytest -n 4 -v
```

### 4. Run in headed mode
```powershell
python -m pytest --headed -v
```

---

## Tracing and Debug Artifacts
- **Conditional Playwright Tracing**: Traces (`.zip`) are captured only upon test failure and saved to `reports/debug_artifacts/` with worker ID tags.
- **Screenshots**: Failure screenshots are automatically taken and attached to Allure and `pytest-html` reports.
- **Allure Reports**: Automatically generated in `reports/allure-report/` upon test session finish.
