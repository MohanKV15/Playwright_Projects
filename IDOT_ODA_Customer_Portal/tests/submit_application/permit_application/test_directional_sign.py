import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.directional_sign_page import (
    DirectionalSignPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import (
    PaymentPage,
)
from IDOT_ODA_Customer_Portal.testdata import (
    generate_directional_sign_test_data,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Permit Application")
@allure.story("Directional Sign, Official Sign or Official Notice")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application
@pytest.mark.regression
def test_submit_directional_sign_permit_application(
    login_page: LoginPage,
    directional_sign_page: DirectionalSignPage,
    payment_page: PaymentPage,
):
    """
    Test Case ID: TC_PERMIT_DS_001
    Verifies end-to-end permit application submission for Directional Sign, Official Sign or Official Notice:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Submit Application -> Permit Application -> Directional Sign, Official.
    3. Fills Sign Information (selects Directional sign type, 1st option in dropdowns, dimensions).
    4. Fills Location Information (District, County, Route, 1st option travel direction, distances, landmarks).
    5. Fills Property Owner Information using dynamic Faker data.
    6. Attaches dummy PDF proof of property.
    7. Signs acknowledgment and disclosure.
    8. Submits form, clicks OK on confirmation modal.
    9. Fills Payment Gateway credit card details and proceeds to review.
    10. Submits payment, clicks No on survey popup modal, and clicks Return Home to Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    test_data = generate_directional_sign_test_data()

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Directional Sign Application Form"):
        directional_sign_page.navigate_to_directional_sign_application()

    with allure.step("3. Fill Sign Information (Directional sign type, first dropdown options, dimensions)"):
        directional_sign_page.fill_sign_information(test_data)

    with allure.step("4. Fill Location Information (District, County, Route, 1st option travel direction, landmarks)"):
        directional_sign_page.fill_location_information(test_data)

    with allure.step("5. Fill Property Owner Information with Faker data"):
        directional_sign_page.fill_property_owner_information(test_data)

    with allure.step("6. Upload Proof of Property dummy PDF attachment"):
        directional_sign_page.upload_proof_of_property()

    with allure.step("7. Fill Acknowledgment & Signature details"):
        directional_sign_page.fill_acknowledgment_and_signature(test_data)

    with allure.step("8. Submit application and confirm 1st page modal (click OK)"):
        directional_sign_page.submit_application().confirm_submission_modal()

    with allure.step("9. Process Payment Gateway (if fee required) or verify Success Page"):
        if "casuccesspagefull" not in payment_page.page.url.lower():
            payment_page.wait_for_payment_gateway()
            payment_page.fill_card_details()
            payment_page.click_next_step()
            payment_page.submit_payment()

    with allure.step("10. Dismiss survey modal and Return Home to Dashboard"):
        payment_page.handle_survey_modal(respond=False)
        payment_page.click_return_home()
