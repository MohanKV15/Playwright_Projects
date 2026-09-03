import pytest
from pages.action_items.action_items_page import ActionItemsPage

def test_action_items_pagination_and_click(authenticated_page):
    """
    Validates clicking 'Action Items', dynamically paginating to the last page,
    and clicking an action button within the grid.
    """
    # 1. Initialize Action Items POM
    action_items_page = ActionItemsPage(authenticated_page)
    
    # 2. Open the Action Items panel
    action_items_page.open()
    
    # 3. Paginate until the very end of the grid
    action_items_page.validate_pagination()
    
    # 4. Open the first 2 action items, verifying they load correctly, and back out
    action_items_page.open_first_n_records(n=2)
    
    print("[INFO] Action Items pagination and interaction completed successfully!")
