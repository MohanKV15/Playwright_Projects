import pytest
from playwright.sync_api import expect
from IDOT_ODA_Staff_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Staff_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Staff_Portal.utils.data_reader import DataReader
from IDOT_ODA_Staff_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@pytest.mark.login
@pytest.mark.smoke
def test_valid_login(login_page: LoginPage, dashboard_page: DashboardPage):
    """
    Test Case ID: TC_STAFF_LOG_001
    Verifies valid authentication and logout in IDOT Outdoor Advertising Staff Portal:
    1. Enters Security PIN ("11") into spinbutton
    2. Enters Valid Email and Password
    3. Clicks Login
    4. Asserts Staff Dashboard branding ("**TEST** Outdoor Advertising")
    5. Clicks Logout link and confirms modal dialog
    6. Verifies redirection back to Login page
    """
    valid_data = LOGIN_DATA["valid_credentials"]

    # 1. Navigate to portal login page
    login_page.navigate_to_login()

    # 2. Verify page branding
    login_page.verify_login_page_elements()

    # 3. Perform login with PIN, Email, and Password
    login_page.login(
        email=valid_data["email"],
        password=valid_data["password"],
        pin=valid_data.get("pin", "11"),
    )

    # 4. Verify dashboard loaded
    dashboard_page.verify_dashboard_loaded()

    # 5. Logout and verify redirection back to Login page
    dashboard_page.logout()
    login_page.verify_login_page_elements()


@pytest.mark.login
@pytest.mark.regression
def test_invalid_email_and_password(login_page: LoginPage):
    """
    Test Case ID: TC_STAFF_LOG_002
    Verifies alert popup when entering dummy Invalid Email and Invalid Password ('testttt' / 'esttt').
    """
    data = LOGIN_DATA["invalid_email_and_password"]

    # 1. Navigate to login page
    login_page.navigate_to_login()

    # 2. Enter invalid credentials and submit
    login_page.login(
        email=data["email"],
        password=data["password"],
        pin=data.get("pin", "11"),
    )

    # 3. Verify 'You have entered an invalid' alert popup
    login_page.verify_invalid_login_popup()

    # 4. Dismiss modal by clicking OK
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_valid_email_invalid_password(login_page: LoginPage):
    """
    Test Case ID: TC_STAFF_LOG_003
    Verifies alert popup when entering Valid Email and Invalid Password.
    """
    data = LOGIN_DATA["valid_email_invalid_password"]

    # 1. Navigate to login page
    login_page.navigate_to_login()

    # 2. Enter valid email and invalid password
    login_page.login(
        email=data["email"],
        password=data["password"],
        pin=data.get("pin", "11"),
    )

    # 3. Verify 'You have entered an invalid' alert popup
    login_page.verify_invalid_login_popup()

    # 4. Dismiss modal by clicking OK
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_invalid_email_valid_password(login_page: LoginPage):
    """
    Test Case ID: TC_STAFF_LOG_004
    Verifies alert popup when entering Invalid Email and Valid Password.
    """
    data = LOGIN_DATA["invalid_email_valid_password"]

    # 1. Navigate to login page
    login_page.navigate_to_login()

    # 2. Enter invalid email and valid password
    login_page.login(
        email=data["email"],
        password=data["password"],
        pin=data.get("pin", "11"),
    )

    # 3. Verify 'You have entered an invalid' alert popup
    login_page.verify_invalid_login_popup()

    # 4. Dismiss modal by clicking OK
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_empty_credentials(login_page: LoginPage):
    """
    Test Case ID: TC_STAFF_LOG_005
    Verifies submission behavior with empty email and empty password.
    """
    data = LOGIN_DATA["empty_credentials"]

    # 1. Navigate to login page
    login_page.navigate_to_login()

    # 2. Submit empty credentials
    login_page.login(
        email=data["email"],
        password=data["password"],
        pin=data.get("pin", "11"),
    )

    # 3. Assert user remains on login page
    assert login_page.is_at_login_page(), "Expected browser to remain on login page when submitting empty credentials"
