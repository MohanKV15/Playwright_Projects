import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.permit_transfer.customer_action_items_page import CustomerActionItemsPage


@allure.epic("Staff Portal")
@allure.feature("Permit Transfer")
@allure.story("Customer Action Items End-to-End Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.permit_transfer
@pytest.mark.regression
def test_customer_action_items_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_PERMIT_TRANSFER_CUST_ACTION_001
    Workflow:
    1. Parent Context: Navigate to Permit Transfer Listing, search permit '016-503386', click 1st record row.
    2. Sidebar Link: Click 'Customer Action Items' sub-link under Permit Transfer.
    3. Add New Record: Select 1st valid options for required dropdowns, fill dynamic Faker message, attach document, and Save.
    4. Table Verification: Assert newly created record exists in listing table grid.
    5. Details Re-opening: Click action button on table record row and verify details view displays accurately.
    """
    cust_action_pg = CustomerActionItemsPage(authenticated_page)

    with allure.step("Execute Permit Transfer Customer Action Items E2E workflow"):
        result = cust_action_pg.execute_customer_action_items_workflow(
            permit_number="016-503386",
            row_index=0,
            attach_document=True,
        )
        assert result["status"] == "Verified successfully", "Customer Action Items E2E workflow failed"
        assert result["permit_number"] == "016-503386", "Permit number mismatch"
        assert all(result["saved_data"].values()), f"Incomplete form data: {result['saved_data']}"
