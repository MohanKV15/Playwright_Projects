import pytest
from pages.pre_application.pre_application_page import PreApplicationPage


def test_pre_application_flow(authenticated_page):
    """
    Verifies the complete Pre-Application workflow per user directives:
    1. Navigate to Pre-Application page and verify initial layout headers.
    2. Extract Route value from 1st row, fill Route# search input, and click Refresh.
    3. Clear all search filter inputs and click Refresh again to reload full grid.
    4. Click Edit (pencil icon) button on the 1st record row.
    5. Verify 'Pre-Application Information' full view header is visible.
    6. Click Save button and assert 0 validation errors.
    """
    pre_app_page = PreApplicationPage(authenticated_page)

    # 1. Navigate to Pre-Application & verify initial layout
    pre_app_page.navigate_to_pre_application()
    pre_app_page.verify_initial_layout()

    # 2. Search using 1st record Route value & refresh
    pre_app_page.search_by_first_record_route()

    # 3. Clear all search inputs & refresh again
    pre_app_page.clear_search_and_refresh()

    # 4. Open 1st record in Edit mode
    pre_app_page.open_first_record_in_edit_mode()

    # 5. Verify Pre-Application Information full view
    pre_app_page.verify_pre_application_info()

    # 6. Save and verify zero validation errors
    pre_app_page.safe_click_save()
