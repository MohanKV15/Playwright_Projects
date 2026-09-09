import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.customer_action_items_page import CustomerActionItemsPage


@pytest.mark.application_permit
@pytest.mark.customer_action_items
@pytest.mark.smoke
def test_customer_action_items_full_workflow(
    authenticated_customer_action_items: CustomerActionItemsPage,
):
    """
    Test Case: Customer Action Items End-to-End Workflow

    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit context.
    2. Navigate to 'Customer Action Items' via sidebar link.
    3. Verify listing page loads with 'Application Details Permit', 'Customer Communication' heading, and 'Add New' button.
    4. Click 'Add New' and verify customer communication details form loaded.
    5. Dynamically select the 1st valid dropdown options for:
       - Action Item Type (#Communication_Type)
       - Status (#Review_Status)
       - Review Person (#Review_By)
    6. Populate 'Message to Customer *' using dynamic Faker text.
    7. Click 'Attach', select the first available attachment from 'Send Email With Attachments' modal, and confirm.
    8. Click 'Save' and verify redirect back to listing page.
    9. Verify the newly created action item is displayed in the listing table.
    10. Click the view/action button on the saved table row to re-open it.
    11. Verify the saved details and comments are displayed correctly.
    """
    cai_page = authenticated_customer_action_items

    # 1. Activate permit session and navigate to Customer Action Items
    cai_page.navigate_to_customer_action_items(company_name="IDOTOAtest2")

    # 2. Create new Customer Action Item (1st dropdown options, Faker message, attachment, save)
    saved_data = cai_page.create_customer_action_item(attach_document=True)
    assert all(saved_data.values()), f"Customer action item form data was incomplete: {saved_data}"

    # 3. Verify newly created record appears in the listing table
    saved_row = cai_page.verify_action_item_in_table()
    assert saved_row, "Created customer action item row was not found in listing table"

    # 4. Open record from table and verify details form displays accurately
    cai_page.open_action_item_and_verify_details(saved_row)

