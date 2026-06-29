import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DealerStatusLogPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation Links
        self.dealers_menu_link = page.get_by_role("link", name=re.compile(r"Dealers\s*", re.I))
        self.status_log_menu_link = page.locator("#navigationMenu2 a[href*='DealerStatusLogStaffFull']")
        
        # Heading & Grid Content elements
        self.dealer_details_heading = page.get_by_role("heading", name="Dealer Details")
        self.dealer_details_summary = page.get_by_text("Dealer Details Dealer Number")
        self.status_log_heading = page.get_by_role("heading", name="Status Log")
        
        # Content Layout containers
        self.status_log_grid_container = page.locator("div:nth-child(2) > div:nth-child(2)").first
        self.outer_form_layout = page.locator("#partial-form > section > div > div")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("dealer")

    def navigate_to_status_log(self) -> None:
        """Navigates to the Status Log page from the Dealers sidebar category menu."""
        logger.info("Navigating to Dealer Status Log page")
        self._expand_navigation_menu()
        
        logger.info("Clicking Status Log submenu link")
        self.status_log_menu_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def verify_status_log_elements(self) -> None:
        """Verifies that all required headings, summaries, and data lists are visible."""
        logger.info("Verifying visibility of Status Log page elements")
        
        expect(self.dealer_details_heading).to_be_visible(timeout=15000)
        expect(self.dealer_details_summary).to_be_visible(timeout=10000)
        expect(self.status_log_heading).to_be_visible(timeout=10000)
        expect(self.status_log_grid_container).to_be_visible(timeout=10000)
        expect(self.outer_form_layout).to_be_visible(timeout=10000)
