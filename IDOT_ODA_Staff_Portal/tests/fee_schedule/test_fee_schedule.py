import allure
import pytest
from playwright.sync_api import Page
from IDOT_ODA_Staff_Portal.pages.fee_schedule.fee_schedule_page import FeeSchedulePage


@allure.epic("Staff Portal")
@allure.feature("Fee Schedule")
@allure.story("Add Fee Schedule and Grid Record Verification")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.fee_schedule
@pytest.mark.regression
def test_add_and_verify_fee_schedule_workflow(authenticated_page: Page):
    """
    Test Case ID: TC_STAFF_FEE_SCHEDULE_001
    Workflow:
    1. Navigate: Click 'Fee Schedule' sidebar menu and open 'Fee Schedule Listing'.
    2. Listing Page: Assert heading 'Fee Schedule' and grid content visibility.
    3. Add Schedule: Click '+ Add Fee Schedule' button and verify details form.
    4. Dynamic Selection: Dynamically select a distinct application type from dropdown options.
    5. Effective Date: Select present day date in the Kendo calendar datepicker.
    6. Save & Confirm: Click Save and confirm 'Operation completed' dialog.
    7. Search & Verify: Filter by saved application type, click Search, and verify record in the grid.
    """
    fee_schedule_pg = FeeSchedulePage(authenticated_page)

    with allure.step("Execute Add Fee Schedule and Grid Verification Workflow"):
        result = fee_schedule_pg.execute_add_and_verify_fee_schedule_workflow()

        assert result["status"] == "Verified successfully", "Fee schedule workflow execution failed"
        assert result["application_type"], "Application type was not selected"
        assert result["effective_date"], "Effective date was not selected"
        assert result["grid_verified"] is True, "Saved fee schedule record was not found in grid"
