import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class AdministrativePage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Administrative' application type.
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

        self.design_job_input = page.get_by_role("textbox", name=re.compile(r"Design Job", re.I)).or_(
            page.locator("#design_job, input[name*='DesignJob']")
        ).first
        self.upc_input = page.get_by_role("textbox", name=re.compile(r"UPC", re.I)).or_(
            page.locator("#upc_no, input[name*='UPC']")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSavePermit, #btnSave, .btn:has-text('Save')")).first

    def _dismiss_alert_if_present(self) -> None:
        """Dismisses any Kendo alert or warning dialogs if present."""
        try:
            self.page.wait_for_timeout(300)
            ok_btn = self.page.locator("div.k-dialog:visible button, div.k-window:visible button, .modal:visible button, #btnOk, .k-button:has-text('OK')").first
            if ok_btn.count() > 0 and ok_btn.is_visible():
                ok_btn.click()
                self.page.wait_for_timeout(300)
                self._wait_for_loader()
        except Exception:
            pass

    def fill_general_information(self, data: dict = None) -> None:
        """Fills the General Information section for Administrative permit."""
        logger.info("Filling Administrative General Information section.")
        self._wait_for_loader()
        try:
            self.frm_permit_container.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

        data = data or {}

        try:
            if self.design_job_input.count() > 0 and self.design_job_input.first.is_visible():
                self.design_job_input.fill(data.get("design_job", "TEST-JOB-123"))
        except Exception as e:
            logger.warning(f"Design job input note: {e}")

        try:
            if self.upc_input.count() > 0 and self.upc_input.first.is_visible():
                self.upc_input.fill(data.get("upc", "UPC-123456"))
        except Exception as e:
            logger.warning(f"UPC input note: {e}")

        dropdown_placeholders = [
            "--Select District Office--",
            "--Select Department Project",
            "--Select Department Project--",
            "--Select Supervising Engineer",
            "--Select Access Case Manager--",
            "--Select Case Manager--",
            "--Select Permit Sub Type--",
        ]

        for placeholder in dropdown_placeholders:
            try:
                trig = self.page.locator("#frmPermit").get_by_text(placeholder)
                if trig.count() > 0 and trig.first.is_visible():
                    trig.first.click()
                    self.page.wait_for_timeout(300)
                    self.page.get_by_role("option").first.click()
                    self.page.wait_for_timeout(300)
                    self._wait_for_loader()
            except Exception as e:
                logger.warning(f"Dropdown '{placeholder}' selection note: {e}")

    def fill_location_information(self, data: dict = None) -> None:
        """Fills Location Information using exact pre_application_meeting_page logic with alert handling."""
        logger.info("Filling Administrative Location Information section.")
        milepost_val = (data or {}).get("milepost", "0")
        self._wait_for_loader()
        try:
            self.location_info_container.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

        # 1. Select Route
        try:
            self._wait_for_loader()
            self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Route--").first.click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()
            self._dismiss_alert_if_present()
        except Exception as e:
            logger.warning(f"Route selection note: {e}")

        # 2. Fill Mileposts
        try:
            self._wait_for_loader()
            spin1 = self.page.get_by_role("spinbutton").first
            if spin1.is_visible():
                spin1.click()
                spin1.fill(str(milepost_val))
                spin1.press("Enter")
                self.page.wait_for_timeout(300)
                self._dismiss_alert_if_present()

            spin2 = self.page.get_by_role("spinbutton").nth(1)
            if spin2.is_visible():
                spin2.click()
                spin2.fill(str(milepost_val))
                spin2.press("Enter")
                self.page.wait_for_timeout(300)
                self._dismiss_alert_if_present()
        except Exception as e:
            logger.warning(f"Milepost spinbutton note: {e}")

        # 3. Select Suffix
        try:
            self._wait_for_loader()
            self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Suffix--").first.click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()
            self._dismiss_alert_if_present()
        except Exception as e:
            logger.warning(f"Suffix selection note: {e}")

        # 4. Select Direction
        try:
            self._wait_for_loader()
            dir_trig = self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Direction--").first
            dir_trig.click()
            self.page.wait_for_timeout(200)
            dir_trig.click()
            self.page.wait_for_timeout(300)
            self.page.get_by_role("option").first.click()
            self.page.wait_for_timeout(500)
            self._wait_for_loader()
            self._dismiss_alert_if_present()
        except Exception as e:
            logger.warning(f"Direction selection note: {e}")

    def save_permit(self) -> None:
        """Clicks Save button and asserts no validation errors."""
        logger.info("Saving Administrative permit.")
        self._wait_for_loader()
        self._dismiss_alert_if_present()
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

    def verify_administrative_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_administrative_permit(self, data: dict = None) -> None:
        """High-level workflow method to create administrative permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_administrative_details(data)
        self.close_permit_page()
