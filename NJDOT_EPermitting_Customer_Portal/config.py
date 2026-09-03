import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

BASE_HOST = (os.getenv("BASE_URL") or os.getenv("PYTEST_BASE_URL") or "https://u-njhtcp.bemcorp.net").rstrip("/")
BASE_URL = f"{BASE_HOST}/Accounts/Account/Account"
DASHBOARD_URL = f"{BASE_HOST}/Portal/Page/Index/4321CustomerPortalDashboardFull"
DEFAULT_TIMEOUT = 10000

