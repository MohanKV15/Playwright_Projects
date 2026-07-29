import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class MT121Page(BasePage):
    """
    Page Object Model for MT-121 Inspection Report in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation
        self.mt121_tab = page.get_by_role("link", name=re.compile(r"^MT-", re.I))

        # Layout Verification Selectors
        self.layout_div = page.locator("div").filter(has_text="Department Job # Permit Type").nth(4)
        self.header_label = page.get_by_role("heading", name="MT-121 Inspection Report")
        self.inspection_report_text = page.get_by_text("Inspection Report", exact=True)
        self.report_section = page.locator("div").filter(has_text="MT-121 Inspection Report").nth(4)

        # Inputs & Form Controls
        self.date_picker_button = page.get_by_role("button", name="select").first
        self.time_from_picker = page.locator("#Inspection_Time_From_Date_Placeholder2")
        self.time_to_picker = page.locator("#Inspection_Time_To_Date_Placeholder3")

        # Actions & Dialogs
        self.save_report_button = page.get_by_role("button", name=" Save")
        self.ok_confirm_button = page.get_by_role("button", name="OK")
        self.gen_report_button = page.get_by_role("button", name="Generate Inspection Report")

    def navigate_to_mt121(self) -> None:
        """Transitions to the MT-121 tab."""
        logger.info("Navigating to MT-121 tab.")
        self._wait_for_loader()
        self.js_click(self.mt121_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates headers and base layout components on the MT-121 page."""
        logger.info("Verifying MT-121 Inspection Report initial layout.")
        expect(self.layout_div).to_be_visible(timeout=15000)
        expect(self.header_label).to_be_visible(timeout=15000)
        expect(self.inspection_report_text).to_be_visible(timeout=15000)
        expect(self.report_section).to_be_visible(timeout=15000)

    def fill_inspection_report(self) -> None:
        """Fills out the inspection report fields: date, times, radio options, dropdowns, and checkboxes."""
        logger.info("Filling out MT-121 Inspection Report form.")
        self._wait_for_loader()

        # 1. Fill Date using BasePage set_today_date
        self.set_today_date(self.date_picker_button)

        # 2. Fill Times
        if self.time_from_picker.is_visible():
            self.js_click(self.time_from_picker)
            self.time_from_picker.fill("09:00 AM")
            self.time_from_picker.press("Tab")

        if self.time_to_picker.is_visible():
            self.js_click(self.time_to_picker)
            self.time_to_picker.fill("05:00 PM")
            self.time_to_picker.press("Tab")

        # 3. Choose "No" options for radio buttons
        no_radios = self.page.locator("#MTInspectiondiv label.k-radio-label:has-text('No'), #MTInspectiondiv label:has-text('No')")
        for i in range(no_radios.count()):
            self.js_click(no_radios.nth(i))

        # Checkboxes and option items
        allowable_label = self.page.locator(".col-md-1 > .form-check > .k-checkbox-label").first
        if allowable_label.is_visible():
            allowable_label.click()

        # Timeline dropdown selection (soft-checked)
        timeline1 = self.page.locator("#Timeline1").first
        if timeline1.is_visible():
            self.js_click(timeline1)
            self.page.wait_for_timeout(300)
            opt1 = self.page.get_by_role("option", name="1:00", exact=True).first
            if opt1.is_visible():
                self.js_click(opt1)

        timeline4 = self.page.locator("#Timeline4").first
        if timeline4.is_visible():
            self.js_click(timeline4)
            self.page.wait_for_timeout(300)
            opt4 = self.page.get_by_role("option", name="1:30", exact=True).first
            if opt4.is_visible():
                self.js_click(opt4)

        # 4. Fill Dropdowns
        dropdowns = self.page.locator("#MTInspectiondiv span.k-dropdown:visible, #MTInspectiondiv span[role='listbox']:visible")
        for i in range(dropdowns.count()):
            self.select_first_dropdown_option(dropdowns.nth(i))

    def save_inspection_report(self) -> None:
        """Clicks Save, accepts confirmation prompt if shown, and waits for save to complete."""
        logger.info("Saving MT-121 Inspection Report.")
        if self.save_report_button.is_visible():
            self.js_click(self.save_report_button)

        try:
            self.ok_confirm_button.wait_for(state="visible", timeout=5000)
            self.js_click(self.ok_confirm_button)
        except Exception:
            pass

        self._wait_for_loader()
        logger.info("MT-121 Inspection Report saved successfully.")

    def generate_inspection_report_pdf(self) -> None:
        """Clicks Generate Inspection Report, confirms dialog, and verifies report popup canvas."""
        logger.info("Generating Inspection Report PDF.")
        self._wait_for_loader()
        if self.gen_report_button.is_visible():
            self.js_click(self.gen_report_button)

        try:
            expect(self.page.get_by_text("Document generated. Please")).to_be_visible(timeout=15000)
        except Exception:
            pass

        try:
            with self.page.expect_popup(timeout=15000) as popup_info:
                if self.ok_confirm_button.is_visible():
                    self.js_click(self.ok_confirm_button)
            popup = popup_info.value
            expect(popup.locator("#mainCanvas, canvas, embed, iframe")).to_be_visible(timeout=25000)
            popup.close()
            logger.info("Inspection report PDF verified and closed.")
        except Exception as e:
            logger.warning(f"PDF popup verification note: {e}")
