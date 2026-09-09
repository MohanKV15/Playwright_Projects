import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.amendment_page import AmendmentPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Amendment / Modification Requests")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.amendment
@pytest.mark.smoke
def test_amendment_full_workflow(
    authenticated_amendment: AmendmentPage,
):
    """
    Test Case ID: TC_STAFF_AMEND_001
    Workflow:
    1. Activate permit session for company and navigate to Amendment.
    2. Verify listing page elements (Permit details, Modification Requests heading, k-grid).
    3. Execute and verify Add Amendment dialog workflow (Add New -> Alert -> OK -> Listing).
    """
    amendment_pg = authenticated_amendment

    with allure.step("1. Activate permit session and navigate to Amendment page"):
        amendment_pg.navigate_to_amendment(company_name="IDOTOAtest2")

    with allure.step("2. Verify listing view elements loaded"):
        amendment_pg.verify_amendment_page_loaded()

    with allure.step("3. Execute Add New Amendment alert and confirmation workflow"):
        amendment_pg.handle_add_amendment_workflow()


