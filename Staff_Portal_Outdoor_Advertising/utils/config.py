from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_URL = "https://u-njoda.bemcorp.net" 
    LOGIN_URL = f"{BASE_URL}/Account/LogOutUser"
    DASHBOARD_URL = f"{BASE_URL}/Portal/Page/Index/4319AppListSearchStaffFull"
    TIMEOUT = 90000 # 90 seconds for slow staging environments
