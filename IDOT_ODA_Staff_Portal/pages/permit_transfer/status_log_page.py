import logging
from typing import Any, Dict
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.status_log_page import (
    StatusLogPage as AppStatusLogPage,
)
from IDOT_ODA_Staff_Portal.pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage

logger = logging.getLogger(__name__)


class StatusLogPage(AppStatusLogPage):
    """
    Page Object Model representing the Status Log module under Permit Transfer in the IDOT Staff Portal.
    Inherits form interaction capabilities and Kendo control helpers from application_permit's StatusLogPage.

    Workflow:
    - Navigates to Permit Transfer Details view via parent PermitTransferDetailsPage workflow.
    - Clicks 'Status Log' sidebar sub-link under Permit Transfer.
    - Verifies 'Transfer Details Permit' / 'Transfer Details', 'Status Log' heading, and '.k-grid-content' visibility.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.permit_transfer_details = PermitTransferDetailsPage(page)

        # Permit Transfer Specific Locators
        self.sidebar_status_log_link = page.locator(
            ".sidebar a[href*='4319TransfStatusLogListingStaffFull'], .sidebar a:has-text('Status Log')"
        ).or_(
            page.get_by_role("link", name="Status Log")
        ).last

        self.text_transfer_details_permit = page.get_by_text("Transfer Details Permit").or_(
            page.get_by_text("Transfer Details")
        ).or_(
            page.get_by_text("Permit Transfer Details")
        ).first

        self.heading_status_log = page.get_by_role("heading", name="Status Log").filter(visible=True).or_(
            page.get_by_text("Status Log").filter(visible=True)
        ).first

        self.grid_content = page.locator(".k-grid-content, #gridStatusLog, #StatusLogGrid, table.k-selectable").filter(visible=True).first

    def navigate_to_status_log(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """
        Executes parent PermitTransferDetailsPage workflow:
        1. Navigates to Permit Transfer Listing page (via Dashboard).
        2. Searches permit number ('016-503386').
        3. Selects 1st record row (row_index=0).
        4. Verifies Permit Transfer Details headings.
        5. Clicks 'Status Log' link under Permit Transfer sidebar.
        6. Verifies 'Transfer Details Permit', 'Status Log' heading, and '.k-grid-content' visibility.
        """
        self.logger.info("Executing parent PermitTransferDetailsPage workflow for permit: %s", permit_number)
        self.permit_transfer_details.execute_permit_transfer_details_workflow(
            permit_number=permit_number,
            row_index=row_index,
        )

        self.logger.info("Clicking 'Status Log' sidebar sub-link under Permit Transfer")
        if not self.sidebar_status_log_link.is_visible(timeout=3000):
            if self.permit_transfer_details.sidebar_permit_transfer_parent.is_visible(timeout=2000):
                self.permit_transfer_details.sidebar_permit_transfer_parent.click(force=True)
                self.page.wait_for_timeout(300)

        if self.sidebar_status_log_link.is_visible(timeout=3000):
            self.sidebar_status_log_link.click(force=True)
        else:
            self.logger.info("Fallback navigation to 4319TransfStatusLogListingStaffFull")
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319TransfStatusLogListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass

        self.page.wait_for_timeout(800)
        self._wait_for_loader()

        self.verify_status_log_page_loaded(timeout_ms=timeout_ms)

    def verify_status_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Validates page navigation by checking 'Transfer Details Permit' / 'Transfer Details',
        'Status Log' heading, and '.k-grid-content' visibility.
        """
        self.logger.info("Verifying Status Log page elements and headings")
        expect(self.text_transfer_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_status_log).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

    def execute_status_log_workflow(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end Status Log navigation and verification workflow for Permit Transfer.
        """
        self.navigate_to_status_log(permit_number=permit_number, row_index=row_index)

        return {
            "status": "Verified successfully",
            "permit_number": permit_number,
            "row_index": row_index,
        }

