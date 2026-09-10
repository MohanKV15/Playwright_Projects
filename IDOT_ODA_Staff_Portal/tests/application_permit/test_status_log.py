import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.status_log_page import StatusLogPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Status Log - Add Status")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.status_log
@pytest.mark.smoke
def test_status_log_full_workflow(
    authenticated_status_log: StatusLogPage,
):
    """
    Test Case ID: TC_STAFF_STATUS_LOG_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Status Log' via sidebar menu link and verify page elements.
    3. Click 'Add Status' button and verify form container headers.
    4. Select Action Type (1st valid option / 'Application Status') and Action Item (1st valid option / 'Amended Permit').
    5. Set present day date and populate Comments field with dynamic Faker generated text.
    6. Save form, verify 'Operation completed' modal alert, click OK, and verify return to listing view.
    """
    with allure.step("1. Execute full Status Log workflow (navigate, add status, fill form, save, verify)"):
        status_data = authenticated_status_log.add_status_log_full_workflow(
            company_name="IDOTOAtest2",
            action_type="Application Status",
            action_item="Amended Permit",
        )
        assert status_data["comments"], "Status log comments were not generated"
        assert status_data["action_type"], "Action type was not selected"
