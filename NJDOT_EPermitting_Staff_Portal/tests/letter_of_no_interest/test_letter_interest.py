import pytest
from pages.letter_of_no_interest.letter_interest_page import LetterOfNoInterestPage


def test_letter_of_no_interest_flow(authenticated_page):
    """
    Verifies the complete Letter of No Interest workflow per user directives & codegen:
    1. Navigate to Letter of No Interest page and verify initial layout headers.
    2. Test 'Linked with Permit' checkbox toggling and Refresh.
    3. Dynamically extract Route#, Block, and Lot from 1st row and search all at once.
    4. Clear search filter inputs and click Refresh again.
    5. Open 1st record in Edit mode (pencil icon button).
    6. Verify 'Location Information' and 'Letter of No Interest View' headers.
    7. Click Save button and assert 0 validation errors.
    """
    loni_page = LetterOfNoInterestPage(authenticated_page)

    # 1. Navigate to Letter of No Interest & verify layout
    loni_page.navigate_to_loni()
    loni_page.verify_initial_layout()

    # 2. Test Linked with Permit checkbox toggle
    loni_page.test_linked_with_permit_checkbox_toggle()

    # 3. Dynamically extract Route#, Block, and Lot from 1st row & search all at once
    loni_page.search_by_first_record_route_block_lot()

    # 4. Clear search inputs & refresh again
    loni_page.clear_search_and_refresh()

    # 5. Open 1st record in Edit mode
    loni_page.open_first_record_in_edit_mode()

    # 6. Verify LONI full view layout
    loni_page.verify_loni_full_view()

    # 7. Save and verify zero validation errors
    loni_page.safe_click_save()
