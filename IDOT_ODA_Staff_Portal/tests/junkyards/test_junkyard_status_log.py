import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.status_log_page import JunkyardStatusLogPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Status Log - Add Status")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_status_log
@pytest.mark.regression
def test_junkyard_status_log_full_workflow(
    authenticated_junkyard_status_log: JunkyardStatusLogPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_STATUS_LOG_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') on Junkyard/Permit Search to activate permit session context.
    2. Navigate to 'Status Log' via Junkyards sidebar menu link and verify headers ('Junkyard Details Permit', 'Status Log', #StatusLogGrid, .k-grid-content).
    3. Click 'Add Status' button.
    4. Fill status log details (Action Type, Action Item, Date, Faker comments) leveraging inherited parent logic.
    5. Save form, confirm OK modal dialog, and return to Status Log listing grid view.
    """
    page_obj = authenticated_junkyard_status_log

    with allure.step("1. Execute full Junkyard Status Log workflow (navigate, add status, fill form, save, verify)"):
        status_data = page_obj.add_status_log_full_workflow(
            company_name="IDOTOAtest2",
            action_type="Application Status",
            action_item="Amended Permit",
        )
        assert status_data["comments"], "Status log comments were not generated"
        assert status_data["action_type"], "Action type was not selected"
