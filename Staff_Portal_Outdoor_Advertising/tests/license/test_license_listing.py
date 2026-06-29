import pytest
from playwright.sync_api import Page
from pages.license.license_listing_page import LicenseListingPage


class TestLicenseListing:

    def test_license_listing_flow(self, authenticated_page: Page):
        """Verify navigation, search, assertions, save action, and popup OK click in License Listing."""
        license_page = LicenseListingPage(authenticated_page)

        # 1. Navigate to License Listing
        license_page.navigate_to_license_listing()

        # 2. Search for Dealer Name "vansh" and Dealer Number "701001"
        license_page.search_dealer_license(name="vansh", number="701001")

        # 3. Verify License Details headers and forms are visible
        license_page.assert_license_details_visible()

        # 4. Save and handle popup OK confirmation
        license_page.click_save()
        license_page.handle_kendo_popup_and_ok()
