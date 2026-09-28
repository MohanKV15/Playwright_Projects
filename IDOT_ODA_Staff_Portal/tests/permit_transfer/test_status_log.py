import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.permit_transfer.status_log_page import StatusLogPage


@allure.epic("Staff Portal")
@allure.feature("Permit Transfer")
@allure.story("Status Log Navigation & Verification Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.permit_transfer
@pytest.mark.regression
def test_status_log_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_PERMIT_TRANSFER_STATUS_LOG_001
    Workflow:
    1. Parent Context: Execute PermitTransferDetailsPage workflow (search permit '016-503386', click 1st record row, verify details).
    2. Click Link: Click 'Status Log' sidebar sub-link under Permit Transfer.
    3. Verification: Validate 'Transfer Details Permit' text, 'Status Log' heading, and '.k-grid-content' visibility without breaking.
    """
    status_log_pg = StatusLogPage(authenticated_page)

    with allure.step("1. Execute Permit Transfer parent session and navigate to Status Log"):
        result = status_log_pg.execute_status_log_workflow(
            permit_number="016-503386",
            row_index=0,
        )

    with allure.step("2. Assert workflow execution results"):
        assert result["status"] == "Verified successfully", "Status Log workflow execution failed"
        assert result["permit_number"] == "016-503386", f"Permit number mismatch: {result['permit_number']}"
        assert result["row_index"] == 0, f"Row index mismatch: {result['row_index']}"
