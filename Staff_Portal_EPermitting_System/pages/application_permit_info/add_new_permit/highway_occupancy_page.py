import logging
import re
from playwright.sync_api import expect
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class HighwayOccupancyPage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Highway Occupancy' application type.
    """

    def __init__(self, page):
        super().__init__(page)

        # General Information Locators
        self.team_leader_dropdown = page.locator("#frmPermit").get_by_text("--Select Team Leader--").first
        self.job_number_dropdown = page.locator("#frmPermit").get_by_text("--Select Job").first
        self.department_dropdown = page.locator("#frmPermit").get_by_text("--Select Department--").first
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--").first
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Case Manager--").first
        self.inspector_dropdown = page.locator("#frmPermit").get_by_text("--Select Inspector--").first

        # Permit Information Locators
        self.loc_reference_input = page.get_by_role("textbox", name="Location in Reference to")
        self.num_poles_formatted = page.get_by_role("spinbutton", name="0.00").first
        self.num_poles_input = page.get_by_role("spinbutton", name="Number of pole(s) or pole")
        self.utility_companies_input = page.get_by_role("textbox", name="Attached Utility Compan(ies) *")
        self.voltage_input = page.get_by_role("textbox", name="Voltage not to exceed *")
        self.appurtenances_input = page.get_by_role("textbox", name="Attached Appurtenance(s) to")
        self.date_picker_btn = page.get_by_role("button", name="select").first

        # Location Information Locators
        self.location_div = page.locator("#ApplicationLocationInfoDiv")
        self.route_dropdown = self.location_div.get_by_text("--Select Route--").first
        self.suffix_dropdown = self.location_div.get_by_text("--Select Suffix--").first
        self.direction_dropdown = self.location_div.get_by_text("--Select Direction--").first

        # Save button
        self.save_button = page.get_by_role("button", name=" Save")

    def fill_general_information(self, data: dict):
        """Fills the General Information section for Highway Occupancy."""
        self._wait_for_loader()

        for dropdown in [
            self.team_leader_dropdown,
            self.job_number_dropdown,
            self.department_dropdown,
            self.permit_sub_type_dropdown,
            self.case_manager_dropdown,
            self.inspector_dropdown,
        ]:
            self.select_first_dropdown_option(dropdown)

    def fill_permit_information(self, data: dict):
        """Fills the permit specific information."""
        self._wait_for_loader()

        if self.loc_reference_input.is_visible():
            self.loc_reference_input.fill(data.get("loc_ref", "Dynamic Location Reference"))

        if self.utility_companies_input.is_visible():
            self.utility_companies_input.fill(data.get("utility_co", "Faker Utility Co"))

        if self.appurtenances_input.is_visible():
            self.appurtenances_input.fill(data.get("appurtenance", "Faker Appurtenance"))

        self.set_today_date(self.date_picker_btn)

    def fill_location_information(self, data: dict):
        """Fills the Location Information section."""
        self._wait_for_loader()

        for dropdown in [self.route_dropdown, self.suffix_dropdown, self.direction_dropdown]:
            self.select_first_dropdown_option(dropdown)

        try:
            self._set_kendo_numeric_value("milepost", 0.0)
        except Exception:
            pass

    def save_permit(self):
        """Clicks the save button and completes creation."""
        self._wait_for_loader()
        self.save_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.save_button)
        self._wait_for_loader()

    def create_highway_occupancy_permit(self, data: dict):
        """Orchestrates full Highway Occupancy creation flow."""
        self.fill_general_information(data)
        self.fill_permit_information(data)
        self.fill_location_information(data)
        self.save_permit()
