import pytest
from playwright.sync_api import Page
from faker import Faker
from pages.violations.payments_page import ViolationPaymentsPage


class TestViolationPayment:

    def test_add_violation_payment_flow(self, authenticated_page: Page):
        """
        Verifies the complete Violation Payment workflow:
        1. Navigates to Violations Listing.
        2. Filters by dealer name 'vansh'.
        3. Edits the first matching record.
        4. Navigates to the Payments tab.
        5. Clicks 'Add Paper Check' to open the payment form.
        6. Fills the Payment & Refund Details using Faker.
        7. Saves and asserts that we are returned to the Payment Listing successfully.
        """
        fake = Faker()
        payment_page = ViolationPaymentsPage(authenticated_page)

        # 1. Navigate to Violations Listing
        payment_page.navigate_to_violations_listing()

        # 2. Search for dealer name 'vansh'
        payment_page.search_by_dealer_name(dealer_name="vansh")

        # 3. Edit the first record
        payment_page.click_edit_on_first_record()

        # 4. Navigate to Payments tab
        payment_page.navigate_to_payments()

        # 5. Click Add Paper Check
        payment_page.click_add_paper_check()

        # 6. Fill the Payment & Refund Details using Faker (always selecting 1st option for dropdowns)
        check_no = payment_page.fill_payment_details(dealer_name="Vansh tech pvt ltd")

        # 7. Save payment and verify redirection back to grid
        payment_page.save_payment(check_number=check_no)
