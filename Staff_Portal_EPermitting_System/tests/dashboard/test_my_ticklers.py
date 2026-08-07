import pytest
from pages.dashboard.my_ticklers_page import MyTicklersPage


def test_my_ticklers_flow(authenticated_page):
    """
    Verifies Dashboard -> My Ticklers page workflow:
    1. Navigate to Dashboard -> My Ticklers.
    2. Verify initial grid layout.
    3. Test Close Out button and cancel confirmation dialog.
    4. Test Delete button and cancel confirmation dialog.
    5. Test Notification button report viewer popup.
    6. Select 1st option for all authorizer dropdowns and save/cancel.
    """
    ticklers_page = MyTicklersPage(authenticated_page)

    # 1. Navigate & verify layout
    ticklers_page.navigate_to_my_ticklers()
    ticklers_page.verify_initial_layout()

    # 2. Perform grid row actions
    ticklers_page.test_close_out_action()
    ticklers_page.test_delete_action()
    ticklers_page.test_notification_popup()

    # 3. Select 1st option in dropdowns and save
    ticklers_page.select_authorizer_dropdowns_and_save()
