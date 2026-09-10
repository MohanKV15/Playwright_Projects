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
    with allure.step("1. Execute full Permit Completion workflow (navigate, save permit, generate permit, verify status & form)"):
        authenticated_permit_completion.handle_permit_completion_full_workflow(company_name="IDOTOAtest2")
