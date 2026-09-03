import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.Appeal_page import AppealPage

class TestAppeal:
    
    def test_appeal_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Appeal tab, fill in the details using Faker and current date, and save.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        appeal_page = AppealPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Appeal Tab
        appeal_page.navigate_to_appeal_tab()
        
        # 3. Fill in details and Save (uses default assignee Andrew Feller and Faker sentence comments)
        appeal_page.fill_appeal_details()
