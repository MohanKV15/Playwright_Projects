import pytest
from playwright.sync_api import Page
from pages.license.payment_page import LicensePaymentPage


class TestLicensePayment:

    def test_add_license_payment_flow(self, authenticated_page: Page):
        """Verify adding a license payment using paper check, filling details with Faker, and verifying saved record."""
        payment_page = LicensePaymentPage(authenticated_page)

        # 1. Navigate to License Listing
        payment_page.navigate_to_license_listing()

        # 2. Search for dealer "vansh" and click Edit on target row
        payment_page.search_and_edit_license(dealer_name="vansh")

        # 3. Click Payments link and assert listing loaded
        payment_page.navigate_to_payments_tab()

        # 4. Click Add Paper Check
        payment_page.click_add_paper_check()

        # 5. Fill details using Faker (Payment Type: License Fee, Status: Paid, Present Day Date)
        payment_page.fill_payment_details_using_faker(
            payment_type="License Fee",
            status="Paid"
        )

        # 6. Save and verify final grid container
        payment_page.save_and_verify_payment_grid()
