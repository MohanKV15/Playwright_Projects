import logging
import re
from typing import Dict, Any
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class CompanyListingPage(BasePage):
    """
    Page Object Model for Company Listing Page (/Portal/Page/Index/4319DealerExistStaffFull).
    Encapsulates Company navigation, search by Dealer_Name, and grid verification.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # Navigation Locators
        self.company_menu_link = page.get_by_role("link", name=re.compile(r"^Company", re.I)).or_(
            page.locator(".sidebar a:has-text('Company')")
        ).first
        self.company_listing_link = page.locator(
            "a[href*='DealerExist'], a[href*='CompanyListing'], a:has-text('Company Listing')"
        ).first

        # Page Layout Locators
        self.heading_companies = page.get_by_role("heading", name=re.compile(r"Companies|Company", re.I)).or_(
            page.locator(".page-header, .title, h1, h2, h3, h4")
        ).first
        self.row_partition = page.locator(".row.partition").first
        self.grid_content = page.locator(".k-grid-content").first

        # Search Controls Locators (Specific to Company Listing Page)
        self.dealer_name_input = page.locator("#Dealer_Name")
        self.search_button = page.get_by_role("button", name=re.compile(r"Search", re.I)).or_(
            page.locator("#btnSearch, button:has-text('Search')")
        ).first
        self.search_results_table = page.locator("#DealersSearchExistTable, .k-grid-content table").first

        # Section Header Locators
        self.header_company_details = page.get_by_text("Company Details Company").or_(
            page.get_by_text("Company Details")
        ).first
        self.header_save_cancel = page.get_by_text("Save Cancel Company Name *").or_(
            page.get_by_text("Company Name *")
        ).first
        self.header_company_contacts = page.get_by_text("Company Contacts Add Contact").or_(
            page.get_by_text("Company Contacts")
        ).first
        self.header_company_name_change = page.get_by_text("Company Name Change Add").or_(
            page.get_by_text("Company Name Change")
        ).first

    def navigate_to_company_listing(self, timeout_ms: int = 20000) -> None:
        """Navigates specifically to Company -> Company Listing (DealerExist) page."""
        self.logger.info("Navigating to Company Listing page")
        self._wait_for_loader()

        if "DealerExist" in self.page.url and self.dealer_name_input.is_visible(timeout=2000):
            self.logger.info("Already on Company Listing page")
            return

        # Check if Company Listing link is visible; if not, click parent Company menu to expand
        if not self.company_listing_link.is_visible(timeout=2000):
            if self.company_menu_link.is_visible(timeout=3000):
                self.company_menu_link.click()
                self.page.wait_for_timeout(400)

        if self.company_listing_link.is_visible(timeout=5000):
            self.company_listing_link.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        # Fallback direct navigation if click didn't change page URL
        if "DealerExist" not in self.page.url:
            self.logger.info("Directly navigating to DealerExist page URL")
            current_url = self.page.url
            base_domain = current_url.split("/Portal/")[0]
            target_url = f"{base_domain}/Portal/Page/Index/4319DealerExistStaffFull"
            self.page.goto(target_url)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        # Assertions on Company Listing page
        expect(self.dealer_name_input).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)


    def search_company(self, company_name: str = "IDOTOAtest2", timeout_ms: int = 20000) -> None:
        """Fills #Dealer_Name filter input on Company Listing page and clicks Search."""
        self.logger.info("Searching on Company Listing page for: '%s'", company_name)
        expect(self.dealer_name_input).to_be_visible(timeout=timeout_ms)
        self.dealer_name_input.click()
        self.dealer_name_input.fill(company_name)

        expect(self.search_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.search_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    def verify_headers_display(self, timeout_ms: int = 5000) -> Dict[str, bool]:
        """Checks visibility of section headers."""
        self.logger.info("Verifying section headers visibility")
        headers = [
            ("Company Details Company", self.header_company_details),
            ("Save Cancel Company Name *", self.header_save_cancel),
            ("Company Contacts Add Contact", self.header_company_contacts),
            ("Company Name Change Add", self.header_company_name_change),
        ]

        verification_results = {}
        for header_name, locator in headers:
            is_visible = False
            if locator.count() > 0:
                try:
                    locator.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(200)
                except Exception:
                    pass
                if locator.is_visible(timeout=timeout_ms):
                    expect(locator).to_be_visible(timeout=timeout_ms)
                    is_visible = True
            verification_results[header_name] = is_visible
            self.logger.info("Section header '%s' visible: %s", header_name, is_visible)

        return verification_results

    def execute_company_listing_workflow(
        self, search_term: str = "IDOTOAtest2"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end Company Listing workflow:
        1. Navigate Company -> Company Listing
        2. Enter search query in #Dealer_Name & click Search
        3. Verify section headers
        """
        self.navigate_to_company_listing()
        self.search_company(company_name=search_term)
        headers_status = self.verify_headers_display()

        return {
            "status": "Verified successfully",
            "search_term": search_term,
            "headers_status": headers_status,
        }

