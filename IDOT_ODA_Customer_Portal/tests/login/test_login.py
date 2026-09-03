import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@pytest.mark.login
@pytest.mark.smoke
def test_valid_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_001
    Verifies login with valid credentials (Email: sprabhu@bemsys.com, Password: Security@#).
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    
    # 1. Navigate to portal login page
    login_page.navigate_to_login()
    
    # 2. Verify page branding & welcome text
    login_page.verify_login_page_elements()
    
    # 3. Perform login with valid email and password
    login_page.login(email=valid_data["email"], password=valid_data["password"])
    
    # 4. Fill PIN if spinbutton is visible
    login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))


@pytest.mark.login
@pytest.mark.regression
def test_invalid_password(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_002
    Verifies error alert and modal dismiss when entering Valid Email & Invalid Password.
    """
    data = LOGIN_DATA["valid_email_invalid_password"]
    
    # 1. Navigate to login page
    login_page.navigate_to_login()
    
    # 2. Enter valid email and invalid password, then click Login
    login_page.login(email=data["email"], password=data["password"])
    
    # 3. Assert invalid credentials popup is visible
    login_page.verify_invalid_login_popup()
    
    # 4. Click OK to dismiss error modal
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_invalid_email(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_003
    Verifies error alert and modal dismiss when entering Invalid Email & Valid Password.
    """
    data = LOGIN_DATA["invalid_email_valid_password"]
    
    # 1. Navigate to login page
    login_page.navigate_to_login()
    
    # 2. Enter invalid email and valid password, then click Login
    login_page.login(email=data["email"], password=data["password"])
    
    # 3. Assert invalid credentials popup is visible
    login_page.verify_invalid_login_popup()
    
    # 4. Click OK to dismiss error modal
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_invalid_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_004
    Verifies error alert when entering Invalid Email & Invalid Password (wrong@email.com / wrongpassword).
    """
    data = LOGIN_DATA["invalid_login"]
    
    # 1. Navigate to login page
    login_page.navigate_to_login()
    
    # 2. Enter invalid email and invalid password, then click Login
    login_page.login(email=data["email"], password=data["password"])
    
    # 3. Assert invalid credentials popup is visible
    login_page.verify_invalid_login_popup()
    
    # 4. Click OK to dismiss error modal
    login_page.dismiss_error_modal()


@pytest.mark.login
@pytest.mark.regression
def test_empty_login(login_page: LoginPage):
    """
    Test Case ID: TC_LOG_005
    Verifies behavior when submitting Empty Email & Empty Password.
    """
    data = LOGIN_DATA["empty_login"]
    
    # 1. Navigate to login page
    login_page.navigate_to_login()
    
    # 2. Submit empty credentials
    login_page.login(email=data["email"], password=data["password"])
    
    # 3. Assert page remains on Login page or shows validation error
    assert "Accounts/Account" in login_page.page.url or login_page.email_input.is_visible()
