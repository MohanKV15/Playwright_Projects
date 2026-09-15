import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.documents_and_log_page import JunkyardDocumentsAndLogPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Documents and Log - Package Creation & Communication")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_documents_and_log
@pytest.mark.regression
def test_junkyard_documents_and_log_full_workflow(
    authenticated_junkyard_documents_and_log: JunkyardDocumentsAndLogPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_DOCUMENTS_AND_LOG_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') on Junkyard/Permit Search to activate permit session context.
    2. Navigate to 'Documents and Log' via Junkyards sidebar menu link and verify headers ('Junkyard Details Permit', 'Documents and Log').
    3. Execute parent class Create Package workflow (select attachments, confirm OK dialog).
    4. Execute parent class Attach Document workflow (upload file, set date, title, description, save).
    5. Execute parent class Add Communication workflow (set date, subject, description, save).
    6. Execute parent class Send Email workflow (open modal and click Cancel to dismiss).
    """
    page_obj = authenticated_junkyard_documents_and_log

    with allure.step("1. Execute full Junkyard Documents and Log workflow (navigate, create package, attach doc, add comm, cancel email)"):
        results = page_obj.execute_junkyard_documents_and_log_full_workflow(company_name="IDOTOAtest2")
        assert results["document"]["title"], "Document title was not generated"
        assert results["communication"]["subject"], "Communication subject was not generated"
