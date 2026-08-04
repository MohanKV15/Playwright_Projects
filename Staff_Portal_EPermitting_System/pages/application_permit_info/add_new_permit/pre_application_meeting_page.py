import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class PreApplicationMeetingPage(GeneralInformationPage):
    """
    Page Object Model for specialized fields and logic specifically for the 'Pre-Application Meeting' application type,
    handling Department, Case Manager, Route, Suffix, Direction, and Milepost Start & End fields.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.render_add_new_container = page.locator("#renderaddnew")
        self.frm_permit_container = page.locator("#frmPermit")
        self.location_info_container = page.locator("#ApplicationLocationInfoDiv")

        self.general_info_heading = page.get_by_role("heading", name="General Information").or_(
            page.get_by_text("General Information")
        ).first
        self.location_info_heading = page.get_by_role("heading", name="Location Information").or_(
            page.get_by_text("Location Information")
        ).first

        self.department_dropdown = page.locator("#frmPermit span.k-widget.k-dropdown:visible, #frmPermit span.k-dropdown:visible").nth(0)
        self.case_manager_dropdown = page.locator("#frmPermit span.k-widget.k-dropdown:visible, #frmPermit span.k-dropdown:visible").nth(1)

        self.route_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(0)
        self.suffix_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(1)
        self.direction_dropdown = page.locator("#ApplicationLocationInfoDiv span.k-widget.k-dropdown:visible, #ApplicationLocationInfoDiv span.k-dropdown:visible").nth(2)

        self.milepost_start_input = page.get_by_role("spinbutton", name=re.compile(r"Milepost Start", re.I)).or_(
            page.get_by_role("spinbutton").first
        ).first
        self.milepost_end_input = page.get_by_role("spinbutton", name=re.compile(r"Milepost End", re.I)).or_(
            page.get_by_role("spinbutton").nth(1)
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSavePermit, #btnSave, .btn:has-text('Save')")).first

    def fill_general_information(self, data: dict = None) -> None:
        """Fills mandatory General Information dropdowns for Pre-Application Meeting."""
        logger.info("Filling Pre-Application Meeting General Information section.")
        self._wait_for_loader()

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 1. Select Department
        try:
            self.page.locator("#frmPermit").get_by_text("--Select Department--").click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Department selection note: {e}")

        # 2. Select Case Manager
        try:
            self.page.locator("#frmPermit").get_by_text("--Select Case Manager--").click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Case Manager selection note: {e}")

    def fill_location_information(self, data: dict = None) -> None:
        """Fills Location Information (Route, Suffix, Direction, Mileposts)."""
        logger.info("Filling Pre-Application Meeting Location Information section.")
        milepost_val = (data or {}).get("milepost", "1")

        try:
            if self.location_info_heading.is_visible():
                expect(self.location_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 1. Select Route
        try:
            self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Route--").click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Route selection note: {e}")

        # 2. Fill Mileposts
        try:
            spin1 = self.page.get_by_role("spinbutton").first
            if spin1.is_visible():
                spin1.click()
                spin1.fill(str(milepost_val))
                spin1.press("Enter")

            spin2 = self.page.get_by_role("spinbutton").nth(1)
            if spin2.is_visible():
                spin2.click()
                spin2.fill(str(milepost_val))
                spin2.press("Enter")
        except Exception as e:
            logger.warning(f"Milepost spinbutton note: {e}")

        # 3. Select Suffix
        try:
            self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Suffix--").click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Suffix selection note: {e}")

        # 4. Select Direction
        try:
            dir_trig = self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Direction--")
            dir_trig.click()
            self.page.wait_for_timeout(200)
            dir_trig.click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Direction selection note: {e}")

    def save_permit(self) -> None:
        """Clicks Save button and asserts no mandatory validation errors."""
        logger.info("Saving Pre-Application Meeting permit.")
        self._wait_for_loader()
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

    def verify_pre_application_meeting_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_pre_application_meeting_permit(self, data: dict = None) -> None:
        """High-level workflow: fill form, save, verify, and return to listing."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_pre_application_meeting_details(data)
        self.close_permit_page()
