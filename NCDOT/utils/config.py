import os
from pathlib import Path


class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DOWNLOADS_DIR = PROJECT_ROOT / "downloads"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    AUTH_DIR = PROJECT_ROOT / ".auth"
    TESTDATA_DIR = PROJECT_ROOT / "testdata"

    BASE_HOST = (os.getenv("BASE_URL") or os.getenv("NCDOT_BASE_URL") or "https://u-ncdot.bemcorp.net").rstrip("/")
    BASE_URL = BASE_HOST
    LOGIN_URL = f"{BASE_HOST}/Home/AccountEntra"
    DASHBOARD_URL = f"{BASE_HOST}/Portal/Page/Index/ProjectListingAndFilters"
    PROJECTS_URL = f"{BASE_HOST}/Portal/Page/Index/ProjectListingAndFilters"

    # Default Credentials
    DEFAULT_USER = os.getenv("NCDOT_USER", "sprabhu@bemsys.com")
    DEFAULT_PASSWORD = os.getenv("NCDOT_PASSWORD", "Security@#")
    DEFAULT_PIN = os.getenv("NCDOT_PIN", "11")

    # Timeouts & Viewport Settings
    TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "45000"))
    ZOOM_PERCENT = int(os.getenv("ZOOM_PERCENT", "67"))

