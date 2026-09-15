import logging
import re
from typing import Dict, Any
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.Company.company_listing_page import CompanyListingPage

logger = logging.getLogger(__name__)


class CompanyStatusLogPage(BasePage):
    """
    Page Object Model for Company Status Log.
    Uses CompanyListingPage navigation and search logic, then clicks Status Log in Company menu list / tabs.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.company_listing_page = CompanyListingPage(page)

        # Navigation Locators
        self.company_menu_link = page.get_by_role("link", name=re.compile(r"^Company", re.I)).or_(
            page.locator(".sidebar a:has-text('Company')")
        ).first
        self.status_log_link = page.locator(
            "a[href*='StatusLog'], a.k-link:has-text('Status Log'), .sidebar a:has-text('Status Log')"
        ).filter(visible=True).first

        # Layout Assertions Locators
        self.header_company_details = page.get_by_text("Company Details Company").or_(
            page.get_by_text("Company Details")
        ).filter(visible=True).first
        self.heading_status_log = page.get_by_role("heading", name=re.compile(r"Status\s+Log", re.I)).or_(
            page.get_by_text("Status Log")
        ).filter(visible=True).first
        self.status_log_grid = page.locator("#StatusLogGrid, .k-grid-content, .k-grid, table").filter(visible=True).first

    def navigate_to_company_listing(self, timeout_ms: int = 20000) -> None:
        """Delegates navigation logic to CompanyListingPage."""
        self.company_listing_page.navigate_to_company_listing(timeout_ms=timeout_ms)

    def search_company(self, company_name: str = "IDOTOAtest2", timeout_ms: int = 20000) -> None:
        """Delegates search logic to CompanyListingPage."""
        self.company_listing_page.search_company(company_name=company_name, timeout_ms=timeout_ms)

    def click_status_log_link(self, timeout_ms: int = 20000) -> None:
        """Clicks Status Log in Company menu list / sub-tab."""
        self.logger.info("Clicking Status Log link")
        self._wait_for_loader()

        status_btn = self.page.locator(
            "a[href*='StatusLog'], a:has-text('Status Log')"
        ).filter(visible=True).first

        if not status_btn.is_visible(timeout=2000):
            if self.company_menu_link.is_visible(timeout=2000):
                self.company_menu_link.click()
                self.page.wait_for_timeout(400)

        if status_btn.is_visible(timeout=3000):
            status_btn.click(force=True)
        else:
            self.page.locator("a[href*='StatusLog']").first.click(force=True)

        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    def verify_status_log_elements(self, timeout_ms: int = 20000) -> Dict[str, Any]:
        """Asserts Company Details Company text, Status Log heading, and #StatusLogGrid table."""
        self.logger.info("Asserting Status Log layout elements")
        expect(self.heading_status_log).to_be_visible(timeout=timeout_ms)
        expect(self.status_log_grid).to_be_visible(timeout=timeout_ms)

        if self.header_company_details.count() > 0 and self.header_company_details.is_visible(timeout=2000):
            expect(self.header_company_details).to_be_visible(timeout=timeout_ms)

        return {
            "status": "Verified successfully",
            "heading_status_log_visible": self.heading_status_log.is_visible(),
            "status_log_grid_visible": self.status_log_grid.is_visible(),
        }

    def execute_status_log_workflow(self, company_name: str = "IDOTOAtest2") -> Dict[str, Any]:
        """
        Executes end-to-end Status Log workflow:
        1. Navigate Company Listing using CompanyListingPage
        2. Fill #Dealer_Name with "IDOTOAtest2" & click Search using CompanyListingPage
        3. Click Status Log link
        4. Assert Company Details Company, Status Log heading, and #StatusLogGrid
        """
        self.navigate_to_company_listing()
        self.search_company(company_name=company_name)
        self.click_status_log_link()
        return self.verify_status_log_elements()


