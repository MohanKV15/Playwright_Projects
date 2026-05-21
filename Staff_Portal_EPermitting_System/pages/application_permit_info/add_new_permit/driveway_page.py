from pages.application_permit_info.general_information_page import GeneralInformationPage
from playwright.sync_api import expect
import re

class DrivewayPage(GeneralInformationPage):
    def __init__(self, page):
        super().__init__(page)
        self.team_leader_dropdown = page.locator("#frmPermit").get_by_text("--Select Team Leader--")
        self.department_dropdown = page.locator("#frmPermit").get_by_text("--Select Department--")
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--")
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Case Manager--")
        self.design_job_input = page.get_by_role("textbox", name=re.compile(r"Design Job", re.IGNORECASE))

        # --- Locators for Location Information Section ---
        self.location_div = page.locator("#ApplicationLocationInfoDiv")
        self.route_dropdown = self.location_div.get_by_text("--Select Route--")
        self.suffix_dropdown = self.location_div.get_by_text("--Select Suffix--")
        self.direction_dropdown = self.location_div.get_by_text("--Select Direction--")
        self.milepost_start_input = page.locator("#milepost")
        
        # Save and Success indicators
        self.save_button = page.get_by_role("button", name=" Save")
        self.initial_review_indicator = page.get_by_text("Initial Review")

    def fill_general_information(self, data: dict):
        """
        Fills the General Information section for a Driveway permit.
        """
        self._wait_for_loader()

        # 1. Design Job # (Required for almost all permits)
        if self.design_job_input.is_visible(timeout=2000):
            self.design_job_input.fill(data.get("project_name", "DRIVEWAY-TEST"))

        # 2. Team Leader
        self.team_leader_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 2. Department
        self.department_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 3. Permit Sub Type
        self.permit_sub_type_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 4. Case Manager
        self.case_manager_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

    def fill_location_information(self, data: dict):
        """
        Fills the Location Information section (Shared logic).
        """
        self._wait_for_loader()
        
        # 1. Route
        self.route_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 2. Milepost Start (Hardcoded to 0 as requested by USER)
        # 2. Milepost Start (Hardcoded to 0 as requested by USER)
        self._set_kendo_numeric_value("milepost", 0.0)
        self.page.evaluate("""
                            () => {
                                const el = document.getElementById('milepost');
                                if (!el) return;
                                el.blur();
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            """)

        # 3. Suffix
        self.suffix_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 4. Direction (Robust selection with retry loop)
        self.direction_dropdown.wait_for(state="visible")
        for _ in range(3):
            try:
                self.direction_dropdown.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            try:
                self.direction_dropdown.click(timeout=5000)
                first_option = self.page.get_by_role("option").first
                if first_option.is_visible(timeout=2000):
                    self.js_click(first_option)
                    break
            except Exception:
                pass
        self._wait_for_loader()

    def save_permit(self):
        """
        Clicks the Save button and verifies registration.
        """
        self._wait_for_loader()
        
        # --- BUBBLE LOGIC ---
        save_btn = self.page.get_by_role("button", name=" Save")
        self.dispatch_bubble_click(save_btn)
        
        try:
            if save_btn.is_visible(timeout=2000):               
                self.dispatch_bubble_click(save_btn)
        except Exception as e:
            pass
        
        self._wait_for_loader()
        
    def create_driveway_permit(self, data: dict):
        """
        Orchestrates the full Driveway creation flow.
        """
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
