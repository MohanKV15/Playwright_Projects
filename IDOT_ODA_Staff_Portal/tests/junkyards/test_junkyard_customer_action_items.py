import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.customer_action_items_page import JunkyardCustomerActionItemsPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Customer Action Items Form Creation & Verification")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_customer_action_items
@pytest.mark.regression
def test_junkyard_customer_action_items_full_workflow(
    authenticated_junkyard_customer_action_items: JunkyardCustomerActionItemsPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_CUSTOMER_ACTION_ITEMS_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2') and select 1st record row.
    3. Navigate to Customer Action Items page via Junkyards sidebar menu.
    4. Verify page elements ('Junkyard Details Permit', 'Customer Communication', grid content).
    5. Click 'Add New', verify form header, populate dropdowns (Action Item Type, Status, Review Person).
    6. Fill Message to Customer with dynamic Faker library string and submit form.
    7. Dismiss confirmation OK popups and verify saved record in table grid.
    """
    page_obj = authenticated_junkyard_customer_action_items

    with allure.step("1-3. Search company, select record, and navigate to Junkyard Customer Action Items"):
        record_info = page_obj.navigate_to_junkyard_customer_action_items(company_name="IDOTOAtest2")
        assert record_info, "Failed to select 1st record row to activate permit context"

    with allure.step("4. Assert Customer Action Items listing page elements"):
        page_obj.verify_junkyard_customer_action_items_page_loaded()

    with allure.step("5-6. Click Add New, fill dropdowns & Faker message, submit form, and confirm OK popups"):
        action_data = page_obj.create_customer_action_item(
            action_type_name="Additional Info Requested",
            status_name="Requested",
            review_person_name="Bill Siders",
        )
        assert action_data["action_type"], "Action Item Type selection failed"
        assert action_data["message"], "Message text generation failed"

    with allure.step("7. Verify action item record in grid content table"):
        page_obj.verify_action_item_in_table()
