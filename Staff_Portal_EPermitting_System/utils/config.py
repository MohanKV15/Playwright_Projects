from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    BASE_URL = "https://u-njhtsp.bemcorp.net" 
    LOGIN_URL = f"{BASE_URL}/Account/LogOutUser"
    DASHBOARD_URL = f"{BASE_URL}/Home/Dashboard?MenuName=Dashboard"
    TIMEOUT = 60000 # 60 seconds for slow staging environments
