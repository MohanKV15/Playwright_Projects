import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.Company.documents_and_log_page import CompanyDocumentsAndLogPage


@allure.epic("Staff Portal")
@allure.feature("Company Management")
@allure.story("Company Documents & Communication Log Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.company
@pytest.mark.company_documents_and_log
@pytest.mark.regression
def test_company_documents_and_log_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_COMPANY_DOCUMENTS_AND_LOG_001
    Workflow:
    1. Navigate: Click 'Company Listing' link.
    2. Search: Fill '#Dealer_Name' with 'IDOTOAtest2' and click Search.
    3. Navigate Sub-menu/Tab: Click 'Documents and Log' link.
    4. Assertions:
       - Verify 'Company Details Company' is visible.
       - Verify 'Documents and Log' heading is visible.
       - Verify 'Documents and Log Create' section is visible.
    5. Parent Class Workflows:
       - Create Package (Create Package -> Select Attachments -> Confirm OK)
       - Attach Document (Attach Document -> Upload -> Save)
       - Add Communication (Add Communication -> Save)
       - Open & Cancel Send Email modal
    """
    doc_log_pg = CompanyDocumentsAndLogPage(authenticated_page)
    with allure.step("Execute Company Documents and Log full workflow"):
        result = doc_log_pg.execute_company_documents_and_log_workflow(company_name="IDOTOAtest2")
        assert result["status"] == "Verified successfully", "Company Documents and Log workflow failed"
        assert "title" in result["document"], "Document title missing in result"
        assert "subject" in result["communication"], "Communication subject missing in result"
