import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AppealPage(BasePage):
    """
    Page Object Model for Appeal tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.appeal_tab = page.get_by_role("link", name="Appeal").or_(
            page.locator("a:has-text('Appeal'), span:has-text('Appeal'), .k-tabstrip a:has-text('Appeal'), .k-tabstrip span:has-text('Appeal')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.appeal_heading = page.get_by_role("heading", name="Appeal").or_(
            page.locator("h1:has-text('Appeal'), h2:has-text('Appeal'), h3:has-text('Appeal')")
        ).first

        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_appeal(self) -> None:
        """Navigates to Appeal tab."""
        logger.info("Navigating to Appeal tab.")
        self._wait_for_loader()
        if not self.appeal_heading.is_visible():
            self.js_click(self.appeal_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout."""
        logger.info("Verifying Appeal initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_appeal_details(self, comments: str = "") -> None:
        """Fills appeal form details and saves."""
        self.fill_and_save_appeal(comments)

    def fill_and_save_appeal(self, comments: str = "") -> None:
        """Fills appeal details and saves."""
        logger.info("Saving Appeal form.")
        self._wait_for_loader()
        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)
        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
