import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.dashboard.action_items.action_items_page import (
    ActionItemsPage,
)
from IDOT_ODA_Customer_Portal.utils.data_reader import DataReader
from IDOT_ODA_Customer_Portal.utils.config import Config

DATA_PATH = Config.PROJECT_ROOT / "testdata" / "login_data.json"
LOGIN_DATA = DataReader.load_json(DATA_PATH)


@allure.epic("Customer Portal")
@allure.feature("Action Items")
@allure.story("Open 1st Action Item and Save for Later")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.dashboard
@pytest.mark.regression
def test_open_action_item_and_save_for_later(
    login_page: LoginPage,
    action_items_page: ActionItemsPage,
):
    """
    Test Case ID: TC_ACTION_ITEMS_001
    Verifies end-to-end action items workflow:
    1. Authenticates user with valid credentials and PIN.
    2. Navigates from Dashboard -> Action Items.
    3. Asserts Action Items heading and #ActionItemGrid are displayed.
    4. Clicks the action button on the 1st record row in the table.
    5. Clicks 'Save for Later'.
    6. Confirms 'The page information will be...' dialog (clicks 'OK').
    7. Confirms 'Record saved successfully.' alert (clicks 'OK').
    """
    valid_data = LOGIN_DATA["valid_credentials"]

    with allure.step("1. Login to Customer Portal"):
        login_page.navigate_to_login()
        login_page.login(email=valid_data["email"], password=valid_data["password"])
        login_page.fill_pin_if_prompted(pin=valid_data.get("pin", "11"))

    with allure.step("2. Navigate to Action Items"):
        action_items_page.navigate_to_action_items()

    with allure.step("3. Verify Action Items page and grid are visible"):
        action_items_page.verify_action_items_page()

    with allure.step("4. Open 1st record row from the Action Items grid"):
        action_items_page.open_first_action_item()

    with allure.step("5. Click Save for Later"):
        action_items_page.click_save_for_later()

    with allure.step("6. Confirm 'The page information will be...' dialog"):
        action_items_page.confirm_save_for_later_dialog()

    with allure.step("7. Confirm 'Record saved successfully.' modal"):
        action_items_page.confirm_record_saved_modal()

