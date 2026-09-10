import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.original_permit_page import OriginalPermitPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Original Permit View Verification")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.application_permit
@pytest.mark.original_permit
@pytest.mark.smoke
def test_original_permit_full_workflow(
    authenticated_original_permit: OriginalPermitPage,
):
    """
    Test Case ID: TC_STAFF_ORIGINAL_PERMIT_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Original Permit' via sidebar menu link.
    3. Verify page elements:
       - 'Application Details Permit' header banner
       - 'Sign Information' heading
       - 'Location Information' heading
       - Form wrapper container layout (#partial-form)
    """
    original_permit_pg = authenticated_original_permit

    with allure.step("1. Activate permit session and navigate to Original Permit page"):
        original_permit_pg.navigate_to_original_permit(company_name="IDOTOAtest2")

    with allure.step("2. Verify Original Permit page headers, section headings, and layout container"):
        original_permit_pg.verify_original_permit_page_loaded()
