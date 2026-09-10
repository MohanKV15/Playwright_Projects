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
    doc_log_pg = authenticated_documents_and_log

    with allure.step("1. Activate permit session and navigate to Documents and Log page"):
        doc_log_pg.navigate_to_documents_and_log(company_name="IDOTOAtest2")

    with allure.step("2. Verify Documents and Log headers, form wrapper, and action buttons loaded"):
        doc_log_pg.verify_documents_and_log_page_loaded()

    with allure.step("3. Attach document with upload file, present day date, title, description, and save"):
        doc_info = doc_log_pg.attach_document()
        assert doc_info["title"], "Document title was not generated"

    with allure.step("4. Add communication log entry with subject, description, and save"):
        comm_info = doc_log_pg.add_communication()
        assert comm_info["subject"], "Communication subject was not generated"

    with allure.step("5. Open Send Email modal and cancel/dismiss it"):
        doc_log_pg.open_and_cancel_send_email()

    with allure.step("6. Execute Create Package workflow (select attachment, confirm OK dialog)"):
        doc_log_pg.create_package()
