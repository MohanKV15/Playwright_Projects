import re
import logging
from playwright.sync_api import expect, Page
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Using a more robust locator to find the dashboard header across environments
        self.header = page.locator("h2, h1, .navbar-brand").filter(has_text=re.compile(r"E-Permitting System|Staff Portal|Outdoor Advertising", re.IGNORECASE)).first
        
        # Search Filters
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=re.compile(r"\bSearch\b", re.IGNORECASE))
        
        # Result Grid
        self.permit_list_grid = page.locator("#PermitListGrid > .form-wrapper > .row > .col-md-12")

    def assert_dashboard_loaded(self) -> None:
        """Verifies the dashboard components have successfully rendered on screen"""
        logger.info("Verifying Dashboard has loaded")
        expect(self.dealer_name_input).to_be_visible(timeout=45000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Fills the Dealer Name search box and executes the search."""
        logger.info(f"Searching for Dealer Name: '{dealer_name}'")
        
        # Click the dealer input (with fallback for intercepted clicks)
        try:
            self.dealer_name_input.click(modifiers=["ControlOrMeta"], timeout=5000)
        except Exception:
            self.dealer_name_input.click(timeout=5000)
            
        self.dealer_name_input.fill(dealer_name)
        
        # Click Search
        logger.info("Clicking the Search button")
        try:
            self.search_button.first.click(modifiers=["ControlOrMeta"], timeout=5000)
        except Exception:
            self.search_button.first.click(timeout=5000)

    def assert_search_results_visible(self) -> None:
        """Asserts that the permit list grid appears after a search."""
        logger.info("Verifying the Permit List Grid is visible after search")
        # Ensure the grid itself appears
        expect(self.permit_list_grid).to_be_visible(timeout=15000)
