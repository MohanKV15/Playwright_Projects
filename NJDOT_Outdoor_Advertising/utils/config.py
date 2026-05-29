from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_URL = "https://u-njcp.bemcorp.net"  # Staging environment URL
    LOGIN_URL = f"{BASE_URL}/Accounts/Account/Account"
    DASHBOARD_URL = f"{BASE_URL}/Accounts/Account/Account"
    TIMEOUT = 45000  # 45 seconds for slow environments, but fails fast enough to avoid massive rerun delays
