import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.Inspection_page import InspectionPage
from utils.config import Config

class TestInspection:
    
    def test_add_inspection_record(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Inspection tab, add a new inspection with file upload, and save it.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        inspection_page = InspectionPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Inspection Tab
        inspection_page.navigate_to_inspection_tab()
        
        # 3. Add a new inspection record and upload dummy.pdf
        dummy_pdf_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")
        inspection_page.add_new_inspection(file_path=dummy_pdf_path)
        
        # 4. Verify the inspection record shows up in the grid
        inspection_page.verify_inspection_record_in_grid()
