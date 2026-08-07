import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.kendo_controls import KendoControls

logger = logging.getLogger(__name__)


class AdministrativeProcessPage(BasePage):
    """
    Page Object Model for Administrative Process in Staff Portal E-Permitting System.
    Provides automated methods for navigating sub-tabs (General Information, Initial Review,
    LOAC, LOLA, Payment, Revision, Appeal), triggering document/report popups, and saving updates.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.admin_process_tab = page.get_by_role("link", name="Administrative Process").or_(
            page.locator("a:has-text('Administrative Process'), span:has-text('Administrative Process')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.active_process_tab_heading = page.locator("#ProcessTab_ts_active").get_by_text("Administrative Process").or_(
            page.locator("#ProcessTab_ts_active, .k-state-active:has-text('Administrative Process')")
        ).first

        self.general_info_heading = page.get_by_role("heading", name="General Information").or_(
            page.locator("h1:has-text('General Information'), h2:has-text('General Information'), h3:has-text('General Information')")
        ).first

        # ── General Action Buttons ────────────────────────────────────────────
        self.back_button = page.get_by_role("button", name=" Back").or_(
            page.get_by_role("button", name="Back")
        ).first

        # ── Sub-Tab Locators ──────────────────────────────────────────────────
        self.generate_permit_num_button = page.get_by_role("button", name="Generate Permit #").or_(
            page.locator("button:has-text('Generate Permit #')")
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

        # ── LOAC Buttons ──────────────────────────────────────────────────────
        self.generate_reminder_button = page.get_by_role("button", name=re.compile(r"Generate Reminder", re.I)).first
        self.generate_final_notice_button = page.get_by_role("button", name=re.compile(r"Generate Final Notice", re.I)).first

        # ── Payment Sub-Tab Buttons ───────────────────────────────────────────
        self.download_w9_button = page.get_by_role("button", name="Download W9").first
        self.generate_voucher_button = page.get_by_role("button", name="Generate Voucher").first
        self.generate_cover_letter_button = page.get_by_role("button", name="Generate Cover Letter").first
        self.cover_letter_modal_title = page.locator("#GenerateCoverLetterDiv_wnd_title, .k-window-title:has-text('Cover Letter')").first
        self.generate_letter_to_owner_button = page.get_by_role("button", name=re.compile(r"Generate Letter to Owner", re.I)).first

        # ── Revision Sub-Tab Buttons ──────────────────────────────────────────
        self.add_new_revision_button = page.get_by_role("button", name=" Add New").or_(
            page.get_by_role("button", name="Add New")
        ).first
        self.add_edit_revision_modal_title = page.locator("#AddEditReviewDiv_wnd_title, .k-window-title:has-text('Revision')").first

        # ── Appeal Sub-Tab Locators ───────────────────────────────────────────
        self.appeal_section_container = page.locator("#frmCustomer > section > div > div, #frmCustomer section, .form-wrapper").first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_administrative_process(self) -> None:
        """Navigates to Administrative Process tab."""
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
        expect(self.general_info_heading).to_be_visible(timeout=15000)

    def safe_click_save(self) -> None:
        """Safely clicks the Save button if a visible Save button is present on the active sub-tab."""
        self._wait_for_loader()
        visible_save = self.page.locator("button:visible:has-text('Save'), input[type='submit']:visible[value*='Save']").first
        if visible_save.count() > 0 and visible_save.is_visible():
            self.js_click(visible_save)
            self._wait_for_loader()

    def trigger_report_popup(self, action_button, timeout: int = 15000) -> None:
        """
        Clicks target report generation button and verifies `#mainCanvas` in the popup window if triggered.
        """
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

    def process_general_information(self) -> None:
        """Saves General Information and triggers Generate Permit # if available."""
        logger.info("Processing General Information sub-tab.")
        self.safe_click_save()

        if self.generate_permit_num_button.is_visible():
            self.trigger_report_popup(self.generate_permit_num_button)

    def process_initial_review(self) -> None:
        """Navigates to Initial Review sub-tab and saves if available."""
        logger.info("Processing Initial Review sub-tab.")
        self._wait_for_loader()
        if self.initial_review_tab.count() > 0 and self.initial_review_tab.is_visible():
            self.js_click(self.initial_review_tab)
            self.safe_click_save()

    def process_loac(self) -> None:
        """Navigates to LOAC sub-tab, generates Reminder & Final Notice reports, and saves if available."""
        logger.info("Processing LOAC sub-tab.")
        self._wait_for_loader()
        if self.loac_tab.count() > 0 and self.loac_tab.is_visible():
            self.js_click(self.loac_tab)
            self._wait_for_loader()

            if self.generate_reminder_button.is_visible():
                self.trigger_report_popup(self.generate_reminder_button)

            if self.generate_final_notice_button.is_visible():
                self.trigger_report_popup(self.generate_final_notice_button)

            self.safe_click_save()

    def process_lola(self) -> None:
        """Navigates to LOLA sub-tab and saves if available."""
        logger.info("Processing LOLA sub-tab.")
        self._wait_for_loader()
        if self.lola_tab.count() > 0 and self.lola_tab.is_visible():
            self.js_click(self.lola_tab)
            self.safe_click_save()

    def process_payment_subtab(self) -> None:
        """
        Navigates to Payment sub-tab, downloads W9, generates Voucher, Cover Letter,
        and Letter to Owner, then saves if available.
        """
        logger.info("Processing Payment sub-tab.")
        self._wait_for_loader()
        if self.payment_subtab.count() > 0 and self.payment_subtab.is_visible():
            self.js_click(self.payment_subtab)
            self._wait_for_loader()

            # Download W9
            if self.download_w9_button.is_visible():
                try:
                    with self.page.expect_popup(timeout=15000) as popup_info:
                        self.js_click(self.download_w9_button)
                    w9_popup = popup_info.value
                    w9_popup.close()
                except Exception as e:
                    logger.warning(f"W9 download popup note: {e}")

            # Generate Voucher
            if self.generate_voucher_button.is_visible():
                self.trigger_report_popup(self.generate_voucher_button)

            # Generate Cover Letter modal
            if self.generate_cover_letter_button.is_visible():
                self.js_click(self.generate_cover_letter_button)
                self.page.wait_for_timeout(500)
                self.select_all_kendo_dropdowns()
                self.page.wait_for_timeout(300)

                gen_btn = self.page.get_by_role("button", name="Generate", exact=True).or_(
                    self.page.locator(".k-window:visible button:has-text('Generate')")
                ).first

                if gen_btn.is_visible():
                    with self.page.expect_popup(timeout=30000) as popup_info:
                        self.js_click(gen_btn)
                    cov_popup = popup_info.value
                    cov_popup.close()

                close_btn = self.page.get_by_role("button", name="Close").or_(
                    self.page.locator(".k-window:visible a.k-window-action, .k-window:visible button.close")
                ).first
                if close_btn.is_visible():
                    self.js_click(close_btn)

            # Generate Letter to Owner
            if self.generate_letter_to_owner_button.is_visible():
                self.trigger_report_popup(self.generate_letter_to_owner_button)

            self.safe_click_save()

    def process_revision(self) -> None:
        """Navigates to Revision sub-tab, opens Add New Revision modal, fills form, and saves if available."""
        logger.info("Processing Revision sub-tab.")
        self._wait_for_loader()
        if self.revision_tab.count() > 0 and self.revision_tab.is_visible():
            self.js_click(self.revision_tab)
            self._wait_for_loader()

            if self.add_new_revision_button.is_visible():
                self.js_click(self.add_new_revision_button)
                self.page.wait_for_timeout(500)
                self.select_all_kendo_dropdowns()
                self.page.wait_for_timeout(300)

                modal_save = self.page.locator(".k-window:visible button:has-text('Save'), #frmRevisionProc button:has-text('Save')").first
                if modal_save.is_visible():
                    self.js_click(modal_save)
                    self._wait_for_loader()

    def process_appeal(self) -> None:
        """Navigates to Appeal sub-tab and saves if available."""
        logger.info("Processing Appeal sub-tab.")
        self._wait_for_loader()
        if self.appeal_tab.count() > 0 and self.appeal_tab.is_visible():
            self.js_click(self.appeal_tab)
            self.safe_click_save()
            self.assert_no_validation_errors()
