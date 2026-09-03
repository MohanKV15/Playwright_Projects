# Staff Portal: Outdoor Advertising - Automation Framework

## Overview
This repository contains the enterprise-grade Playwright automation framework for the **Outdoor Advertising Staff Portal**. 
It is designed for high-concurrency execution, maximum stability, and data-driven validations.

## 🏗️ Architecture Highlights (Enterprise Standards)

1. **Page Object Model (POM) Design**
   - Strictly separates UI locators from test logic.
   - Ensures high maintainability if the frontend UI changes.
   - Utilizes Python's `logging` module to generate human-readable CI/CD traces.

2. **Parallel State-Sharing (File Locking)**
   - When running tests with `pytest-xdist` (e.g., `-n 4`), the framework uses a highly optimized thread-safe file lock.
   - Only **one** worker physical logs into the system via the UI. It securely intercepts the Auth Cookie/Token and shares it with all other parallel workers, avoiding login rate-limiting and drastically cutting down execution time.

3. **Data-Driven Testing (DDT)**
   - Zero hardcoded credentials in the codebase.
   - Consumes dynamic datasets from `testdata/login_data.json` for rapid test parameterization (e.g., iterating through multiple valid/invalid scenarios dynamically).

4. **Self-Healing Authentication**
   - The global `authenticated_page` fixture automatically detects if a session has expired mid-test.
   - If an unauthorized state is detected, it self-heals by triggering a background re-authentication before proceeding with the test.

5. **Advanced Traceability & HTML Reporting**
   - Natively integrated with `pytest-html` to generate gorgeous, client-ready HTML reports.
   - Automatically captures **Screenshots**, **Videos**, and **Playwright Traces** strictly upon failure to save storage space while maximizing debuggability.

## 🚀 Execution Commands

**Run tests sequentially:**
```powershell
python -m pytest tests/ -v -s
```

**Run tests in parallel (e.g., 4 workers):**
```powershell
python -m pytest tests/ -n 4 -v -s
```

**Run in Slow-Mo (for client demos):**
```powershell
python -m pytest tests/ -v -s --slowmo 1500
```
