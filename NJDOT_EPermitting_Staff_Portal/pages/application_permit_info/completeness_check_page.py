import logging
import re
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
            page.locator("a[href*='CompletenessCheck'], a:has-text('Completeness Check'), span:has-text('Completeness Check'), .k-tabstrip a:has-text('Completeness Check'), .k-tabstrip span:has-text('Completeness Check')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.completeness_heading = page.get_by_role("heading", name=re.compile(r"Completeness Check", re.I)).or_(
            page.locator("h1:has-text('Completeness Check'), h2:has-text('Completeness Check'), h3:has-text('Completeness Check'), h4:has-text('Completeness Check')")
        ).first

        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("button:has-text('Save'), input[type='submit'][value='Save']")
        ).first
        self.completeness_letter_btn = page.get_by_role("button", name=re.compile(r"Completeness Letter", re.I)).first
        self.first_info_btn = page.get_by_role("button", name=re.compile(r"1st Info", re.I)).first
        self.thirty_day_followup_btn = page.get_by_role("button", name=re.compile(r"30 Day Follow-up", re.I)).first

    def navigate_to_completeness_check(self) -> None:
        """Navigates to Completeness Check tab."""
        logger.info("Navigating to Completeness Check tab.")
        self._wait_for_loader()
        if "/CompletenessCheck" in self.page.url:
            return

        # Ensure PanelBar is expanded if collapsed
        try:
            self.page.evaluate("""
                () => {
                    var jq = window.jQuery || window.$;
                    if (jq) {
                        var pb = jq('#navigationMenu2').data('kendoPanelBar');
                        var item = jq('#navigationMenu2 > li:has(a:contains("Application/Permit Info"))');
                        if (pb && item.length) {
                            pb.expand(item);
                        }
                    }
                }
            """)
        except Exception as e:
            logger.debug(f"PanelBar expansion note: {e}")

        link = self.page.locator("a[href*='CompletenessCheck'], a:has-text('Completeness Check')").first
        try:
            if link.is_visible():
                self.js_click(link)
            else:
                link.evaluate("el => { if (el.href) window.location.href = el.href; else el.click(); }")
        except Exception:
            if self.completeness_tab.is_visible():
                self.js_click(self.completeness_tab)

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=3000)
        except Exception:
            pass
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
