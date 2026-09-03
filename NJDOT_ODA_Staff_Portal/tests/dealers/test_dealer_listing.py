import pytest
from playwright.sync_api import Page
from pages.dealers.dealer_listing_page import DealerListingPage

class TestDealerListing:
    
    def test_dealer_listing_flow(self, authenticated_page: Page):
        """
        Verifies that a user can navigate to Dealers -> Dealer Listing, search for Dealer "vansh",
        open the 1st record, verify details, navigate to Add Contact and back, perform a Name Change request
        and cancel it, and verify Violation Details are visible.
        """
        dealer_page = DealerListingPage(authenticated_page)
        
        # 1. Navigate to Dealer Listing Page
        dealer_page.navigate_to_dealer_listing()
        
        # 2. Search for Dealer "vansh"
        dealer_page.search_dealer("vansh")
        
        # 3. Open first record
        dealer_page.open_first_record()
        
        # 4. Verify Dealer Details & Contact Grid
        dealer_page.verify_dealer_details()
        
        # 5. Navigate to Add Contact and back
        dealer_page.navigate_add_contact_and_back()
        
        # 6. Request Name Change and cancel
        dealer_page.request_name_change_and_cancel()
        
        # 7. Verify Violation Details visibility
        dealer_page.verify_violation_details()
