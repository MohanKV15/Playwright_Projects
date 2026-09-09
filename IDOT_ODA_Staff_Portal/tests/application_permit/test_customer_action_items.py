import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.customer_action_items_page import CustomerActionItemsPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Customer Communication & Action Items")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.customer_action_items
@pytest.mark.smoke
def test_customer_action_items_full_workflow(
    authenticated_customer_action_items: CustomerActionItemsPage,
):
    """
    Test Case ID: TC_STAFF_CAI_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit context.
    2. Navigate to 'Customer Action Items' and verify listing view.
    3. Create Customer Action Item (dynamic 1st dropdown options, Faker message, attachment, save).
    4. Verify newly created record appears in the listing table.
    5. Re-open record from table and verify details form displays accurately.
    """
    cai_page = authenticated_customer_action_items

    with allure.step("1. Activate permit session and navigate to Customer Action Items"):
        cai_page.navigate_to_customer_action_items(company_name="IDOTOAtest2")

    with allure.step("2. Create Customer Action Item with document attachment and dynamic Faker message"):
        saved_data = cai_page.create_customer_action_item(attach_document=True)
        assert all(saved_data.values()), f"Customer action item form data was incomplete: {saved_data}"

    with allure.step("3. Verify newly created record in listing table"):
        saved_row = cai_page.verify_action_item_in_table()
        assert saved_row, "Created customer action item row was not found in listing table"

    with allure.step("4. Open record from table and verify details form displays accurately"):
        cai_page.open_action_item_and_verify_details(saved_row)


