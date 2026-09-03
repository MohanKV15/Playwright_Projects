import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.permit_completion_page import PermitCompletionPage

class TestPermitCompletion:
    
    def test_permit_completion_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Permit Completion tab, and complete the permit completion flow.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        permit_completion_page = PermitCompletionPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Permit Completion Tab
        permit_completion_page.navigate_to_permit_completion()
        
        # 3. Complete the Permit Completion flow
        permit_completion_page.verify_tab_headings()
        permit_completion_page.change_status()
        
        # Select current date for the 1st date picker (index 0)
        permit_completion_page.select_current_date(0)
        
        # Generate Permit
        permit_completion_page.generate_permit()
        
        # Select current date for the 2nd date picker (index 1)
        permit_completion_page.select_current_date(1)
        
        # Select current date for the 3rd date picker (index 2)
        permit_completion_page.select_current_date(2)
        
        # Enter Comments and click Save
        permit_completion_page.enter_comments_and_save()

