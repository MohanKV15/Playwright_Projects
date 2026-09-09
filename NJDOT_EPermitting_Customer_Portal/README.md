# NJDOT E-Permitting Customer Portal - Playwright Automation Framework

An enterprise-grade, end-to-end test automation framework for the **New Jersey Department of Transportation (NJDOT) E-Permitting Customer Portal**, built using **Playwright (Python)** and **Pytest**.

---

## 🏛 Framework Architecture

```text
NJDOT_EPermitting_Customer_Portal/
├── conftest.py               # Session storage, parallel auth locks, self-healing login, HTML/Allure hooks
├── pytest.ini                # Pytest configuration, reporters, domain tags/markers
├── requirements.txt          # Framework dependencies
├── config.py                 # Core configuration
│
├── fixtures/                 # Fixture Dependency Injection Layer
│   ├── page_fixtures.py      # Decoupled Page Object Model fixtures
│   └── __init__.py
│
├── pages/                    # Page Object Model (POM) layer
│   ├── base_page_handler.py  # Base actions, synchronization, wait helpers
│   ├── dashboard_page.py     # Customer dashboard navigation
│   ├── login/                # Authentication page objects
│   ├── action_items/         # Customer action items management
│   ├── applications_list/    # Applications history and status tracking
│   ├── submit_application/   # Application submission workflows (Highway, Utility, Drainage, etc.)
│   └── payment_activity/     # Payment activity and processing
│
├── tests/                    # Test suite layer
│   ├── test_login.py                     # Authentication scenarios
│   ├── test_action_items.py              # Customer action item responses
│   ├── test_highway_occupancy.py         # Highway occupancy permits
│   ├── test_utility_opening.py           # Utility opening permits
│   ├── test_drainage.py                  # Drainage permit applications
│   ├── test_pre_application_meeting.py   # Pre-application meeting requests
│   ├── test_permit_history.py            # Status history verification
│   └── test_payment_activity.py          # Payment validation
│
└── utils/                    # Shared utilities
```

---

## 🧪 Test Execution Commands

### 1. Run all tests in parallel (4 workers)
```bash
pytest -n 4
```

### 2. Run specific domain suites using markers
```bash
# Smoke tests only
pytest -m smoke

# Authentication tests
pytest -m login

# Highway occupancy permits
pytest -m highway_occupancy

# Utility opening permits
pytest -m utility_opening

# Customer action items
pytest -m action_items
```

---

## 📊 Reports & Artifacts

- **HTML Report**: Written to `reports/test_report.html`.
- **Allure Report**: Results generated in `reports/allure-results`. View via:
  ```bash
  allure serve reports/allure-results
  ```
