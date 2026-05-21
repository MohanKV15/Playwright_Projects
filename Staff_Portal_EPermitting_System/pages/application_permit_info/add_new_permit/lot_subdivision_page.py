from pages.application_permit_info.general_information_page import GeneralInformationPage
from playwright.sync_api import expect
import re

class LotSubdivisionPage(GeneralInformationPage):
    def __init__(self, page):
        super().__init__(page)
        
        # --- General Information Locators ---
        self.team_leader_dropdown = page.locator("#frmPermit").get_by_text("--Select Team Leader--")
        self.job_number_input = page.get_by_role("textbox", name=re.compile(r"Design Job|Job #", re.IGNORECASE))
        self.department_dropdown = page.locator("#frmPermit").get_by_text("--Select Department--")
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Case Manager--")
        self.inspector_dropdown = page.locator("#frmPermit").get_by_text("--Select Inspector--")
        
        # --- Location Information Locators ---
        self.location_div = page.locator("#ApplicationLocationInfoDiv")
        self.route_dropdown = self.location_div.get_by_text("--Select Route--")
        self.milepost_start_input = page.get_by_role("spinbutton", name=re.compile(r"0.00", re.IGNORECASE))
        self.suffix_dropdown = self.location_div.get_by_text("--Select Suffix--")
        self.direction_dropdown = self.location_div.locator("div:has(> label:has-text('Direction'))").get_by_text("--Select Direction--")
        
        # Save button
        self.save_button = page.get_by_role("button", name=" Save")

    def fill_general_information(self, data: dict):
        """
        Fills the General Information section for Lot Subdivision.
        """
        self._wait_for_loader()
        
        # 1. Job # / Project Name
        if self.job_number_input.is_visible(timeout=2000):
            self.job_number_input.fill(data.get("project_name", "LOT-SUB-AUTO"))

        # 2. Team Leader
        self.team_leader_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 3. Department
        self.department_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 4. Case Manager
        try:
            if self.case_manager_dropdown.is_visible(timeout=2000):
                self.case_manager_dropdown.click()
                self.js_click(self.page.get_by_role("option").first)
                self._wait_for_loader()
        except: pass

        # 5. Inspector (Optional)
        try:
            if self.inspector_dropdown.is_visible(timeout=2000):
                self.inspector_dropdown.click()
                self.js_click(self.page.get_by_role("option").first)
                self._wait_for_loader()
        except: pass

    def fill_location_information(self, data: dict):
        """
        Fills the Location Information section.
        """
        self._wait_for_loader()
        
        # 1. Route
        self.route_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 2. Milepost Start (Stable pattern from Lot Consolidation)
        try:
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
           self.page.wait_for_timeout(500)
        except Exception: 
           pass

        # 3. Suffix
        self.suffix_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 4. Direction (Standard robust selection - grabs first option)
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
        
        # Stability buffer
        self.page.wait_for_timeout(2000)
        
        # Only click again if the button is still visible (navigation hasn't started)
        try:
            if save_btn.is_visible():
                self.dispatch_bubble_click(save_btn)
        except Exception:
            pass
        # --------------------
        
        self._wait_for_loader()
        


    def verify_success(self):
        """
        Verify successful navigation to details page.
        """
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()
        # Increased timeout to 60s for staging environments
        expect(self.page).to_have_url(re.compile(r"DetailsPageFV|FullView", re.IGNORECASE), timeout=60000)

    def create_lot_subdivision_permit(self, data: dict):
        """
        Main flow orchestrator.
        """
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_success()
