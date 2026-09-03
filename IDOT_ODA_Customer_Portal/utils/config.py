import os
from pathlib import Path


class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_HOST = (os.getenv("BASE_URL") or os.getenv("IDOT_BASE_URL") or "https://u-idcp.bemcorp.net").rstrip("/")
    BASE_URL = BASE_HOST
    LOGIN_URL = f"{BASE_HOST}/Accounts/Account/Account"
    DASHBOARD_URL = f"{BASE_HOST}/Portal/Page/Index/4321CustomerPortalDashboardFull"
    TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))
    ZOOM_PERCENT = 67
