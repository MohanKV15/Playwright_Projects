import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitDetailsPage(BasePage):
    """
    Page Object Model for Permit Details tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation / Tabs
        self.permit_details_tab = page.get_by_role("link", name="Permit Details").or_(
            page.locator("a:has-text('Permit Details'), span:has-text('Permit Details'), .k-tabstrip a:has-text('Permit Details'), .k-tabstrip span:has-text('Permit Details')")
        ).first

        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.permit_details_heading = page.get_by_role("heading", name="Permit Details").or_(
            page.locator("h1:has-text('Permit Details'), h2:has-text('Permit Details'), h3:has-text('Permit Details')")
        ).first
        self.documents_log_heading = page.locator("#divfrmLog, #LogDynGridLoad, h1, h2, h3, h4, h5, h6").get_by_text("Documents and Log").first

        # Form Selectors
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_permit_details(self) -> None:
        """Transitions to the Permit Details tab."""
        logger.info("Navigating to Permit Details tab.")
        self._wait_for_loader()
        if not self.permit_details_heading.is_visible():
            self.js_click(self.permit_details_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout and headers on the Permit Details page."""
        logger.info("Verifying Permit Details page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_permit_details(self, comments: str = "Automated Permit Details Entry") -> None:
        """Fills out fields and saves permit details."""
        self.fill_and_save_permit_details(comments)

    def fill_and_save_permit_details(self, comments: str = "Automated Permit Details Entry") -> None:
        """Fills out fields and saves permit details."""
        logger.info("Filling permit details form fields.")
        self._wait_for_loader()

        self.select_all_kendo_dropdowns()

        if self.comments_input.is_visible():
            self.comments_input.fill(comments)

        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
        logger.info("Permit Details saved successfully.")
