import pytest
from playwright.sync_api import Page
from pages.violations.generate_forms_page import ViolationGenerateFormsPage


class TestViolationGenerateForms:

    def test_generate_forms_flow(self, authenticated_page: Page):
        """
        Verifies the complete Violation Generate Forms workflow:
        1. Navigates to Violations Listing.
        2. Asserts "Violation Search (Enter the" is visible.
        3. Searches by dealer name 'vansh'.
        4. Edits the matching record '2026-618 Vansh tech pvt ltd'.
        5. Navigates to the Generate Forms tab.
        6. Verifies all headings, layouts, and containers are visible.
        7. Confirms that templates/records in the grid are visible.
        """
        generate_forms_page = ViolationGenerateFormsPage(authenticated_page)

        # 1. Navigate to Violations Listing
        generate_forms_page.navigate_to_violations_listing()

        # 2. Search for dealer name 'vansh'
        generate_forms_page.search_by_dealer_name(dealer_name="vansh")

        # 3. Edit the record
        generate_forms_page.click_edit_on_first_record()

        # 4. Navigate to Generate Forms tab and verify layout
        generate_forms_page.navigate_to_generate_forms()

        # 5. Verify records/templates are visible in the grid
        generate_forms_page.verify_records_visible()
