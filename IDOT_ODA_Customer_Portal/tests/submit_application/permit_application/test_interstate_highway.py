import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.interstate_highway_page import (
    InterstateHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import (
    PaymentPage,
)
from IDOT_ODA_Customer_Portal.testdata.primary_highway_data import (
    generate_primary_highway_test_data,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Permit Application")
@allure.story("Business Area Sign - Interstate Highway")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application
@pytest.mark.regression
def test_submit_interstate_highway_permit_application(
    login_page: LoginPage,
    interstate_highway_page: InterstateHighwayPage,
    payment_page: PaymentPage,
):
    """
    Test Case ID: TC_PERMIT_IH_001
    Verifies end-to-end permit application submission for Business Area Sign - Interstate Highway:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Submit Application -> Permit Application -> Business Area Sign - Interstate.
    3. Fills Sign Information selecting 1st option in all dropdowns.
    4. Fills Location Information (District, County, Route, Municipality, Zoning classification on).
    5. Fills Property Owner Information using dynamic Faker data.
    6. Attaches dummy PDF proof of property.
    7. Signs acknowledgment and disclosure.
    8. Submits form, clicks OK on confirmation modal.
    9. Fills Payment Gateway credit card details and proceeds to review.
    10. Submits payment, clicks No on survey popup modal, and clicks Return Home to Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    test_data = generate_primary_highway_test_data()

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Interstate Highway Application Form"):
        interstate_highway_page.navigate_to_interstate_highway_application()

    with allure.step("3. Fill Sign Information (first dropdown options)"):
        interstate_highway_page.fill_sign_information(test_data)

    with allure.step("4. Fill Location Information (District, County, Route, Zoning classification on)"):
        interstate_highway_page.fill_location_information(test_data)

    with allure.step("5. Fill Property Owner Information with Faker data"):
        interstate_highway_page.fill_property_owner_information(test_data)

    with allure.step("6. Upload Proof of Property dummy PDF attachment"):
        interstate_highway_page.upload_proof_of_property()

    with allure.step("7. Fill Acknowledgment & Signature details"):
        interstate_highway_page.fill_acknowledgment_and_signature(test_data)

    with allure.step("8. Submit application and confirm 1st page modal (click OK)"):
        interstate_highway_page.submit_application().confirm_submission_modal()

    with allure.step("9. Fill Payment Gateway card details and click Next Step"):
        payment_page.wait_for_payment_gateway()
        payment_page.fill_card_details()
        payment_page.click_next_step()

    with allure.step("10. Submit payment, click No on survey modal, and click Return Home"):
        payment_page.submit_payment()
        payment_page.handle_survey_modal(respond=False)
        payment_page.click_return_home()
