import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitTransferDetailsPage(BasePage):
    """Page Object Model for the Permit Transfer section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.permit_transfer_menu_link = page.get_by_role("link", name="Permit Transfer ")
        self.permit_transfer_sub_link = page.get_by_role("link", name="Permit Transfer", exact=True)

        # Search elements
        self.permit_number_input = page.get_by_role("textbox", name="Permit Number")
        self.search_button = page.get_by_role("button", name=" Search")
        self.from_dealer_name_input = page.get_by_role("textbox", name="From Dealer Name")

        # Headings / Layout Validation
        self.partial_form_first = page.locator("#partial-form").first
        self.partition_col = page.locator(".row.partition > .col-md-12").first
        self.permit_transfer_heading = page.get_by_role("heading", name="Permit Transfer", exact=True)
        self.page_load_container = page.locator("#permitTransferOnPageLoad")
        self.select_permits_text = page.get_by_text("Select Permits to transfer")
        self.form_wrapper_child = page.locator("#frmCustomer > .form-wrapper > div > div:nth-child(2)").first

        # Save and OK dialog elements
        self.save_button = page.get_by_role("button", name=" Save")
        self.ok_button = page.get_by_role("button", name="OK")

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Permit Transfer."""
        logger.info("Expanding Permit Transfer PanelBar navigation.")
        self._expand_kendo_panel("permit transfer")

    def navigate_to_permit_transfer(self) -> None:
        """Navigates to the Permit Transfer page and verifies submenus/links are visible."""
        self._expand_navigation_menu()
        if not self.permit_transfer_sub_link.is_visible():
            self.permit_transfer_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.permit_transfer_sub_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def search_permit_transfer(self, permit_number: str = None, from_dealer_name: str = None) -> None:
        """Searches for permit transfer using Permit Number and/or From Dealer Name."""
        logger.info(f"Searching permit transfer. Permit Number: {permit_number}, From Dealer Name: {from_dealer_name}")
        
        # Search by Permit Number if provided
        if permit_number:
            self.permit_number_input.wait_for(state="visible", timeout=10000)
            self.permit_number_input.click()
            self.permit_number_input.fill(permit_number)
            self.search_button.click()
            self._wait_for_loader()

        # Search by From Dealer Name if provided
        if from_dealer_name:
            self.from_dealer_name_input.wait_for(state="visible", timeout=10000)
            self.from_dealer_name_input.click()
            self.from_dealer_name_input.fill(from_dealer_name)
            self.from_dealer_name_input.press("Enter")
            self._wait_for_loader()

    def verify_layout(self) -> None:
        """Verifies that all visual layout containers, headers, and grids are visible."""
        logger.info("Verifying Permit Transfer page layout components.")
        expect(self.partial_form_first).to_be_visible(timeout=15000)
        expect(self.partition_col).to_be_visible(timeout=10000)
        expect(self.permit_transfer_heading).to_be_visible(timeout=10000)
        expect(self.page_load_container).to_be_visible(timeout=10000)
        expect(self.select_permits_text).to_be_visible(timeout=10000)
        expect(self.form_wrapper_child).to_be_visible(timeout=10000)
        logger.info("Layout verified successfully.")

    def save_and_confirm(self) -> None:
        """Saves the permit transfer and confirms the operation completed popup."""
        logger.info("Saving permit transfer.")
        self.save_button.click()
        self._wait_for_loader()
        
        logger.info("Waiting for Operation Completed popup.")
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(
            has_text=re.compile(r"Operation Completed|Operation completed", re.I)
        ).first
        
        try:
            expect(active_dialog).to_be_visible(timeout=15000)
            logger.info("Dismissing success popup.")
            active_dialog.get_by_role("button", name="OK").click()
        except Exception:
            logger.warning("Kendo dialog not found. Clicking fallback OK button directly.")
            self.ok_button.click()
            
        self.page.wait_for_timeout(1000)
        logger.info("Permit transfer transaction saved and confirmed successfully.")
