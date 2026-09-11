import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.permit_completion_page import JunkyardPermitCompletionPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Permit Completion & Document Generation Verification")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_permit_completion
@pytest.mark.regression
def test_junkyard_permit_completion_full_workflow(
    authenticated_junkyard_permit_completion: JunkyardPermitCompletionPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_PERMIT_COMPLETION_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2') and select 1st record row.
    3. Navigate to Permit Completion page via Junkyards sidebar menu.
    4. Verify page heading ('Permit Completion').
    5. Click 'Generate Permit', verify #mainCanvas on popup window, close popup window, assert 'Generated successfully', and confirm OK popup.
    6. Click 'Save', assert 'Operation completed', and confirm OK popup.
    """
    page_obj = authenticated_junkyard_permit_completion

    with allure.step("1-3. Search company, select record, and navigate to Junkyard Permit Completion"):
        record_info = page_obj.navigate_to_junkyard_permit_completion(company_name="IDOTOAtest2")
        assert record_info, "Failed to select 1st record row to activate permit context"

    with allure.step("4. Assert Permit Completion page elements"):
        page_obj.verify_junkyard_permit_completion_page_loaded()

    with allure.step("5. Generate Permit document, verify popup canvas preview, and confirm OK popup"):
        permit_generated = page_obj.generate_permit()
        assert permit_generated, "Permit document generation failed"

    with allure.step("6. Save Permit Completion and confirm OK popup"):
        page_obj.save_permit_completion()
