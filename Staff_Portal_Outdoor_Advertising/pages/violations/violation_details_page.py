import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationDetailsPage(BasePage):
    """Page Object for Violations Listing and Violation Details on the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")

        # Search elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.frm_customer_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")

        # Details elements
        self.violation_glance_div = page.locator("div").filter(has_text="Violation Details at a Glance").nth(4)
        self.violation_glance_heading = page.get_by_role("heading", name="Violation Details at a Glance")
        self.linked_info_text = page.get_by_text("Link to Permit Link to Dealer")
        self.violation_status_heading = page.get_by_role("heading", name="Violation Status")
        self.violation_info_heading = page.get_by_role("heading", name="Violation Information")
        self.gis_info_heading = page.get_by_role("heading", name="GIS Information")
        self.sign_details_heading = page.get_by_role("heading", name="Sign Details")
        self.fee_assessment_heading = page.get_by_role("heading", name="Fee Assessment")
        self.inspection_container = page.locator("#violationDetailsInspection")
        self.linked_info_container = page.locator("#violationDetailsLinkedInfo")
        self.removal_info_heading = page.get_by_role("heading", name="Removal Information")
        self.removal_info_ad12_text = page.get_by_text("Removal Information Ad-12")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all violations links are visible."""
        logger.info("Expanding Violations PanelBar navigation panel.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations -> Violations Listing and validates search page load."""
        logger.info("Navigating to Violations Listing page")
        self._expand_navigation_menu()

        # If sub-menu link is not visible, toggle the parent Violations menu link
        if not self.violations_listing_link.is_visible():
            logger.info("Violations Listing link not visible; clicking Violations menu header to expand.")
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)

        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

        # Verify initial search page elements
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.frm_customer_container).to_be_visible(timeout=10000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Enters the dealer name and clicks search."""
        logger.info(f"Searching violations by Dealer Name: '{dealer_name}'")
        self.dealer_name_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)

        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        self.page.wait_for_timeout(2000)

    def verify_violation_details(self) -> None:
        """Asserts that all expected Violation Details headings and containers are visible."""
        logger.info("Asserting all Violation Details elements are visible")

        # Self-healing fallback: click the first View/Edit link/button if details are not visible directly
        if not self.violation_glance_heading.is_visible():
            # Try to find a view/edit link in the search grid
            view_btn = self.page.locator(".k-grid-content tbody tr button, .k-grid-content tbody tr a.k-grid-edit, .k-grid-content tbody tr a").first
            if view_btn.count() > 0 and view_btn.is_visible():
                logger.info("Details not directly visible; clicking first grid row view button.")
                view_btn.click()
                self.page.wait_for_load_state("networkidle")
                self._wait_for_loader()
                self.page.wait_for_timeout(2000)

        # Assert visibility of all required fields
        expect(self.violation_glance_div).to_be_visible(timeout=15000)
        expect(self.violation_glance_heading).to_be_visible(timeout=10000)
        expect(self.linked_info_text).to_be_visible(timeout=10000)
        expect(self.violation_status_heading).to_be_visible(timeout=10000)
        expect(self.violation_info_heading).to_be_visible(timeout=10000)
        expect(self.gis_info_heading).to_be_visible(timeout=10000)
        expect(self.sign_details_heading).to_be_visible(timeout=10000)
        expect(self.fee_assessment_heading).to_be_visible(timeout=10000)
        expect(self.inspection_container).to_be_visible(timeout=10000)
        expect(self.linked_info_container).to_be_visible(timeout=10000)
        expect(self.removal_info_heading).to_be_visible(timeout=10000)
        expect(self.removal_info_ad12_text).to_be_visible(timeout=10000)
