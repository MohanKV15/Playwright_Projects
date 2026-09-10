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

    with allure.step("1. Execute full Amendment workflow (navigate, verify listing, handle alert/form workflow)"):
        result = authenticated_amendment.execute_amendment_full_workflow(company_name="IDOTOAtest2")
        assert result is not None, "Amendment workflow failed to return execution result"


