import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.name_change.name_change_page import (
    NameChangePage,
)
from IDOT_ODA_Customer_Portal.testdata import generate_name_change_test_data
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Name Change")
@allure.story("Name Change Application Submission and Return Home")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application
@pytest.mark.regression
def test_submit_name_change_application(
    login_page: LoginPage,
    name_change_page: NameChangePage,
):
    """
    Test Case ID: TC_NAME_CHANGE_001
    Verifies end-to-end name change application workflow:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Submit Application -> Name Change.
    3. Asserts heading and form sections (partial-form, Application Details, Signature).
    4. Fills New Company Name (#NewName) with dynamic Faker data.
    5. Checks certification checkbox (.k-checkbox-label).
    6. Fills Signer Name (#SignName) and Title (#SignTitle) with dynamic Faker data.
    7. Submits application (' Submit').
    8. Confirms 'Operation Completed' modal dialog (clicks 'OK').
    9. Dismisses survey prompt modal (clicks 'No').
    10. Verifies success message and clicks ' Return Home' back to Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    test_data = generate_name_change_test_data()

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Name Change Application Form"):
        name_change_page.navigate_to_name_change()

    with allure.step("3. Verify form sections are displayed"):
        name_change_page.verify_form_sections()

    with allure.step("4. Fill New Company Name with dynamic Faker data"):
        name_change_page.fill_new_company_name(test_data["new_name"])

    with allure.step("5. Check Signature certification checkbox and fill Signer details"):
        name_change_page.check_signature_certification()
        name_change_page.fill_signature(name=test_data["signer_name"], title=test_data["signer_title"])

    with allure.step("6. Submit Name Change application"):
        name_change_page.submit_application()

    with allure.step("7. Confirm 'Operation Completed' modal dialog"):
        name_change_page.confirm_operation_completed_modal()

    with allure.step("8. Dismiss survey modal by clicking 'No'"):
        name_change_page.dismiss_survey_modal()

    with allure.step("9. Click Return Home and verify navigation back to Dashboard"):
        name_change_page.click_return_home()

