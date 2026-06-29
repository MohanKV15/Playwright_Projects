import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.documents_and_log_page import DocumentsAndLogPage
from utils.config import Config

class TestDocumentsAndLog:
    
    def test_documents_and_log_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Documents and Log tab, upload a dummy document, add a new
        communication log, and create a document package selecting the first document checkbox.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        doc_page = DocumentsAndLogPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Documents and Log Tab
        doc_page.navigate_to_documents_and_log_tab()
        
        # 3. Attach Document (using dummy.pdf)
        dummy_pdf_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")
        doc_page.attach_document(file_path=dummy_pdf_path)
        
        # 4. Add Communication entry
        doc_page.add_communication()
        
        # 5. Create Document Package
        doc_page.create_document_package()
