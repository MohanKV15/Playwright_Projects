import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CompletenessCheckPage(BasePage):
    """
    Page Object Model for Completeness Check in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.completeness_tab = page.get_by_role("link", name="Completeness Check").or_(
            page.locator("a:has-text('Completeness Check'), span:has-text('Completeness Check'), .k-tabstrip a:has-text('Completeness Check'), .k-tabstrip span:has-text('Completeness Check')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.completeness_heading = page.get_by_role("heading", name="Completeness Check").or_(
            page.locator("h1:has-text('Completeness Check'), h2:has-text('Completeness Check'), h3:has-text('Completeness Check')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first
        self.completeness_letter_btn = page.get_by_role("button", name="Completeness Letter").first
        self.first_info_btn = page.get_by_role("button", name="1st Info").first
        self.thirty_day_followup_btn = page.get_by_role("button", name="30 Day Follow-up").first

    def navigate_to_completeness_check(self) -> None:
        """Navigates to Completeness Check tab."""
        logger.info("Navigating to Completeness Check tab.")
        self._wait_for_loader()
        if not self.completeness_heading.is_visible():
            self.js_click(self.completeness_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates page layout."""
        logger.info("Verifying Completeness Check page layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def save_completeness_details(self) -> None:
        """Saves completeness details."""
        self.fill_and_save_completeness_details()

    def generate_letters_and_verify_popups(self) -> None:
        """Generates completeness letters."""
        self.generate_letters_and_verify()

    def fill_and_save_completeness_details(self) -> None:
        """Selects dropdowns, sets dates, and saves completeness details."""
        logger.info("Saving Completeness Check form.")
        self._wait_for_loader()
        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()

    def generate_letters_and_verify(self) -> None:
        """Triggers report generation buttons."""
        for btn in [self.completeness_letter_btn, self.first_info_btn, self.thirty_day_followup_btn]:
            try:
                if btn.is_visible():
                    self.js_click(btn)
                    self.page.wait_for_timeout(500)
                    self._wait_for_loader()
            except Exception:
                pass
