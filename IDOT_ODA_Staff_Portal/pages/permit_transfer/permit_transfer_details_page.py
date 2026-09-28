import logging
import re
from typing import Dict, Optional, Any
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown, KendoControls

logger = logging.getLogger(__name__)


class PermitTransferDetailsPage(BasePage):
    """
    Page Object Model representing the Permit Transfer Details module in the IDOT Staff Portal.
    Encapsulates sidebar navigation (Dashboard -> Permit Transfer), permit record searching,
    table row editing (always selecting 1st record by default), and detail heading validations.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_controls = KendoControls(page)

        # 1. Navigation & Listing Page Locators
        self.sidebar_permit_transfer_parent = page.get_by_role("link", name="Permit Transfer ").or_(
            page.locator(".sidebar > ul > li > a:has-text('Permit Transfer')")
        ).first

        self.sidebar_permit_transfer_sub = page.get_by_role("link", name="Permit Transfer", exact=True).or_(
            page.locator(".sidebar .sub-menu a:has-text('Permit Transfer')")
        ).last

        self.listing_col_heading = page.locator(".col-md-5").first
        self.text_permit_transfer_enter = page.get_by_text("Permit Transfer (Enter in one").or_(
            page.get_by_text("Permit Transfer")
        ).first

        # 2. Search & Table Locators
        self.permit_for_transfer_input = page.locator("#PermitForTransfer, [name='PermitForTransfer']").first
        self.btn_search = page.locator("#btnSearch, button:has-text('Search')").or_(
            page.get_by_role("button", name=re.compile(r"Search", re.I))
        ).first
        self.permit_transfer_table = page.locator("#PermitTransferTable").first
        self.table_rows = page.locator("#PermitTransferTable tbody tr")

        # 3. Details Page Verification Headings
        self.heading_permit_transfer_details = page.get_by_text("Permit Transfer Details Save").or_(
            page.get_by_text("Permit Transfer Details")
        ).first
        self.heading_permit_transfer_transfer = page.get_by_text("Permit Transfer Transfer").or_(
            page.get_by_text("Permit Transfer")
        ).first
        self.heading_select_permits_to_transfer = page.get_by_text("Select Permits to transfer").first

    def navigate_to_permit_transfer_listing(self, timeout_ms: int = 20000) -> None:
        """
        Navigates to Dashboard first to ensure active ASP.NET session parameters,
        then clicks 'Permit Transfer ' parent link and 'Permit Transfer' exact sub-link.
        """
        if self.listing_col_heading.is_visible(timeout=1000) and self.text_permit_transfer_enter.is_visible(timeout=1000):
            self.logger.info("Already on Permit Transfer Listing page")
            return

        self.logger.info("Navigating to Dashboard prior to clicking Permit Transfer sidebar link")
        self._wait_for_loader()

        dash_link = self.page.get_by_role("link", name="Dashboard").or_(
            self.page.locator(".sidebar a:has-text('Dashboard'), a[href*='Dashboard']")
        ).first

        if dash_link.is_visible(timeout=3000):
            dash_link.click(force=True)
            self.page.wait_for_timeout(300)
            self._wait_for_loader()

        self.logger.info("Clicking 'Permit Transfer ' parent sidebar link")
        if self.sidebar_permit_transfer_parent.is_visible(timeout=5000):
            self.sidebar_permit_transfer_parent.click(force=True)
            self.page.wait_for_timeout(300)

        self.logger.info("Clicking exact 'Permit Transfer' sub-link")
        if self.sidebar_permit_transfer_sub.is_visible(timeout=5000):
            self.sidebar_permit_transfer_sub.click(force=True)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        if "PermitTransferListing" not in self.page.url:
            self.logger.info("Fallback navigation to 4319PermitTransferListingStaffFull with domcontentloaded")
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319PermitTransferListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        expect(self.listing_col_heading).to_be_visible(timeout=timeout_ms)
        expect(self.text_permit_transfer_enter).to_be_visible(timeout=timeout_ms)

    def search_permit_for_transfer(self, permit_number: str = "016-503386", timeout_ms: int = 20000) -> None:
        """Fills '#PermitForTransfer' input field and clicks Search button."""
        self.logger.info("Searching for permit number: '%s'", permit_number)
        expect(self.permit_for_transfer_input).to_be_visible(timeout=timeout_ms)
        self.permit_for_transfer_input.click()
        self.permit_for_transfer_input.fill(permit_number)

        expect(self.btn_search).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.btn_search)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        expect(self.permit_transfer_table).to_be_visible(timeout=timeout_ms)

    def select_record_by_index(self, row_index: int = 0, timeout_ms: int = 20000) -> None:
        """
        Selects and clicks the edit button (#btnStfEdit) on the specified row index (default 1st record: row_index=0).
        """
        self.logger.info("Selecting row record at index %d (1st record by default)", row_index)
        expect(self.permit_transfer_table).to_be_visible(timeout=timeout_ms)

        target_row = self.table_rows.nth(row_index)
        expect(target_row).to_be_visible(timeout=timeout_ms)

        edit_btn = target_row.locator("#btnStfEdit, button:has-text('Edit'), a:has-text('Edit'), .btnStfEdit").first
        expect(edit_btn).to_be_visible(timeout=timeout_ms)
        self.safe_click(edit_btn)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    def verify_details_page_headings(self, timeout_ms: int = 20000) -> None:
        """Validates that the details page has loaded by verifying all key headings."""
        self.logger.info("Verifying Permit Transfer Details page headings")
        expect(self.heading_permit_transfer_details).to_be_visible(timeout=timeout_ms)
        expect(self.heading_permit_transfer_transfer).to_be_visible(timeout=timeout_ms)
        expect(self.heading_select_permits_to_transfer).to_be_visible(timeout=timeout_ms)

    def execute_permit_transfer_details_workflow(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end Permit Transfer record lookup workflow:
        1. Navigate to Permit Transfer listing page (via Dashboard).
        2. Search permit number ('016-503386').
        3. Always select 1st record (row_index=0) in the table.
        4. Verify navigation to Details page and validate page headings.
        """
        self.navigate_to_permit_transfer_listing()
        self.search_permit_for_transfer(permit_number=permit_number)
        self.select_record_by_index(row_index=row_index)
        self.verify_details_page_headings()

        return {
            "status": "Verified successfully",
            "permit_number": permit_number,
            "selected_row_index": row_index,
        }
