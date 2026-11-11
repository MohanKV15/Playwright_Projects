import allure
import pytest
from pages.login.login_page import LoginPage
from utils.data_reader import DataReader
from utils.config import Config

LOGIN_DATA_FILE = Config.TESTDATA_DIR / "login_data.json"
LOGIN_DATA = DataReader.load_json(LOGIN_DATA_FILE)


@allure.epic("NCDOT ROW Portal")
@allure.feature("Authentication")
@allure.story("TC_NCDOT_LOG_001 - Valid Login Workflow")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.login
@pytest.mark.smoke
def test_valid_login(login_page: LoginPage):
    """
    Test Case ID: TC_NCDOT_LOG_001
    Verifies that a registered user can log in with valid credentials,
    submits security PIN/OTP (spinbutton), and lands on the ROW dashboard.
    """
    valid = LOGIN_DATA["valid_credentials"]

    with allure.step("1. Navigate to NCDOT Login page"):
        login_page.navigate_to_login()

    with allure.step("2. Verify login form input elements"):
        login_page.verify_login_page_elements()

    with allure.step(f"3. Fill Email ({valid['email']}) and Password"):
        login_page.fill_email(valid["email"])
        login_page.fill_password(valid["password"])

    with allure.step("4. Click Login button"):
        login_page.click_login()

    with allure.step(f"5. Enter Security PIN ({valid['pin']}) if prompted"):
        login_page.fill_pin_if_prompted(pin=valid.get("pin", "11"))

    with allure.step("6. Assert 'ROW' landing text is visible on the dashboard"):
        login_page.verify_successful_login()


@allure.epic("NCDOT ROW Portal")
@allure.feature("Authentication")
@allure.story("TC_NCDOT_LOG_002 - Invalid Credentials Validation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.login
@pytest.mark.regression
def test_invalid_login(login_page: LoginPage):
    """
    Test Case ID: TC_NCDOT_LOG_002
    Verifies that submitting invalid credentials fails authentication cleanly
    and displays an appropriate error alert modal.
    """
    data = LOGIN_DATA["invalid_credentials"]

    with allure.step("1. Navigate to NCDOT Login page"):
        login_page.navigate_to_login()

    with allure.step(f"2. Fill invalid credentials ({data['email']})"):
        login_page.fill_email(data["email"])
        login_page.fill_password(data["password"])
        login_page.click_login()

    with allure.step("3. Verify error notification appears and dismiss it"):
        login_page.verify_invalid_login_popup(expected_text=data.get("expected_error"))
        login_page.dismiss_error_modal()


@allure.epic("NCDOT ROW Portal")
@allure.feature("Authentication")
@allure.story("TC_NCDOT_LOG_003 - Empty Credentials Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.login
@pytest.mark.regression
def test_empty_credentials(login_page: LoginPage):
    """
    Test Case ID: TC_NCDOT_LOG_003
    Verifies that submitting empty credentials does not navigate away
    and enforces required input field validation.
    """
    with allure.step("1. Navigate to NCDOT Login page"):
        login_page.navigate_to_login()

    with allure.step("2. Click login with blank fields"):
        login_page.fill_email("")
        login_page.fill_password("")
        login_page.click_login()

    with allure.step("3. Assert page remains on Login and shows validation states"):
        login_page.verify_empty_field_validations()
