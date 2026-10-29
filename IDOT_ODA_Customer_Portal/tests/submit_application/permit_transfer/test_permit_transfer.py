import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_transfer.permit_transfer_page import (
    PermitTransferPage,
)
from IDOT_ODA_Customer_Portal.testdata import (
    generate_permit_transfer_test_data,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Permit Transfer")
@allure.story("Permit Transfer Application Submission and Return Home")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application
@pytest.mark.regression
def test_submit_permit_transfer_application(
    login_page: LoginPage,
    permit_transfer_page: PermitTransferPage,
):
    """
    Test Case ID: TC_PERMIT_TRANSFER_001
    Verifies end-to-end permit transfer application workflow:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Submit Application -> Permit Transfer.
    3. Asserts all form sections are visible (Applicant Info, Application Info, Acknowledgment, Signature).
    4. Fills Application Information (Permit Number to Transfer, From Company) with dynamic Faker data.
    5. Uploads From Company Approval letter (dummy PDF).
    6. Checks Acknowledgment & Disclosure, and fills Signer Name & Title with dynamic Faker data.
    7. Submits application.
    8. Clicks OK on confirmation modal ('Record saved successfully').
    9. Clicks Return Home and verifies return back to Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    test_data = generate_permit_transfer_test_data()

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Permit Transfer Application Form"):
        permit_transfer_page.navigate_to_permit_transfer()

    with allure.step("3. Verify form sections are displayed"):
        permit_transfer_page.verify_form_sections()

    with allure.step("4. Fill Application Information (Permit Number, From Company) with Faker data"):
        permit_transfer_page.fill_application_information(test_data)

    with allure.step("5. Upload From Company Approval letter (dummy PDF)"):
        permit_transfer_page.upload_approval_letter()

    with allure.step("6. Fill Acknowledgment & Signature details with Faker data"):
        permit_transfer_page.fill_acknowledgment_and_signature(test_data)

    with allure.step("7. Submit Permit Transfer application"):
        permit_transfer_page.submit_application()

    with allure.step("8. Confirm submission modal (click OK)"):
        permit_transfer_page.confirm_submission_modal()

    with allure.step("9. Click Return Home and verify navigation back to Dashboard"):
        permit_transfer_page.click_return_home()

