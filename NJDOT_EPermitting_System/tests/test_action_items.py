import pytest
from NJDOT_EPermitting_System.pages.action_items.action_items_page import ActionItemsPage


@pytest.mark.authenticated
def test_action_items_flow(authenticated_page):

    action_page = ActionItemsPage(authenticated_page)

    # Step 1: Open Action Items page
    action_page.open()

    # Step 2: Validate edit functionality
    action_page.open_first_n_records(2)

    # Step 3: Validate pagination
    action_page.validate_pagination()