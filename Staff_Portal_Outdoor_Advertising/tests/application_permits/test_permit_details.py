import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage

class TestPermitDetails:
    
    def test_verify_permit_details_headings(self, authenticated_page: Page):
        """
        Verifies that a user can successfully search by Dealer Name "vansh"
        on the dashboard, select the 1st record to open, and verify that the
        Permit Details page successfully loads and scrolls to all required headings.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" on the dashboard by filling input and pressing Enter
        permit_page.search_dealer_on_dashboard("vansh")
        
        # 2. Click the button of the 1st record in the grid to open details
        permit_page.open_first_record()
        
        # 3. Assert all main headings are visible and scroll to them for demo purposes
        permit_page.verify_permit_details_page_headings()
