import os
from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_URL = (os.getenv("BASE_URL") or os.getenv("PYTEST_BASE_URL") or "https://u-njcp.bemcorp.net").rstrip("/")
    LOGIN_URL = f"{BASE_URL}/Accounts/Account/Account"
    DASHBOARD_URL = f"{BASE_URL}/Accounts/Account/Account"
    TIMEOUT = 45000  # 45 seconds for slow environments, but fails fast enough to avoid massive rerun delays
