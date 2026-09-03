import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage


def test_permit_listing_codegen_flow(authenticated_page):
    """
    Verifies the complete Permit Listing workflow per user codegen:
    1. Navigate to Permit Listing and verify initial page layout (Home link, Applications/Permits heading, Grid content).
    2. Click 'Add New Permit' and verify modal dialog layout.
    3. Close the modal dialog.
    4. Search by company 'HCL' and click Refresh.
    5. Navigate to the next page and click grid row Edit (#gridEdit).
    """
    permit_page = PermitListingPage(authenticated_page)

    # 1. Navigate to Permit Listing & verify initial layout
    permit_page.navigate_to_permit_listing()
    permit_page.verify_initial_layout()

    # 2. Verify Add New Permit modal layout and close modal
    permit_page.verify_and_close_add_new_modal()

    # 3. Search by company "HCL" and edit record on next page
    record_data = permit_page.search_and_edit_permit("HCL")
    assert record_data is not None
