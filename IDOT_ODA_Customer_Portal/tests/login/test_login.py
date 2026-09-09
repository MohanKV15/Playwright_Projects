import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Authentication")
@allure.story("Valid Login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.login
@pytest.mark.smoke
def test_valid_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_001
    Verifies login with valid credentials.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    
    with allure.step("1. Navigate to customer portal login page"):
        login_page.navigate_to_login()
    
    with allure.step("2. Verify page branding & welcome text"):
        login_page.verify_login_page_elements()
    
    with allure.step("3. Perform login with valid email and password"):
        login_page.login(email=valid_data["email"], password=valid_data["password"])
    
    with allure.step("4. Fill PIN if prompted"):
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))


@allure.epic("Customer Portal")
@allure.feature("Authentication")
@allure.story("Invalid Password")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.login
@pytest.mark.regression
def test_invalid_password(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_002
    Verifies error alert and modal dismiss when entering Valid Email & Invalid Password.
    """
    data = LOGIN_DATA["valid_email_invalid_password"]
    
    with allure.step("1. Navigate to login page"):
        login_page.navigate_to_login()
    
    with allure.step("2. Submit valid email and invalid password"):
        login_page.login(email=data["email"], password=data["password"])
    
    with allure.step("3. Verify and dismiss error popup"):
        login_page.verify_invalid_login_popup()
        login_page.dismiss_error_modal()


@allure.epic("Customer Portal")
@allure.feature("Authentication")
@allure.story("Invalid Email")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.login
@pytest.mark.regression
def test_invalid_email(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_003
    Verifies error alert and modal dismiss when entering Invalid Email & Valid Password.
    """
    data = LOGIN_DATA["invalid_email_valid_password"]
    
    with allure.step("1. Navigate to login page"):
        login_page.navigate_to_login()
    
    with allure.step("2. Submit invalid email and valid password"):
        login_page.login(email=data["email"], password=data["password"])
    
    with allure.step("3. Verify and dismiss error popup"):
        login_page.verify_invalid_login_popup()
        login_page.dismiss_error_modal()


@allure.epic("Customer Portal")
@allure.feature("Authentication")
@allure.story("Invalid Credentials")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.login
@pytest.mark.regression
def test_invalid_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_004
    Verifies error alert when entering Invalid Email & Invalid Password.
    """
    data = LOGIN_DATA["invalid_login"]
    
    with allure.step("1. Navigate to login page"):
        login_page.navigate_to_login()
    
    with allure.step("2. Submit invalid credentials"):
        login_page.login(email=data["email"], password=data["password"])
    
    with allure.step("3. Verify and dismiss error popup"):
        login_page.verify_invalid_login_popup()
        login_page.dismiss_error_modal()


@allure.epic("Customer Portal")
@allure.feature("Authentication")
@allure.story("Empty Credentials")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.login
@pytest.mark.regression
def test_empty_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_005
    Verifies behavior when submitting Empty Email & Empty Password.
    """
    data = LOGIN_DATA["empty_login"]
    
    with allure.step("1. Navigate to login page"):
        login_page.navigate_to_login()
    
    with allure.step("2. Submit empty credentials"):
        login_page.login(email=data["email"], password=data["password"])
    
    with allure.step("3. Assert page remains on Login page or shows validation error"):
        assert "Accounts/Account" in login_page.page.url or login_page.email_input.is_visible()

