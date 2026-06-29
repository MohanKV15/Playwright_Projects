import pytest
import logging
from playwright.sync_api import Page
from pages.renewals.permit_payment_page import PermitPaymentPage

logger = logging.getLogger(__name__)

class TestPermitPayment:

    def test_permit_payment_flow(self, authenticated_page: Page):
        """
        Verifies the complete Permit Payment workflow:
        1. Navigates to the Permit Payments dashboard.
        2. Iterates through each status: Cancelled, Not Paid, Paid, Refund/Bounce, Requested, SEE LATE FEE.
        3. Dynamically extracts first record information and searches for it.
        4. Validates Payment Details modal navigation and back actions.
        """
        payment_page = PermitPaymentPage(authenticated_page)

        # 1. Navigate to Permit Payments
        payment_page.navigate_to_permit_payments()

        # 2. Iterate through all statuses
        statuses = ["Cancelled", "Not Paid", "Paid", "Refund/Bounce", "Requested", "SEE LATE FEE"]

        for status in statuses:
            logger.info(f"=== Testing Payment Status: '{status}' ===")
            
            # Select status & search
            payment_page.select_status(status)
            payment_page.click_search()

            # Check if records are present for this status
            if payment_page.has_grid_records():
                # Extract first record info
                dealer_name, dealer_number = payment_page.get_first_record_dealer_info()
                
                # Use only the first alphanumeric word of the dealer name to avoid single quotes/commas breaking backend queries
                import re
                words = [w for w in re.split(r"[^a-zA-Z0-9]+", dealer_name) if len(w) > 0]
                search_name = words[0] if words else dealer_name
                logger.info(f"Using search name term: '{search_name}' for dealer: '{dealer_name}'")

                # Perform filtered search
                payment_page.search_by_dealer_info(search_name, dealer_number)
                
                # Check if search auto-navigated to Payment Details page
                if payment_page.payment_details_heading.is_visible(timeout=5000):
                    logger.info(f"Auto-navigated to Payment Details for status: '{status}'")
                    payment_page.verify_payment_details_page()
                    payment_page.click_back()
                else:
                    logger.info(f"Stayed on search grid for status: '{status}'")
                    assert payment_page.has_grid_records(), f"Grid should display results for search term '{search_name}'"
                
                # Reset search fields for next status
                payment_page.clear_search_fields()
            else:
                logger.warning(f"No records present in the database for status: '{status}'. Skipping dynamic search.")
                payment_page.clear_search_fields()
