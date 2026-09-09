import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.amendment_page import AmendmentPage


@pytest.mark.application_permit
@pytest.mark.amendment
@pytest.mark.smoke
def test_amendment_full_workflow(
    authenticated_amendment: AmendmentPage,
):
    """
    Test Case: Amendment / Modification Requests Workflow

    User codegen workflow:
    1. Click sidebar link 'Amendment'.
    2. Expect 'Application Details Permit' to be visible.
    3. Expect heading 'Modification Requests' to be visible.
    4. Expect 'Modification Requests Add New' to be visible.
    5. Expect locator('.k-grid-content') to be visible.
    6. Click button 'Add New Amendment'.
    7. Expect 'Sign is already erected,' dialog to be visible.
    8. Click 'OK' button.
    9. Expect 'Modification Requests Add New' to be visible.
    """
    amendment_pg = authenticated_amendment

    # 1. Activate permit session for company and navigate to Amendment
    amendment_pg.navigate_to_amendment(company_name="IDOTOAtest2")

    # 2. Verify listing page elements
    amendment_pg.verify_amendment_page_loaded()

    # 3. Execute and verify Add Amendment dialog workflow (Add New -> Alert -> OK -> Listing)
    amendment_pg.handle_add_amendment_workflow()

