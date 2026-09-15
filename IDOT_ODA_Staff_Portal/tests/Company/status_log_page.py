import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.Company.status_log_page import CompanyStatusLogPage


@allure.epic("Staff Portal")
@allure.feature("Company Management")
@allure.story("Company Status Log Verification Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.company
@pytest.mark.company_status_log
@pytest.mark.regression
def test_company_status_log_search_and_verify_grid(authenticated_page):
    """
    Test Case ID: TC_STAFF_COMPANY_STATUS_LOG_001
    Workflow:
    1. Navigate: Click 'Company Listing' link.
    2. Search: Fill '#Dealer_Name' with 'IDOTOAtest2' and click Search.
    3. Navigate Sub-menu: Click 'Status Log' link.
    4. Assertions:
       - Verify 'Company Details Company' is visible.
       - Verify 'Status Log' heading is visible.
       - Verify '#StatusLogGrid' table is visible.
    """
    status_log_pg = CompanyStatusLogPage(authenticated_page)
    with allure.step("Execute Company Status Log search and layout verification workflow"):
        result = status_log_pg.execute_status_log_workflow(company_name="IDOTOAtest2")
        assert result["status"] == "Verified successfully", "Company Status Log workflow execution failed"
        assert result["heading_status_log_visible"], "Status Log heading is not visible"
        assert result["status_log_grid_visible"], "StatusLogGrid table is not visible"
