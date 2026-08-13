import os
from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_URL = (os.getenv("BASE_URL") or os.getenv("PYTEST_BASE_URL") or "https://u-njoda.bemcorp.net").rstrip("/")
    LOGIN_URL = f"{BASE_URL}/Account/LogOutUser"
    DASHBOARD_URL = f"{BASE_URL}/Portal/Page/Index/4319AppListSearchStaffFull"
    TIMEOUT = 90000 # 90 seconds for slow staging environments
