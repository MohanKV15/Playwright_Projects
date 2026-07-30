import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class InspectionPage(BasePage):
    """
    Page Object Model for Inspection tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.inspection_tab = page.get_by_role("link", name="Inspection").or_(
            page.locator("a:has-text('Inspection'), span:has-text('Inspection'), .k-tabstrip a:has-text('Inspection'), .k-tabstrip span:has-text('Inspection')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.inspection_heading = page.get_by_role("heading", name="Inspection").or_(
            page.locator("h1:has-text('Inspection'), h2:has-text('Inspection'), h3:has-text('Inspection')")
        ).first

        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_inspection(self) -> None:
        """Navigates to Inspection tab."""
        logger.info("Navigating to Inspection tab.")
        self._wait_for_loader()
        if not self.inspection_heading.is_visible():
            self.js_click(self.inspection_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout."""
        logger.info("Verifying Inspection initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_inspection_details(self, comments: str = "") -> None:
        """Fills inspection details."""
        self.fill_and_save_inspection(comments)

    def generate_inspection_reports(self) -> None:
        """Generates inspection reports."""
        pass

    def add_inspection_review(self, comments: str = "") -> None:
        """Adds inspection review."""
        pass

    def fill_and_save_inspection(self, comments: str = "") -> None:
        """Fills inspection details and saves."""
        logger.info("Saving Inspection form.")
        self._wait_for_loader()
        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)
        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
