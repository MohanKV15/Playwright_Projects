from pages.application_permit_info.general_information_page import GeneralInformationPage
from playwright.sync_api import expect
import re

class HighwayOccupancyPage(GeneralInformationPage):
    def __init__(self, page):
        super().__init__(page)
        
        # --- General Information Locators ---
        self.team_leader_dropdown = page.locator("#frmPermit").get_by_text("--Select Team Leader--")
        self.job_number_dropdown = page.locator("#frmPermit").get_by_text("--Select Job")
        self.department_dropdown = page.locator("#frmPermit").get_by_text("--Select Department--")
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--")
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Case Manager--")
        self.inspector_dropdown = page.locator("#frmPermit").get_by_text("--Select Inspector--")
        
        # --- Permit Information (Erection of Pole) Locators ---
        self.loc_reference_input = page.get_by_role("textbox", name="Location in Reference to")
        self.num_poles_formatted = page.get_by_role("spinbutton", name="0.00")
        self.num_poles_input = page.get_by_role("spinbutton", name="Number of pole(s) or pole")
        self.utility_companies_input = page.get_by_role("textbox", name="Attached Utility Compan(ies) *")
        self.voltage_input = page.get_by_role("textbox", name="Voltage not to exceed *")
        self.appurtenances_input = page.get_by_role("textbox", name="Attached Appurtenance(s) to")
        self.date_picker_btn = page.get_by_role("button", name="select")
        
        # --- Location Information Locators ---
        self.location_div = page.locator("#ApplicationLocationInfoDiv")
        self.route_dropdown = self.location_div.get_by_text("--Select Route--")
        self.milepost_start_input = page.get_by_role("spinbutton", name="0.00").nth(1) # Usually the 2nd 0.00 is milepost
        self.suffix_dropdown = self.location_div.get_by_text("--Select Suffix--")
        self.direction_dropdown = self.location_div.get_by_text("--Select Direction--")
        
        # Save button
        self.save_button = page.get_by_role("button", name=" Save")

    def fill_general_information(self, data: dict):
        """
        Fills the General Information section for Highway Occupancy.
        """
        self._wait_for_loader()
        
        # Team Leader
        self.team_leader_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Job # (If exists/visible)
        try:
            if self.job_number_dropdown.is_visible(timeout=2000):
                self.job_number_dropdown.click()
                self.js_click(self.page.get_by_role("option").first)
                self._wait_for_loader()
        except: pass

        # Department
        self.department_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Permit Sub Type (Erection of Pole)
        self.permit_sub_type_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Case Manager
        self.case_manager_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Inspector
        self.inspector_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

    def fill_permit_information(self, data: dict):
        """
        Fills the 'Erection of Pole' specific information using dynamic test data.
        """
        self._wait_for_loader()
        
        # 1. Location Reference
        self.loc_reference_input.click()
        self.loc_reference_input.fill(data.get("loc_ref", "Dynamic Location Reference"))
        
        # 2. Number of Poles (Kendo toggle sequence)
        self._wait_for_loader()
        self.num_poles_formatted.first.click()
        self.num_poles_input.fill("0")
        
        # 3. Voltage
        self.voltage_input.click()
        self.voltage_input.fill("0")
        
        # 4. Date Selection
        self.date_picker_btn.click()
        self.page.locator(".k-calendar td:not(.k-other-month)") \
            .get_by_role("link", name="10", exact=True).click(force=True)
        
        # 5. Utility Companies
        self.utility_companies_input.click()
        self.utility_companies_input.fill(data.get("utility_co", "Faker Utility Co"))
        
        # 6. Attached Appurtenance
        self.appurtenances_input.click()
        self.appurtenances_input.fill(data.get("appurtenance", "Faker Appurtenance"))
        
        self._wait_for_loader()

    def fill_location_information(self, data: dict):
        """
        Fills the Location Information section.
        """
        self._wait_for_loader()
        
        # Route
        self.route_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Milepost Start (Hardcoded to 0)
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
        except: pass

        # Suffix
        self.suffix_dropdown.click()
        self.js_click(self.page.get_by_role("option").first)
        self._wait_for_loader()

        # Direction (Retry loop for stability)
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
        self._wait_for_loader()

    def verify_success(self):
        """
        Verify successful navigation to details page.
        """
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()
        # Increased timeout to 60s for staging latency
        expect(self.page).to_have_url(re.compile(r"DetailsPageFV|FullView", re.IGNORECASE), timeout=60000)

    def create_highway_occupancy_permit(self, data: dict):
        """
        Main flow orchestrator.
        """
        self.fill_general_information(data)
        self.fill_permit_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_success()
