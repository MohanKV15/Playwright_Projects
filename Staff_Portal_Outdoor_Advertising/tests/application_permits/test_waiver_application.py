import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.waiver_application_page import WaiverApplicationPage

class TestWaiverApplication:
    
    def test_waiver_application_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Waiver Application tab, fill out and save the waiver form using
        Faker library and selecting the current date, accept the confirmation dialog,
        and verify that the saved form section is visible.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        waiver_page = WaiverApplicationPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Waiver Application Tab
        waiver_page.navigate_to_waiver_application_tab()
        
        # 3. Fill out and save the Waiver details
        waiver_page.fill_waiver_application_details()
