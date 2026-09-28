import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.permit_transfer.documents_and_log_page import DocumentsAndLogPage


@allure.epic("Staff Portal")
@allure.feature("Permit Transfer")
@allure.story("Documents and Log Navigation & Verification Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.permit_transfer
@pytest.mark.documents_and_log
@pytest.mark.regression
def test_documents_and_log_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_PERMIT_TRANSFER_DOCUMENTS_LOG_001
    Workflow:
    1. Parent Context: Execute PermitTransferDetailsPage workflow (search permit '016-503386', click 1st record row, verify details).
    2. Click Link: Click 'Documents and Log' sidebar sub-link under Permit Transfer.
    3. Verification: Validate 'Transfer Details Permit' text, 'Documents and Log' heading, and 'Documents and Log Create' visibility.
    4. Form Actions: Execute attach document, add communication, open/cancel send email modal, and create package via parent class.
    """
    documents_log_pg = DocumentsAndLogPage(authenticated_page)

    with allure.step("1. Execute Permit Transfer parent session, navigate to Documents and Log, and run workflow"):
        results = documents_log_pg.execute_documents_and_log_full_workflow(
            permit_number="016-503386",
            row_index=0,
        )

    with allure.step("2. Assert workflow execution results"):
        assert results["status"] == "Verified successfully", "Documents and Log workflow execution failed"
        assert results["permit_number"] == "016-503386", f"Permit number mismatch: {results['permit_number']}"
        assert results["row_index"] == 0, f"Row index mismatch: {results['row_index']}"
        assert results["document"]["title"], "Document title was not generated"
        assert results["communication"]["subject"], "Communication subject was not generated"
