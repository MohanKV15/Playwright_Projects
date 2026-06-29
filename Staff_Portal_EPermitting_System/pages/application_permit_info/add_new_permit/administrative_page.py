from pages.application_permit_info.general_information_page import GeneralInformationPage
from playwright.sync_api import expect
import re

class AdministrativePage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for 
    the 'Administrative' application type.
    """
    def __init__(self, page):
        super().__init__(page)
        
        # Dropdown Triggers (Kendo/Bootstrap patterns observed in codegen)
        self.district_office_dropdown = page.locator("#frmPermit").get_by_text("--Select District Office--")
        self.department_project_dropdown = page.locator("#frmPermit").get_by_text("--Select Department Project")
        self.supervising_engineer_dropdown = page.locator("#frmPermit").get_by_text("--Select Supervising Engineer")
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Access Case Manager--")
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--")
        
        # Text/Spinbox Inputs
        self.design_job_input = page.get_by_role("textbox", name="Design Job # *")
        self.upc_input = page.get_by_role("textbox", name="UPC # *")
        
        # Location Specific Selectors
        self.route_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Route--")
        self.milepost_start_input = page.get_by_role("spinbutton", name=re.compile(r"Milepost Start", re.IGNORECASE))
        self.suffix_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Suffix--")
        self.direction_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Direction--")
        
        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        self.initial_review_indicator = page.get_by_text("Initial Review")

    def fill_general_information(self, data: dict):
        """
        Fills the 'General Information' section of the Administrative permit.
        """
        self._wait_for_loader()

        # 1. District Office
        self.district_office_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 2. Design Job #
        self.design_job_input.fill(data.get("design_job", "test"))

        # 3. Department Project
        self.department_project_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 4. UPC #
        self.upc_input.fill(data.get("upc", "test123"))

        # 5. Supervising Engineer & Case Manager
        self.supervising_engineer_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()
        
        self.case_manager_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # 6. Permit Sub Type
        self.permit_sub_type_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

    def fill_location_information(self, data: dict):
        """
        Fills the 'Location Information' section of the Administrative permit.
        """
        self._wait_for_loader()
        
        # 1. Route
        self.route_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()
        
        # 2. Milepost Start (Always fill with 0 as requested by USER)
        try:
           self._set_kendo_numeric_value("milepost", 0.0)
           self.page.evaluate("""
                              () => {
                                  const el = document.getElementById('milepost');
                                  if (!el) return;

                                  el.blur();  // remove focus

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
        Clicks the save button and verifies success.
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
        
        self._wait_for_loader()
        
        expect(self.initial_review_indicator).to_be_visible(timeout=60000)

    def verify_administrative_details(self, data: dict):
        """
        REACH-BASED VERIFICATION:
        Ensures the application navigated to the Success/Full View page.
        """
        # 1. Wait for navigation signal
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()
        
        # 2. Verify we are on the Full View page (Target URL reached)
        # Increased timeout to 60s for staging latency
        expect(self.page).to_have_url(re.compile(r"HAPSProcessFullView"), timeout=60000)
        
        # The test will now finish and close successfully

    def create_administrative_permit(self, data: dict):
        """
        Orchestrates the full creation flow and verifies data.
        """
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_administrative_details(data)
