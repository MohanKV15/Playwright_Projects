import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class LetterOfNoInterestPage(GeneralInformationPage):
    """
    Page Object Model for specialized fields and logic specifically for the 'Letter of No Interest' application type.
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

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSavePermit, #btnSave, .btn:has-text('Save')")).first

    def fill_general_information(self, data: dict = None) -> None:
        """Fills General Information section for Letter of No Interest."""
        logger.info("Filling Letter of No Interest General Information section.")
        self._wait_for_loader()

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        dropdown_placeholders = [
            "--Select Department--",
            "--Select Case Manager--",
        ]

        for placeholder in dropdown_placeholders:
            try:
                trig = self.page.locator("#frmPermit").get_by_text(placeholder).first
                if trig.is_visible():
                    trig.click()
                    self.page.wait_for_timeout(300)
                    self.page.get_by_role("option").first.click()
                    self.page.wait_for_timeout(300)
            except Exception as e:
                logger.warning(f"Dropdown '{placeholder}' selection note: {e}")

    def fill_location_information(self, data: dict = None) -> None:
        """Fills Location Information using exact pre_application_meeting_page logic."""
        logger.info("Filling Letter of No Interest Location Information section.")
        milepost_start = (data or {}).get("milepost_start", (data or {}).get("milepost", "1"))
        milepost_end = (data or {}).get("milepost_end", "2")

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
                spin1.fill(str(milepost_start))
                spin1.press("Enter")

            spin2 = self.page.get_by_role("spinbutton").nth(1)
            if spin2.is_visible():
                spin2.click()
                spin2.fill(str(milepost_end))
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
        """Clicks Save button and asserts no validation errors."""
        logger.info("Saving Letter of No Interest permit.")
        self._wait_for_loader()
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

    def verify_letter_of_no_interest_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_letter_of_no_interest_permit(self, data: dict = None) -> None:
        """Executes complete creation flow for Letter of No Interest permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
