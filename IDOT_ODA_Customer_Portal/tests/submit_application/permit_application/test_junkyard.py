import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.junkyard_page import (
    JunkyardPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import (
    PaymentPage,
)
from IDOT_ODA_Customer_Portal.testdata import (
    generate_junkyard_test_data,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Permit Application")
@allure.story("Junkyard Permit Application")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application
@pytest.mark.regression
def test_submit_junkyard_permit_application(
    login_page: LoginPage,
    junkyard_page: JunkyardPage,
    payment_page: PaymentPage,
):
    """
    Test Case ID: TC_PERMIT_JY_001
    Verifies end-to-end permit application submission for Junkyard:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Submit Application -> Permit Application -> Junkyard.
    3. Fills Yard Information (Yard Type Junkyard, Secretary of State UDL, Date Yard Established, Screening).
    4. Fills Location Information (District, County, Route, GPS Coordinates, Distance, Direction 'East', Landmarks, Limits, Zoning).
    5. Fills Property Owner Information with dynamic Faker data.
    6. Attaches dummy PDF proof of property.
    7. Signs acknowledgment and disclosure.
    8. Submits form via #CompletePayment and verifies redirect to Success Page.
    9. Processes Payment Gateway (if fee required) or confirms application receipt.
    10. Dismisses survey popup modal (if prompted) and clicks Return Home to Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]
    test_data = generate_junkyard_test_data()

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Junkyard Application Form"):
        junkyard_page.navigate_to_junkyard_application()

    with allure.step("3. Fill Yard Information (Yard Type, Sec of State UDL, Date Yard Established, Screening)"):
        junkyard_page.fill_yard_information(test_data)

    with allure.step("4. Fill Location Information (District, County, Route, GPS, Distance, Direction, Landmarks, Zoning)"):
        junkyard_page.fill_location_information(test_data)

    with allure.step("5. Fill Property Owner Information with Faker data"):
        junkyard_page.fill_property_owner_information(test_data)

    with allure.step("6. Upload Proof of Property dummy PDF attachment"):
        junkyard_page.upload_proof_of_property()

    with allure.step("7. Fill Acknowledgment & Signature details"):
        junkyard_page.fill_acknowledgment_and_signature(test_data)

    with allure.step("8. Submit application via #CompletePayment"):
        junkyard_page.submit_application()

    with allure.step("9. Process Payment Gateway (if fee required) or verify Success Page"):
        if "casuccesspagefull" not in payment_page.page.url.lower():
            payment_page.wait_for_payment_gateway()
            payment_page.fill_card_details()
            payment_page.click_next_step()
            payment_page.submit_payment()

    with allure.step("10. Dismiss survey modal and Return Home to Dashboard"):
        payment_page.handle_survey_modal(respond=False)
        payment_page.click_return_home()
