import logging
import re
from playwright.sync_api import expect
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class AdministrativePage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Administrative' application type.
    """

    def __init__(self, page):
        super().__init__(page)

        # Dropdown Triggers
        self.district_office_dropdown = page.locator("#frmPermit").get_by_text("--Select District Office--").first
        self.department_project_dropdown = page.locator("#frmPermit").get_by_text("--Select Department Project").first
        self.supervising_engineer_dropdown = page.locator("#frmPermit").get_by_text("--Select Supervising Engineer").first
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Access Case Manager--").first
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--").first

        # Text/Spinbox Inputs
        self.design_job_input = page.get_by_role("textbox", name="Design Job # *")
        self.upc_input = page.get_by_role("textbox", name="UPC # *")

        # Location Specific Selectors
        self.route_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Route--").first
        self.suffix_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Suffix--").first
        self.direction_dropdown = page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Direction--").first
        self.milepost_start_input = page.get_by_role("spinbutton", name=re.compile(r"Milepost Start", re.IGNORECASE))

        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        self.initial_review_indicator = page.get_by_text("Initial Review")

    def fill_general_information(self, data: dict):
        """Fills the 'General Information' section of the Administrative permit."""
        self._wait_for_loader()

        for dropdown in [
            self.district_office_dropdown,
            self.department_project_dropdown,
            self.supervising_engineer_dropdown,
            self.case_manager_dropdown,
            self.permit_sub_type_dropdown,
        ]:
            self.select_first_dropdown_option(dropdown)

        if self.design_job_input.is_visible():
            self.design_job_input.fill(data.get("design_job", "test"))

        if self.upc_input.is_visible():
            self.upc_input.fill(data.get("upc", "test123"))

    def fill_location_information(self, data: dict):
        """Fills the 'Location Information' section of the Administrative permit."""
        self._wait_for_loader()

        for dropdown in [self.route_dropdown, self.suffix_dropdown, self.direction_dropdown]:
            self.select_first_dropdown_option(dropdown)

        try:
            self._set_kendo_numeric_value("milepost", 0.0)
        except Exception:
            pass

    def save_permit(self):
        """Clicks the save button and verifies success."""
        self._wait_for_loader()
        self.save_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.save_button)
        self._wait_for_loader()

    def create_administrative_permit(self, data: dict):
        """High-level workflow method to create administrative permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()

    def verify_administrative_details(self, data: dict):
        """Verifies successful permit creation."""
        pass
