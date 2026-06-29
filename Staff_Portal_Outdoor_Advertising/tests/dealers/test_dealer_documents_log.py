import pytest
from playwright.sync_api import Page
from pages.dealers.dealer_listing_page import DealerListingPage
from pages.dealers.documents_and_log_page import DealerDocumentsAndLogPage
from utils.config import Config

class TestDealerDocumentsLog:
    
    def test_dealer_documents_log_flow(self, authenticated_page: Page):
        """
        Verifies that a user can:
        1. Navigate to Dealers -> Dealer Listing, search for Dealer "vansh", and open the record.
        2. From the details page, click the Documents and Log menu link in the Dealers sidebar.
        3. Assert that all headers and log container divs are successfully displayed on the Documents and Log view.
        4. Upload a dummy document and save it.
        5. Add a communication log entry and save it.
        6. Click the 'Send Email' button to open the send email view, and click 'Cancel' to return.
        """
        listing_page = DealerListingPage(authenticated_page)
        doc_page = DealerDocumentsAndLogPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and navigate to its details page
        listing_page.navigate_to_dealer_listing()
        listing_page.search_dealer("vansh")
        listing_page.open_first_record()
        
        # 2. Click the "Documents and Log" menu link to load page
        doc_page.navigate_to_documents_log()
        
        # 3. Assert all required headings and container are visible
        doc_page.verify_page_headings()
        
        # 4. Attach a dummy document (using dummy.pdf)
        dummy_pdf_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")
        doc_page.attach_document(file_path=dummy_pdf_path)
        
        # 5. Add a new communication log entry
        doc_page.add_communication()
        
        # 6. Click Send Email, verify redirect to send email page, and cancel back
        doc_page.click_send_email_and_verify_navigation()
