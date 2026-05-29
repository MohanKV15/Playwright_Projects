# NJDOT Outdoor Advertising Test Automation

This project contains a professional Page Object Model (POM) test automation suite built with Python, Playwright, and `pytest`.

## Project Structure

```text
NJDOT_Outdoor_Advertising/
├── .auth/                        # Saved browser context storage state (session json)
├── pages/                        # Page Object Model definition files
│   ├── base_page.py              # BasePage wrapping core locator & browser interactions
│   └── login/
│       └── login_page.py         # LoginPage for NJDOT authentication
├── tests/                        # Automated test scripts
│   └── test_login.py             # Verify pages logic and structure works
├── utils/                        # Core configuration and settings
│   └── config.py                 # URL and timeout settings
├── testdata/                     # Local test inputs and configuration
│   └── login_data.json           # Template credentials structure
├── conftest.py                   # Pytest hooks, fixtures (auto-zoom, browser setup, parallel auth)
├── pytest.ini                    # Core command-line configurations
└── requirements.txt              # Project packages list
```

## Setup Instructions

1. **Install Dependencies**:
   Install required python dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install
   ```

3. **Configure User Credentials**:
   Adjust `testdata/login_data.json` to configure the credentials for standard execution.

## Execution

- **Run all tests**:
  ```bash
  pytest
  ```

- **Run in parallel using xdist** (e.g. 3 threads):
  ```bash
  pytest -n 3
  ```

- **Collect tests without execution**:
  ```bash
  pytest --collect-only
  ```
