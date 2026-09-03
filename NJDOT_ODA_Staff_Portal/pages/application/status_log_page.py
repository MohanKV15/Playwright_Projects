import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class StatusLogPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation / Sidebar Link
        self.status_log_link = page.get_by_role("link", name="Status Log")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.status_log_heading = page.get_by_role("heading", name="Status Log")
        
        # Grid container (uses class fallback or codegen structure)
        self.grid_container = page.locator(".k-grid, div:nth-child(2) > div:nth-child(2)").first
        
        # Pager elements
        self.pager_info = page.locator(".k-pager-info")
        self.next_page_link = page.get_by_role("link", name="Go to the next page")
        self.prev_page_link = page.get_by_role("link", name="Go to the previous page")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_status_log_tab(self) -> None:
        """Navigates to the Status Log tab and verifies headings load."""
        logger.info("Navigating to the Status Log tab")
        self._expand_navigation_menu()
        self.status_log_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings and grid containers are visible."""
        logger.info("Verifying headings on the Status Log tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.status_log_heading).to_be_visible(timeout=10000)
        expect(self.grid_container).to_be_visible(timeout=10000)

    def verify_pager_info(self) -> None:
        """Verifies pager information exists and contains total count text."""
        logger.info("Verifying Kendo pager information")
        try:
            expect(self.pager_info).to_be_visible(timeout=8000)
            pager_text = self.pager_info.inner_text()
            logger.info(f"Pager info text matches: '{pager_text}'")
        except Exception:
            logger.warning("Could not verify pager via .k-pager-info locator, trying text matching fallback")
            # Try to match the codegen pattern of raw inner text "Page of 1 (1 - 2 of 2 items)"
            expect(self.page.get_by_text(re.compile(r"Page.*of.*items|1 - 2 of 2 items", re.I))).to_be_visible(timeout=5000)

    def verify_pagination_functionality(self) -> None:
        """Dynamically verifies pagination if multiple pages of records are present."""
        logger.info("Verifying pagination controls visibility and actionability")
        
        # Check if "Go to the next page" button is visible and active
        if self.next_page_link.is_visible():
            class_attr = self.next_page_link.get_attribute("class") or ""
            if "k-state-disabled" not in class_attr and self.next_page_link.is_enabled():
                logger.info("More than one page of status log items found. Performing pagination test.")
                self.next_page_link.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(1000)
                
                # Check that we can navigate back to previous page
                expect(self.prev_page_link).to_be_visible(timeout=5000)
                self.prev_page_link.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(1000)
                logger.info("Successfully navigated forward and backward through the status logs list")
            else:
                logger.info("Pagination controls are visible but disabled (only 1 page of records exists).")
        else:
            logger.info("No pagination control detected (records fit on a single page).")
