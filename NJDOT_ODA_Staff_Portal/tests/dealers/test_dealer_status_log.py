import pytest
from playwright.sync_api import Page
from pages.dealers.dealer_listing_page import DealerListingPage
from pages.dealers.status_log_page import DealerStatusLogPage

class TestDealerStatusLog:
    
    def test_dealer_status_log_flow(self, authenticated_page: Page):
        """
        Verifies that a user can:
        1. Navigate to Dealers -> Dealer Listing, search for Dealer "vansh", and open the record.
        2. From the details page, click the Status Log menu link in the Dealers sidebar subcategory.
        3. Assert that all headers and log container divs are successfully displayed on the Status Log view.
        """
        listing_page = DealerListingPage(authenticated_page)
        status_log_page = DealerStatusLogPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and navigate to its details page
        listing_page.navigate_to_dealer_listing()
        listing_page.search_dealer("vansh")
        listing_page.open_first_record()
        
        # 2. Click the "Status Log" menu link to load logs
        status_log_page.navigate_to_status_log()
        
        # 3. Assert all required elements are visible
        status_log_page.verify_status_log_elements()
