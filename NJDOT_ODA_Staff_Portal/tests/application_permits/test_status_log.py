import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.status_log_page import StatusLogPage

class TestStatusLog:
    
    def test_status_log_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Status Log tab, verify page headings, and validate
        the pagination controls and info.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        status_log_page = StatusLogPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Status Log Tab
        status_log_page.navigate_to_status_log_tab()
        
        # 3. Verify Pager Information
        status_log_page.verify_pager_info()
        
        # 4. Verify Pagination controls (clicks Go to next page if multiple pages exist)
        status_log_page.verify_pagination_functionality()
