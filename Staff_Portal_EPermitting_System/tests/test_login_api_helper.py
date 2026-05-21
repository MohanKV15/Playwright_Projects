import json
from utils.config import Config
from pages.login.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage
from api_validation.api_helper import ApiCaptureHelper

# Load Test Data Dynamically
with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
    test_data = json.load(f)
    valid_user = test_data["valid_users"][0] 

def test_login_api_validation(page):
    """Executes a valid login while tracking all background API responses for strict 200/302 statuses."""
    api_capture = ApiCaptureHelper(page)
    
    # 1. Start capturing network traffic
    api_capture.start()
    
    try:
        login_page = LoginPage(page)
        dashboard_page = DashboardPage(page)
    
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=valid_user["email"], password=valid_user["password"], pin="11")
        
        # Dashboard UI assertion
        dashboard_page.assert_dashboard_loaded()
        
        # 2. Halt test until all routing background APIs finish loading
        api_capture.wait_for_api_idle()
        
        # 3. Mass Verify absolutely no APIs threw a 4xx or 5xx server error during login/load
        api_capture.assert_all_responses_successful()
        
    finally:
        api_capture.stop()
