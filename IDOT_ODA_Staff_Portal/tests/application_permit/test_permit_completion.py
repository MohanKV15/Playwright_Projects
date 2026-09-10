import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.permit_completion_page import PermitCompletionPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Permit Completion & Generation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.permit_completion
@pytest.mark.smoke
def test_permit_completion_full_workflow(
    authenticated_permit_completion: PermitCompletionPage,
):
    """
    Test Case ID: TC_STAFF_PERMIT_COMPLETION_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Permit Completion' via sidebar menu link and verify page elements.
    3. Save permit configuration and confirm modal OK popup dialog.
    4. Generate permit, verify preview canvas (#mainCanvas) in popup window, close popup, and confirm 'Generated successfully' modal.
    5. Verify 'Permit Status' heading and form wrapper layout container (#partial-form).
    """
    permit_comp_pg = authenticated_permit_completion

    with allure.step("1. Activate permit session and navigate to Permit Completion page"):
        permit_comp_pg.navigate_to_permit_completion(company_name="IDOTOAtest2")

    with allure.step("2. Verify Permit Completion page headers and action elements loaded"):
        permit_comp_pg.verify_permit_completion_page_loaded()

    with allure.step("3. Save permit configuration and confirm modal dialog"):
        permit_comp_pg.save_permit()

    with allure.step("4. Generate permit, verify canvas preview popup window, and confirm success modal"):
        success = permit_comp_pg.generate_permit()
        assert success, "Permit generation workflow failed"

    with allure.step("5. Verify Permit Status section and form wrapper container"):
        permit_comp_pg.verify_permit_status_and_form()
