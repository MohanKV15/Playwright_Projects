import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitDetailsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators for search
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        
        # Grid - locate the action button in the first data row
        self.first_grid_row_button = page.locator("#PermitListGrid tbody tr").first.get_by_role("button")
        
        # Headers/Links for validation
        self.permit_details_link = page.get_by_role("link", name="Application/Permit Details")
        self.app_app_div = page.locator("div").filter(has_text="Application Application")
        self.application_heading = page.get_by_role("heading", name="Application")
        self.partial_form = page.locator("#partial-form").first
        self.gis_heading = page.get_by_role("heading", name="GIS Information")
        self.sign_details_heading = page.get_by_role("heading", name="Sign Details")
        self.property_owner_heading = page.get_by_role("heading", name="Property Owner Information")

    def search_dealer_on_dashboard(self, dealer_name: str) -> None:
        """Searches for a dealer by filling in the Dealer Name and pressing Enter."""
        logger.info(f"Searching for dealer '{dealer_name}' by pressing Enter")
        self.dealer_name_input.scroll_into_view_if_needed()
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)
        self.dealer_name_input.press("Enter")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def open_first_record(self) -> None:
        """Clicks the button in the row of the PermitListGrid matching the worker index to avoid parallel collisions."""
        import os
        import re
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
        match = re.search(r"\d+", worker_id)
        worker_idx = int(match.group()) if match else 0

        logger.info(f"Opening record for worker {worker_id} (index: {worker_idx})")
        self.page.wait_for_selector("#PermitListGrid tbody tr", timeout=10000)

        rows = self.page.locator("#PermitListGrid tbody tr")
        row_count = rows.count()
        # Fallback if not enough rows
        target_idx = worker_idx if worker_idx < row_count else 0
        logger.info(f"Selected row index {target_idx} out of {row_count} available rows")

        rows.nth(target_idx).get_by_role("button").click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def verify_permit_details_page_headings(self) -> None:
        """Verifies that the Permit Details page has successfully loaded with all required headings."""
        logger.info("Verifying all Permit Details headings are visible and scrolling to them")
        
        # Ensure navigation menu is expanded so that sidebar submenus are visible
        self._expand_navigation_menu()
        
        expect(self.permit_details_link).to_be_visible(timeout=15000)
        expect(self.app_app_div.nth(4)).to_be_visible(timeout=10000)
        expect(self.partial_form).to_be_visible(timeout=10000)
        
        # Scroll to and verify each main section heading
        logger.info("Scrolling to and verifying Application section")
        self.scroll_to_locator(self.application_heading)
        self.page.wait_for_timeout(1000)
        expect(self.application_heading).to_be_visible(timeout=10000)
        
        logger.info("Scrolling to and verifying GIS Information section")
        self.scroll_to_locator(self.gis_heading)
        self.page.wait_for_timeout(1000)
        expect(self.gis_heading).to_be_visible(timeout=10000)
        
        logger.info("Scrolling to and verifying Sign Details section")
        self.scroll_to_locator(self.sign_details_heading)
        self.page.wait_for_timeout(1000)
        expect(self.sign_details_heading).to_be_visible(timeout=10000)
        
        logger.info("Scrolling to and verifying Property Owner Information section")
        self.scroll_to_locator(self.property_owner_heading)
        self.page.wait_for_timeout(1000)
        expect(self.property_owner_heading).to_be_visible(timeout=10000)
