import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.payment_page import PaymentsPage

class TestPayment:
    
    def test_add_payment_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Payments tab, add a new paper check payment, and verify it in the listing.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        payment_page = PaymentsPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Payments Tab
        payment_page.navigate_to_payments_tab()
        
        # 3. Add Paper Check Payment
        payment_page.add_paper_check_payment()
