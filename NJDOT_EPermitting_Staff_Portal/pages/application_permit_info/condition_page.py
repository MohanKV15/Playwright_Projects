import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ConditionPage(BasePage):
    """
    Page Object Model for Conditions tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.conditions_tab = page.get_by_role("link", name="Conditions").or_(
            page.locator("a:has-text('Conditions'), span:has-text('Conditions'), .k-tabstrip a:has-text('Conditions'), .k-tabstrip span:has-text('Conditions')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.conditions_heading = page.get_by_role("heading", name="Conditions").or_(
            page.locator("h1:has-text('Conditions'), h2:has-text('Conditions'), h3:has-text('Conditions')")
        ).first

        self.condition_radio_application = page.locator("#conditionRadio").get_by_text("Application").first
        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_conditions(self) -> None:
        """Navigates to Conditions tab."""
        logger.info("Navigating to Conditions tab.")
        self._wait_for_loader()
        if not self.conditions_heading.is_visible():
            self.js_click(self.conditions_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout."""
        logger.info("Verifying Conditions page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_condition_details(self) -> None:
        """Fills condition form details."""
        self.interact_with_conditions_form()

    def interact_with_conditions_form(self) -> None:
        """Interacts with condition form elements."""
        self._wait_for_loader()
        self.select_all_kendo_dropdowns()
        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
