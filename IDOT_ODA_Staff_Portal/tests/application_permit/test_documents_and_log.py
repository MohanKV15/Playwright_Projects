import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.documents_and_log_page import DocumentsAndLogPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Documents and Log - Package Creation & Communication")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.documents_and_log
@pytest.mark.smoke
def test_documents_and_log_full_workflow(
    authenticated_documents_and_log: DocumentsAndLogPage,
):
    """
    Test Case ID: TC_STAFF_DOCUMENTS_AND_LOG_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Documents and Log' via sidebar menu link and verify page elements.
    3. Attach Document (upload file, present day date, title, description, save).
    4. Add Communication (present day date, subject, description, save).
    5. Send Email modal (open modal and click Cancel to dismiss).
    6. Create Package (click button, select attachment checkbox, click Select Attachments, confirm OK dialog).
    """
    with allure.step("1. Execute full Documents and Log workflow (navigate, attach doc, add comm, cancel email, create package)"):
        results = authenticated_documents_and_log.execute_documents_and_log_full_workflow(company_name="IDOTOAtest2")
        assert results["document"]["title"], "Document title was not generated"
        assert results["communication"]["subject"], "Communication subject was not generated"
