import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.application_history.application_history_page import (
    ApplicationHistoryPage,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Application History")
@allure.story("Search 1st Record, Export History, and Filter Inactive Applications")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.dashboard
@pytest.mark.regression
def test_application_history_search_and_export(
    login_page: LoginPage,
    application_history_page: ApplicationHistoryPage,
):
    """
    Test Case ID: TC_APP_HISTORY_001
    Verifies end-to-end application history workflow:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Application History.
    3. Asserts Instructions banner and #AppHistoryTable grid are displayed.
    4. Dynamically retrieves 1st record application number and searches by it.
    5. Clears the search textbox.
    6. Exports applications history to dedicated downloads directory (cleans old downloads first).
    7. Clicks Search to refresh table.
    8. Toggles 'Include Inactive' checkbox and executes Search.
    9. Toggles 'Include Inactive' checkbox back and executes Search.
    10. Clicks 'Back' and asserts landing back on Dashboard.
    """
    valid_data = LOGIN_DATA["valid_credentials"]

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Application History"):
        application_history_page.navigate_to_application_history()

    with allure.step("3. Verify Application History page and grid are displayed"):
        application_history_page.verify_application_history_page()

    with allure.step("4. Search for 1st record application in table"):
        application_history_page.search_application()

    with allure.step("5. Clear search input"):
        application_history_page.clear_search()

    with allure.step("6. Export applications history and save latest file to downloads folder"):
        downloaded_file = application_history_page.export_applications()
        allure.attach(
            f"Downloaded File: {downloaded_file.name} ({downloaded_file.stat().st_size} bytes)",
            name="Export_Details",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("7. Refresh search"):
        application_history_page.click_search()

    with allure.step("8. Toggle 'Include Inactive' and Search"):
        application_history_page.toggle_include_inactive()
        application_history_page.click_search()

    with allure.step("9. Toggle 'Include Inactive' again and Search"):
        application_history_page.toggle_include_inactive()
        application_history_page.click_search()

    with allure.step("10. Click Back to return to Dashboard"):
        application_history_page.click_back()

