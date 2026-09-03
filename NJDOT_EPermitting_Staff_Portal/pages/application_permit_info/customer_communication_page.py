import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CustomerCommunicationPage(BasePage):
    """
    Page Object Model for Customer Communications tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.customer_comms_tab = page.get_by_role("link", name="Customer Communications").or_(
            page.locator("a:has-text('Customer Communications'), span:has-text('Customer Communications'), .k-tabstrip a:has-text('Customer Communications'), .k-tabstrip span:has-text('Customer Communications')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.comms_heading = page.get_by_role("heading", name="Customer Communications").or_(
            page.locator("h1:has-text('Customer Communications'), h2:has-text('Customer Communications'), h3:has-text('Customer Communications')")
        ).first

        self.add_new_button = page.get_by_role("button", name=" Add New").or_(page.get_by_role("button", name="Add New")).first
        self.message_input = page.get_by_role("textbox", name="Message")
        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_customer_communications(self) -> None:
        """Navigates to Customer Communications tab."""
        logger.info("Navigating to Customer Communications tab.")
        self._wait_for_loader()
        if not self.comms_heading.is_visible():
            self.js_click(self.customer_comms_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout."""
        logger.info("Verifying Customer Communications initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def add_customer_communication(self, comm_type: str = None, comm_status: str = None, review_person: str = None, message: str = "Automated Communication Message") -> None:
        """Adds customer communication log entry."""
        logger.info("Adding customer communication entry.")
        self._wait_for_loader()
        if self.add_new_button.is_visible():
            self.js_click(self.add_new_button)
            self._wait_for_loader()

        self.select_all_kendo_dropdowns()
        if self.message_input.is_visible():
            self.message_input.fill(message)

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
