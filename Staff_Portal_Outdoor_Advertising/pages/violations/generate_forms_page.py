import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationGenerateFormsPage(BasePage):
    """Page Object for Violations Generate Forms tab on the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")

        # Search elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.dealer_name_search_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.customer_results_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.edit_violation_button = page.locator("#btnViolationsEdit")

        # Generate Forms Tab Navigation Link
        self.generate_forms_tab = page.get_by_role("link", name="Generate Forms")

        # Headings / Layout Validation
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.violation_details_text = page.get_by_text("Violation Details Violation")
        self.generate_forms_heading = page.get_by_role("heading", name="Generate Forms")
        self.layout_container_child = page.locator("#frmCustomer > .form-wrapper > .row > div:nth-child(2)")

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Violations."""
        logger.info("Expanding Violations PanelBar navigation.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations Listing and validates elements."""
        self._expand_navigation_menu()
        if not self.violations_listing_link.is_visible():
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.page.get_by_text("Violation Search (Enter the")).to_be_visible(timeout=10000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Searches violations grid by dealer name."""
        logger.info(f"Searching for dealer '{dealer_name}' in listing grid.")
        self.dealer_name_search_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_search_input.click()
        self.dealer_name_search_input.fill(dealer_name)
        self.search_button.click()
        self._wait_for_loader()
        expect(self.customer_results_container).to_be_visible(timeout=15000)

    def click_edit_on_first_record(self, record_name: str = None) -> None:
        """Clicks edit button on the first matching record in search results."""
        logger.info("Opening the first violation record details.")
        edit_btn = self.page.locator("#btnViolationsEdit").first
        expect(edit_btn).to_be_visible(timeout=10000)
        edit_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def navigate_to_generate_forms(self) -> None:
        """Clicks the Generate Forms tab and verifies headings & layout layout container."""
        logger.info("Navigating to Generate Forms tab.")
        self.generate_forms_tab.wait_for(state="visible", timeout=10000)
        self.generate_forms_tab.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.violation_details_text).to_be_visible(timeout=10000)
        expect(self.generate_forms_heading).to_be_visible(timeout=10000)
        expect(self.layout_container_child).to_be_visible(timeout=10000)
        logger.info("Generate Forms tab headings and layout validated successfully.")

    def verify_records_visible(self) -> None:
        """Verifies that valid form templates/records list is successfully visible in the grid."""
        logger.info("Verifying that records are visible in the Generate Forms grid.")
        grid_rows = self.page.locator(".k-grid-content tbody tr, [role='grid'] tbody tr, tbody tr")
        
        # Filter out rows displaying placeholder/empty text to ensure we match only actual templates
        valid_rows = grid_rows.filter(has_not=self.page.get_by_text("no records", exact=False))
        
        # Playwright auto-retry assertion makes this highly robust without explicit sleeps/polling loops
        expect(valid_rows.first).to_be_visible(timeout=15000)
        logger.info("Successfully verified that form records are visible in the grid.")
