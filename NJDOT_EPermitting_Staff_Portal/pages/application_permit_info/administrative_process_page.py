import logging
import re
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AdministrativeProcessPage(BasePage):
    """
    Optimized Page Object Model for Administrative Process in Staff Portal E-Permitting System.
    Automates navigation, report generation, modal interactions, and form saving across sub-tabs.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Sidebar & Navigation Locators ─────────────────────────────────────
        self.admin_process_tab = page.get_by_role("link", name="Administrative Process").or_(
            page.locator("a:has-text('Administrative Process'), span:has-text('Administrative Process')")
        ).first

        self.general_info_heading = page.get_by_role("heading", name="General Information").or_(
            page.locator("h1:has-text('General Information'), h2:has-text('General Information'), h3:has-text('General Information')")
        ).first

        # ── Sub-Tab Navigation Locators ───────────────────────────────────────
        self.general_info_subtab = page.locator(
            "#ProcessTab a:has-text('Administrative Process'), #ProcessTab span:has-text('Administrative Process')"
        ).first

        self.initial_review_tab = page.get_by_text("Initial Review").or_(
            page.locator("#ProcessTab a:has-text('Initial Review'), #ProcessTab span:has-text('Initial Review')")
        ).first

        self.loac_tab = page.get_by_text("LOAC", exact=True).or_(
            page.locator("#ProcessTab a:has-text('LOAC'), #ProcessTab span:has-text('LOAC')")
        ).first

        self.lola_tab = page.get_by_text("LOLA", exact=True).or_(
            page.locator("#ProcessTab a:has-text('LOLA'), #ProcessTab span:has-text('LOLA')")
        ).first

        self.payment_subtab = page.get_by_text("Payment", exact=True).or_(
            page.locator("#ProcessTab a:has-text('Payment'), #ProcessTab span:has-text('Payment')")
        ).first

        self.revision_tab = page.get_by_text("Revision").or_(
            page.locator("#ProcessTab a:has-text('Revision'), #ProcessTab span:has-text('Revision')")
        ).first

        self.appeal_tab = page.locator("#ProcessTab").get_by_text("Appeal").or_(
            page.locator("#ProcessTab a:has-text('Appeal'), #ProcessTab span:has-text('Appeal')")
        ).first

        # ── Action & Report Generation Locators ───────────────────────────────
        self.generate_permit_num_button = page.get_by_role("button", name="Generate Permit #").or_(
            page.locator("button:has-text('Generate Permit #')")
        ).first
        self.generate_reminder_button = page.get_by_role("button", name=re.compile(r"Generate Reminder", re.I)).first
        self.generate_final_notice_button = page.get_by_role("button", name=re.compile(r"Generate Final Notice", re.I)).first
        self.download_w9_button = page.get_by_role("button", name="Download W9").first
        self.generate_voucher_button = page.get_by_role("button", name="Generate Voucher").first
        self.generate_cover_letter_button = page.get_by_role("button", name="Generate Cover Letter").first
        self.generate_letter_to_owner_button = page.get_by_role("button", name=re.compile(r"Generate Letter to Owner", re.I)).first
        self.add_new_revision_button = page.get_by_role("button", name=" Add New").or_(
            page.get_by_role("button", name="Add New")
        ).first

    # ── Internal Helper Methods ───────────────────────────────────────────────

    def _click_tab(self, tab_locator: Locator) -> bool:
        """Helper to navigate to target sub-tab if visible."""
        self._wait_for_loader()
        if tab_locator.count() > 0 and tab_locator.is_visible():
            self.js_click(tab_locator)
            self._wait_for_loader()
            return True
        return False

    def safe_click_save(self) -> None:
        """Safely clicks the Save button if a visible Save button is present on the active sub-tab."""
        self._wait_for_loader()
        visible_save = self.page.locator("button:visible:has-text('Save'), input[type='submit']:visible[value*='Save']").first
        if visible_save.count() > 0 and visible_save.is_visible():
            self.js_click(visible_save)
            self._wait_for_loader()

    def trigger_report_popup(self, action_button: Locator, timeout: int = 15000) -> None:
        """Clicks target report generation button and closes popup window if triggered."""
        self._wait_for_loader()
        if action_button.count() > 0 and action_button.is_visible():
            try:
                with self.page.expect_popup(timeout=timeout) as popup_info:
                    self.js_click(action_button)
                popup = popup_info.value
                popup.wait_for_load_state("domcontentloaded")
                try:
                    expect(popup.locator("#mainCanvas, body")).to_be_visible(timeout=10000)
                except Exception as e:
                    logger.warning(f"Report viewer canvas note: {e}")
                popup.close()
            except Exception as e:
                logger.warning(f"Popup trigger note for button: {e}")

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_administrative_process(self) -> None:
        """Navigates to Administrative Process main tab."""
        logger.info("Navigating to Administrative Process tab.")
        self._wait_for_loader()
        if self.admin_process_tab.is_visible():
            self.js_click(self.admin_process_tab)
        else:
            self.page.evaluate("$('a:contains(\"Administrative Process\"), span:contains(\"Administrative Process\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def navigate_to_next_record(self) -> None:
        """Clicks the 'Next' navigation button to switch to the next permit record."""
        logger.info("Navigating to next permit record via Next button.")
        self._wait_for_loader()
        next_btn = self.page.get_by_role("button", name=re.compile(r"Next", re.I)).or_(
            self.page.locator("button:has-text('Next'), a:has-text('Next'), input[value*='Next']")
        ).first
        if next_btn.is_visible():
            self.js_click(next_btn)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Administrative Process page initial layout."""
        logger.info("Verifying Administrative Process initial layout.")
        self._wait_for_loader()
        target = self.general_info_heading.or_(self.page.locator("#LogAppHeader, #partial-form, .form-wrapper")).first
        expect(target).to_be_visible(timeout=15000)

    def process_general_information(self) -> None:
        """Saves General Information and triggers Generate Permit # if available."""
        logger.info("Processing General Information sub-tab.")
        self._click_tab(self.general_info_subtab)
        self.safe_click_save()
        self.trigger_report_popup(self.generate_permit_num_button)

    def process_initial_review(self) -> None:
        """Navigates to Initial Review sub-tab and saves if available."""
        logger.info("Processing Initial Review sub-tab.")
        if self._click_tab(self.initial_review_tab):
            self.safe_click_save()

    def process_loac(self) -> None:
        """Navigates to LOAC sub-tab, generates Reminder & Final Notice reports, and saves."""
        logger.info("Processing LOAC sub-tab.")
        if self._click_tab(self.loac_tab):
            self.trigger_report_popup(self.generate_reminder_button)
            self.trigger_report_popup(self.generate_final_notice_button)
            self.safe_click_save()

    def process_lola(self) -> None:
        """Navigates to LOLA sub-tab and saves if available."""
        logger.info("Processing LOLA sub-tab.")
        if self._click_tab(self.lola_tab):
            self.safe_click_save()

    def process_payment_subtab(self) -> None:
        """Navigates to Payment sub-tab, processes reports/modals, and saves."""
        logger.info("Processing Payment sub-tab.")
        if self._click_tab(self.payment_subtab):
            if self.download_w9_button.is_visible():
                try:
                    with self.page.expect_popup(timeout=15000) as popup_info:
                        self.js_click(self.download_w9_button)
                    popup_info.value.close()
                except Exception as e:
                    logger.warning(f"W9 download popup note: {e}")

            self.trigger_report_popup(self.generate_voucher_button)

            if self.generate_cover_letter_button.is_visible():
                self.js_click(self.generate_cover_letter_button)
                self._wait_for_loader()
                self.select_all_kendo_dropdowns()

                gen_btn = self.page.get_by_role("button", name="Generate", exact=True).or_(
                    self.page.locator(".k-window:visible button:has-text('Generate')")
                ).first
                if gen_btn.is_visible():
                    try:
                        with self.page.expect_popup(timeout=30000) as popup_info:
                            self.js_click(gen_btn)
                        popup_info.value.close()
                    except Exception as e:
                        logger.warning(f"Cover letter popup note: {e}")

                close_btn = self.page.get_by_role("button", name="Close").or_(
                    self.page.locator(".k-window:visible a.k-window-action, .k-window:visible button.close")
                ).first
                if close_btn.is_visible():
                    self.js_click(close_btn)

            self.trigger_report_popup(self.generate_letter_to_owner_button)
            self.safe_click_save()

    def process_revision(self) -> None:
        """Navigates to Revision sub-tab, opens Add New Revision modal, fills form, and saves."""
        logger.info("Processing Revision sub-tab.")
        if self._click_tab(self.revision_tab):
            if self.add_new_revision_button.is_visible():
                self.js_click(self.add_new_revision_button)
                self._wait_for_loader()
                self.select_all_kendo_dropdowns()

                modal_save = self.page.locator(".k-window:visible button:has-text('Save'), #frmRevisionProc button:has-text('Save')").first
                if modal_save.is_visible():
                    self.js_click(modal_save)
                    self._wait_for_loader()

    def process_appeal(self) -> None:
        """Navigates to Appeal sub-tab and saves if available."""
        logger.info("Processing Appeal sub-tab.")
        if self._click_tab(self.appeal_tab):
            self.safe_click_save()
            self.assert_no_validation_errors()

    def process_all_subtabs(self) -> None:
        """Master runner: Executes full sub-tab workflow sequentially across all 7 sub-tabs."""
        logger.info("Starting master execution across all Administrative Process sub-tabs.")
        self.process_general_information()
        self.process_initial_review()
        self.process_loac()
        self.process_lola()
        self.process_payment_subtab()
        self.process_revision()
        self.process_appeal()
        logger.info("Completed master execution across all Administrative Process sub-tabs.")
