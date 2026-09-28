import logging
from typing import Any, Dict
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.customer_action_items_page import (
    CustomerActionItemsPage as AppCustomerActionItemsPage,
)
from IDOT_ODA_Staff_Portal.pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage

logger = logging.getLogger(__name__)


class CustomerActionItemsPage(AppCustomerActionItemsPage):
    """
    Page Object Model representing the Customer Action Items module under Permit Transfer in the IDOT Staff Portal.

    Workflow & Inheritance:
    - Inherits form interaction methods (click_add_new, fill_customer_action_item_form, save_action_item,
      create_customer_action_item, verify_action_item_in_table, open_action_item_and_verify_details)
      from application_permit's CustomerActionItemsPage.
    - Activates Permit Transfer context via parent PermitTransferDetailsPage.
    - Navigates to Permit Transfer Listing, searches permit '016-503386', clicks 1st record row (row_index=0).
    - Clicks 'Customer Action Items' under Permit Transfer sidebar menu.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.permit_transfer_details = PermitTransferDetailsPage(page)

        # Permit Transfer Specific Locators
        self.sidebar_action_items_link = page.locator(
            ".sidebar a[href*='4319TransfCustCommListingStaffFull'], .sidebar a:has-text('Customer Action Items')"
        ).or_(
            page.get_by_role("link", name="Customer Action Items")
        ).last

        self.text_transfer_details_permit = page.get_by_text("Transfer Details Permit").or_(
            page.get_by_text("Transfer Details")
        ).or_(
            page.locator(".card-header:has-text('Transfer Details'), .page-header:has-text('Transfer Details'), div:has-text('Transfer Details')")
        ).first

        self.heading_customer_communication = page.get_by_role("heading", name="Customer Communication").or_(
            page.get_by_text("Customer Communication")
        ).first

        self.grid_content = page.locator(".k-grid-content, #gridCustComm, table.k-selectable").first

    def navigate_to_customer_action_items(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """
        Activates Permit Transfer session via parent PermitTransferDetailsPage:
        1. Navigates to Permit Transfer Listing page.
        2. Searches permit number ('016-503386').
        3. Clicks 1st record row (row_index=0).
        4. Clicks 'Customer Action Items' sub-link under Permit Transfer sidebar.
        5. Verifies 'Transfer Details', 'Customer Communication', and grid content visibility.
        """
        self.logger.info("Calling parent PermitTransferDetailsPage to activate session for permit: %s", permit_number)
        self.permit_transfer_details.navigate_to_permit_transfer_listing()
        self.permit_transfer_details.search_permit_for_transfer(permit_number=permit_number)
        self.permit_transfer_details.select_record_by_index(row_index=row_index)

        self.logger.info("Clicking 'Customer Action Items' sidebar sub-link under Permit Transfer")
        if self.sidebar_action_items_link.is_visible(timeout=3000):
            self.sidebar_action_items_link.click(force=True)
        else:
            self.logger.info("Fallback navigation to 4319TransfCustCommListingStaffFull")
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319TransfCustCommListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass

        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.verify_customer_action_items_page_loaded(timeout_ms=timeout_ms)

    def verify_customer_action_items_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Validates page navigation by checking core Permit Transfer headings and grid content."""
        self.logger.info("Verifying Customer Action Items page elements and headings")
        expect(self.text_transfer_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_customer_communication).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

    def execute_customer_action_items_workflow(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
        attach_document: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end Customer Action Items workflow for Permit Transfer:
        1. Navigate Permit Transfer -> search permit -> click 1st record row -> click Customer Action Items.
        2. Create Customer Action Item (1st dropdown options, Faker message, attachment).
        3. Verify record in listing table.
        4. Re-open record and verify details view.
        """
        self.navigate_to_customer_action_items(permit_number=permit_number, row_index=row_index)
        saved_data = self.create_customer_action_item(attach_document=attach_document)
        table_row = self.verify_action_item_in_table()
        self.open_action_item_and_verify_details(table_row)

        return {
            "status": "Verified successfully",
            "permit_number": permit_number,
            "row_index": row_index,
            "saved_data": saved_data,
        }
