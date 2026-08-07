import pytest
from pages.pre_application.pre_application_page import PreApplicationPage


def test_pre_application_flow(authenticated_page):
    """
    Verifies Pre-Application / My Ticklers page workflow:
    1. Navigate to Dashboard -> My Ticklers / Pre-Application.
    2. Verify initial grid layout.
    3. Test Close Out button and cancel confirmation dialog.
    4. Test Delete button and cancel confirmation dialog.
    5. Test Notification button report viewer popup.
    6. Select 1st option for all authorizer dropdowns and save/cancel.
    """
    page_obj = PreApplicationPage(authenticated_page)

    # 1. Navigate & verify layout
    page_obj.navigate_to_my_ticklers()
    page_obj.verify_initial_layout()

    # 2. Perform grid row actions
    page_obj.test_close_out_action()
    page_obj.test_delete_action()
    page_obj.test_notification_popup()

    # 3. Select 1st option in dropdowns and save
    page_obj.select_authorizer_dropdowns_and_save()
