import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.payment_activity.payment_activity_page import (
    PaymentActivityPage,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Payment Activity")
@allure.story("Filter Payment Activity by Period and Export History")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.dashboard
@pytest.mark.regression
def test_payment_activity_filter_and_export(
    login_page: LoginPage,
    payment_activity_page: PaymentActivityPage,
):
    """
    Test Case ID: TC_PAYMENT_ACTIVITY_001
    Verifies end-to-end payment activity workflow:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Payment Activity card ('#btnViewPayment').
    3. Verifies page heading and Kendo grid visibility ('.k-grid-content').
    4. Filters payment history by period '2026' via Kendo dropdown.
    5. Filters payment history by period 'Last 6 months' via Kendo dropdown.
    6. Exports payment activity report, verifying clean downloads folder and presence of latest file.
    7. Navigates back to Dashboard via ' Back' button.
    """
    valid_data = LOGIN_DATA["valid_credentials"]

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Payment Activity"):
        payment_activity_page.navigate_to_payment_activity()

    with allure.step("3. Verify Payment Activity page and grid"):
        payment_activity_page.verify_payment_activity_page()

    with allure.step("4. Filter by period '2026'"):
        payment_activity_page.select_period("2026")

    with allure.step("5. Filter by period 'Last 6 months'"):
        payment_activity_page.select_period("Last 6 months")

    with allure.step("6. Export payment activity to downloads folder"):
        downloaded_file = payment_activity_page.export_payment_activity()
        assert downloaded_file.exists(), f"Downloaded file not found at: {downloaded_file}"
        assert downloaded_file.stat().st_size > 0, "Downloaded file is empty."
        allure.attach(
            f"Downloaded File: {downloaded_file.name} ({downloaded_file.stat().st_size} bytes)",
            name="Export_Details",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("7. Click Back to return to Dashboard"):
        payment_activity_page.click_back()

