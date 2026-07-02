import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class MT121Page(BasePage):
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
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.complete_log_status = page.locator("#CompleteLog > div:nth-child(2)")

    def navigate_to_mt121(self) -> None:
        """Transitions to the MT-121 tab."""
        logger.info("Navigating to MT-121 tab.")
        self._wait_for_loader()
        self.js_click(self.mt121_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates headers and base layout components on the MT-121 page."""
        logger.info("Verifying MT-121 Inspection Report page initial layout.")
        expect(self.layout_div).to_be_visible(timeout=15000)
        expect(self.header_label).to_be_visible(timeout=15000)
        expect(self.inspection_report_text).to_be_visible(timeout=15000)
        expect(self.report_section).to_be_visible(timeout=15000)

    def fill_inspection_report(self) -> None:
        """Fills out the inspection report fields: date, times, radio options, dropdowns, and checkboxes."""
        logger.info("Filling out MT-121 Inspection Report form.")
        self._wait_for_loader()
        
        # 1. Fill Date
        self.select_today_in_calendar(self.date_picker_button)
        
        # 2. Fill Times
        self.js_click(self.time_from_picker)
        self.time_from_picker.fill("09:00 AM")
        self.time_from_picker.press("Tab")
        
        self.js_click(self.time_to_picker)
        self.time_to_picker.fill("05:00 PM")
        self.time_to_picker.press("Tab")
        
        # 3. Choose "No" options for radio buttons
        no_radios = self.page.locator("#MTInspectiondiv label.k-radio-label:has-text('No'), #MTInspectiondiv label:has-text('No')")
        no_count = no_radios.count()
        logger.info(f"Clicking {no_count} 'No' option radio labels.")
        for i in range(no_count):
            self.js_click(no_radios.nth(i))
            
        # Click other specific form-check / radio / checkbox items requested in codegen
        form_check_first = self.page.locator(".col-md-4 > .form-check").first
        if form_check_first.is_visible():
            self.js_click(form_check_first)
            
        na_label = self.page.locator("#MTInspectiondiv label.k-radio-label:has-text('N/A'), #MTInspectiondiv label:has-text('N/A')").first
        if na_label.is_visible():
            self.js_click(na_label)
            
        radio_child_34 = self.page.locator("div:nth-child(34) > .form-check > .k-radio-label")
        if radio_child_34.is_visible():
            self.js_click(radio_child_34)
            
        radio_child_3_first = self.page.locator("div:nth-child(3) > .form-check > .k-radio-label").first
        if radio_child_3_first.is_visible():
            self.js_click(radio_child_3_first)
            
        radio_child_42_third = self.page.locator("div:nth-child(42) > .row > div:nth-child(3) > .form-check > .k-radio-label")
        if radio_child_42_third.is_visible():
            self.js_click(radio_child_42_third)
            
        checkbox_first = self.page.locator(".col-md-1 > .form-check > .k-checkbox-label").first
        if checkbox_first.is_visible():
            self.js_click(checkbox_first)
            
        headwalls_label = self.page.locator("#MTInspectiondiv label:has-text('Headwalls'), #MTInspectiondiv span:has-text('Headwalls'), #MTInspectiondiv .k-radio-label:has-text('Headwalls')").first
        if headwalls_label.is_visible():
            self.js_click(headwalls_label)
            
        trees_label = self.page.locator("#MTInspectiondiv label:has-text('Trees'), #MTInspectiondiv span:has-text('Trees'), #MTInspectiondiv .k-radio-label:has-text('Trees')").first
        if trees_label.is_visible():
            self.js_click(trees_label)
            
        # 4. Fill Dropdowns
        dropdowns = self.page.locator("#MTInspectiondiv span.k-dropdown:visible, #MTInspectiondiv span[role='listbox']:visible")
        drop_count = dropdowns.count()
        logger.info(f"Selecting first valid option in {drop_count} dropdowns.")
        for i in range(drop_count):
            self.js_click(dropdowns.nth(i))
            self._select_first_dropdown_option()

    def save_inspection_report(self) -> None:
        """Clicks Save, accepts the confirmation prompt, and waits for save to complete."""
        logger.info("Saving MT-121 Inspection Report.")
        self.js_click(self.save_report_button)
        self._wait_for_loader()
        
        # Click OK on confirmation
        self.js_click(self.ok_confirm_button)
        self._wait_for_loader()
        logger.info("MT-121 Inspection Report saved successfully.")

    def generate_inspection_report_pdf(self) -> None:
        """Clicks Generate Inspection Report, clicks OK on the confirmation dialog, and verifies the popup Canvas."""
        logger.info("Clicking Generate Inspection Report.")
        self._wait_for_loader()
        self.js_click(self.gen_report_button)
        
        # Wait for dialog and click OK to trigger popup expect
        expect(self.page.get_by_text("Document generated. Please")).to_be_visible(timeout=20000)
        logger.info("Accepting generate confirmation dialog and expecting PDF report popup...")
        
        with self.page.expect_popup() as popup_info:
            self.js_click(self.ok_confirm_button)
        popup = popup_info.value
        
        # Verify the canvas on the generated report window
        expect(popup.locator("#mainCanvas")).to_be_visible(timeout=30000)
        popup.close()
        logger.info("Inspection report PDF generated and verified successfully.")
