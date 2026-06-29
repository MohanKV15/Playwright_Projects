import pytest
from playwright.sync_api import Page
from pages.violations.violation_details_page import ViolationDetailsPage


class TestViolationDetails:

    def test_violation_details_flow(self, authenticated_page: Page):
        """
        Verifies the Violations Search and Details workflow:
        1. Navigates to Violations Listing.
        2. Performs a search for dealer "vansh".
        3. Asserts all Violation Details containers and sections are visible.
        """
        violation_page = ViolationDetailsPage(authenticated_page)

        # 1. Navigate to Violations Listing
        violation_page.navigate_to_violations_listing()

        # 2. Search for dealer name "vansh"
        violation_page.search_by_dealer_name("vansh")

        # 3. Assert Violation Details visibility
        violation_page.verify_violation_details()
