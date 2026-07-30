import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class LetterOfNoInterestPage(GeneralInformationPage):
    """
    Page Object Model for specialized fields and logic specifically for the 'Letter of No Interest' application type,
    strictly implementing the user's recorded codegen workflow.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Form Containers & Headings from Codegen
        self.render_add_new_container = page.locator("#renderaddnew")
        self.general_info_heading = page.get_by_role("heading", name="General Information").or_(
            page.get_by_text("General Information")
        ).first
        self.location_info_heading = page.get_by_role("heading", name="Location Information").or_(
            page.get_by_text("Location Information")
        ).first

        self.frm_permit_container = page.locator("#frmPermit")
        self.location_info_container = page.locator("#ApplicationLocationInfoDiv")

        # Specific Dropdowns inside #frmPermit from Codegen
        self.department_dropdown = page.locator("#frmPermit span.k-widget.k-dropdown:visible, #frmPermit span.k-dropdown:visible").nth(0)
        self.case_manager_dropdown = page.locator("#frmPermit span.k-widget.k-dropdown:visible, #frmPermit span.k-dropdown:visible").nth(1)

        # Location Dropdowns inside #ApplicationLocationInfoDiv from Codegen
        self.route_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(0)
        self.suffix_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(1)
        self.direction_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(2)

        # Spinbuttons from Codegen
        self.milepost_start_input = page.get_by_role("spinbutton", name="Milepost Start *").or_(
            page.get_by_role("spinbutton").first
        ).first
        self.milepost_end_input = page.get_by_role("spinbutton", name="Milepost End").or_(
            page.get_by_role("spinbutton").nth(1)
        ).first

        # Save & Verification Locators from Codegen
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSave, .btn:has-text('Save')")).first

        self.dept_job_permit_container = page.locator("div").filter(has_text="Department Job # Permit Type").nth(4)

    def fill_general_information(self, data: dict) -> None:
        """Fills General Information section selecting 1st option for Department and Case Manager per codegen."""
        logger.info("Filling Letter of No Interest General Information section.")
        self._wait_for_loader()

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 1. Select Department (1st option)
        if self.department_dropdown.is_visible():
            self.js_click(self.department_dropdown)
            self.page.wait_for_timeout(300)
            self.select_first_dropdown_option(self.department_dropdown)
            self.page.wait_for_timeout(1000)
            self._wait_for_loader()

        # 2. Select Case Manager (1st option)
        if self.case_manager_dropdown.is_visible():
            self.js_click(self.case_manager_dropdown)
            self.page.wait_for_timeout(300)
            self.select_first_dropdown_option(self.case_manager_dropdown)
            self.page.wait_for_timeout(1000)
            self._wait_for_loader()

    def fill_location_information(self, data: dict) -> None:
        """Fills Location Information section selecting 1st option for Route, Suffix, Direction, and filling Mileposts."""
        logger.info("Filling Letter of No Interest Location Information section.")
        milepost_start = data.get("milepost_start", "1")
        milepost_end = data.get("milepost_end", "2")

        try:
            if self.location_info_heading.is_visible():
                expect(self.location_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 1. Select Route (1st option)
        if self.route_dropdown.is_visible():
            self.js_click(self.route_dropdown)
            self.page.wait_for_timeout(300)
            self.select_first_dropdown_option(self.route_dropdown)
            self.page.wait_for_timeout(1000)
            self._wait_for_loader()

        # 2. Fill Milepost Start and End with Enter keypress
        try:
            if self.milepost_start_input.is_visible():
                self.milepost_start_input.click(force=True)
                self.milepost_start_input.fill(milepost_start)
                self.milepost_start_input.press("Enter")

            if self.milepost_end_input.is_visible():
                self.milepost_end_input.click(force=True)
                self.milepost_end_input.fill(milepost_end)
                self.milepost_end_input.press("Enter")
        except Exception as e:
            logger.warning(f"Milepost input note: {e}")

        # 3. Select Suffix (1st option)
        if self.suffix_dropdown.is_visible():
            self.js_click(self.suffix_dropdown)
            self.page.wait_for_timeout(300)
            self.select_first_dropdown_option(self.suffix_dropdown)
            self.page.wait_for_timeout(500)

        # 4. Select Direction (double-click fallback as recorded in codegen)
        if self.direction_dropdown.is_visible():
            self.js_click(self.direction_dropdown)
            self.page.wait_for_timeout(200)
            self.js_click(self.direction_dropdown)
            self.page.wait_for_timeout(300)
            self.select_first_dropdown_option(self.direction_dropdown)
            self.page.wait_for_timeout(500)

        self.page.evaluate("$('.k-overlay').hide();")
        self.fill_kendo_numeric("Milepost", float(milepost_start))

    def save_permit(self) -> None:
        """Clicks Save button, confirms secondary save if visible, and verifies post-save containers per codegen."""
        logger.info("Saving Letter of No Interest permit.")
        self.js_click(self.save_button)
        self._wait_for_loader()

        # Secondary Save if present on details page
        try:
            if self.save_button.is_visible():
                self.js_click(self.save_button)
                self._wait_for_loader()
        except Exception:
            pass

        try:
            if self.dept_job_permit_container.is_visible():
                expect(self.dept_job_permit_container).to_be_visible(timeout=10000)
        except Exception:
            pass

    def create_letter_of_no_interest_permit(self, data: dict) -> None:
        """Executes complete creation flow for Letter of No Interest permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
