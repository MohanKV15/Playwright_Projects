import logging
import re
from playwright.sync_api import expect
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class LotSubdivisionPage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Lot Subdivision' application type.
    """

    def __init__(self, page):
        super().__init__(page)

        self.team_leader_dropdown = page.locator("#frmPermit").get_by_text("--Select Team Leader--").first
        self.department_dropdown = page.locator("#frmPermit").get_by_text("--Select Department--").first
        self.permit_sub_type_dropdown = page.locator("#frmPermit").get_by_text("--Select Permit Sub Type--").first
        self.case_manager_dropdown = page.locator("#frmPermit").get_by_text("--Select Case Manager--").first
        self.design_job_input = page.get_by_role("textbox", name=re.compile(r"Design Job", re.IGNORECASE))

        self.location_div = page.locator("#ApplicationLocationInfoDiv")
        self.route_dropdown = self.location_div.get_by_text("--Select Route--").first
        self.suffix_dropdown = self.location_div.get_by_text("--Select Suffix--").first
        self.direction_dropdown = self.location_div.get_by_text("--Select Direction--").first
        self.milepost_start_input = page.locator("#milepost")

        self.save_button = page.get_by_role("button", name=" Save")
        self.initial_review_indicator = page.get_by_text("Initial Review")

    def fill_general_information(self, data: dict):
        """Fills the General Information section for a Lot Subdivision permit."""
        self._wait_for_loader()

        if self.design_job_input.is_visible():
            self.design_job_input.fill(data.get("project_name", "LOTSUB-TEST"))

        for dropdown in [
            self.team_leader_dropdown,
            self.department_dropdown,
            self.permit_sub_type_dropdown,
            self.case_manager_dropdown,
        ]:
            self.select_first_dropdown_option(dropdown)

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
        """Clicks the Save button and verifies registration."""
        self._wait_for_loader()
        self.save_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.save_button)
        self._wait_for_loader()

    def create_lot_subdivision_permit(self, data: dict):
        """Orchestrates full Lot Subdivision creation flow."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
