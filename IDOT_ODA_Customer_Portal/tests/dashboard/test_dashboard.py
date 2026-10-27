import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Dashboard")
@allure.story("Dashboard Cards Verification and Logout Flow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.dashboard
@pytest.mark.smoke
@pytest.mark.regression
def test_dashboard_cards_and_logout(login_page: LoginPage, dashboard_page: DashboardPage):
    """
    Test Case ID: TC_DASH_001
    Verifies that after user logs in with valid credentials:
    1. User can see all 4 primary dashboard action cards:
       - Submit an Application
       - Action Items
       - Application History
       - Payment Activity
    2. User clicks 'Logout' and verifies redirection back to the Login page.
    """
    valid_data = LOGIN_DATA["valid_credentials"]

    with allure.step("1. Navigate to customer portal login page"):
        login_page.navigate_to_login()

    with allure.step("2. Perform login with valid email and password"):
        login_page.login(email=valid_data["email"], password=valid_data["password"])

    with allure.step("3. Fill PIN if prompted"):
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("4. Verify all 4 dashboard action cards are visible"):
        dashboard_page.verify_dashboard_cards()

    with allure.step("5. Click Logout"):
        dashboard_page.click_logout()

    with allure.step("6. Verify redirection to Login page"):
        dashboard_page.verify_redirect_to_login()
