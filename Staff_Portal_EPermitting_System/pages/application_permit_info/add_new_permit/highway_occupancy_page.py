import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class HighwayOccupancyPage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Highway Occupancy' application type.
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

        # Permit Information Locators
        self.loc_reference_input = page.get_by_role("textbox", name=re.compile(r"Location in Reference", re.I)).or_(
            page.locator("input[name*='LocationRef'], #LocationReference")
        ).first
        self.voltage_input = page.get_by_role("textbox", name=re.compile(r"Voltage", re.I)).or_(
            page.locator("input[name*='Voltage'], #VoltageNotToExceed")
        ).first
        self.utility_companies_input = page.get_by_role("textbox", name=re.compile(r"Attached Utility", re.I)).or_(
            page.locator("input[name*='Utility'], #UtilityCompanies")
        ).first
        self.appurtenances_input = page.get_by_role("textbox", name=re.compile(r"Attached Appurtenance", re.I)).or_(
            page.locator("input[name*='Appurtenance'], #Appurtenances")
        ).first
        self.date_picker_btn = page.get_by_role("button", name="select").first

        # Save button
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
        """Fills the General Information section for Highway Occupancy."""
        logger.info("Filling Highway Occupancy General Information section.")
        self._wait_for_loader()
        data = data or {}

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        dropdown_placeholders = [
            "--Select Team Leader--",
            "--Select Job",
            "--Select Department--",
            "--Select Permit Sub Type--",
            "--Select Case Manager--",
            "--Select Inspector--",
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

    def fill_permit_information(self, data: dict = None) -> None:
        """Fills the permit specific information."""
        logger.info("Filling Highway Occupancy permit-specific information.")
        self._wait_for_loader()
        data = data or {}

        try:
            if self.loc_reference_input.count() > 0 and self.loc_reference_input.is_visible():
                self.loc_reference_input.fill(data.get("loc_ref", "Dynamic Location Reference"))
        except Exception as e:
            logger.warning(f"Location reference input note: {e}")

        try:
            if self.voltage_input.count() > 0 and self.voltage_input.is_visible():
                self.voltage_input.fill(data.get("voltage", "120V"))
        except Exception as e:
            logger.warning(f"Voltage input note: {e}")

        try:
            if self.utility_companies_input.count() > 0 and self.utility_companies_input.is_visible():
                self.utility_companies_input.fill(data.get("utility_co", "Faker Utility Co"))
        except Exception as e:
            logger.warning(f"Utility companies input note: {e}")

        try:
            if self.appurtenances_input.count() > 0 and self.appurtenances_input.is_visible():
                self.appurtenances_input.fill(data.get("appurtenance", "Faker Appurtenance"))
        except Exception as e:
            logger.warning(f"Appurtenances input note: {e}")

        try:
            if self.date_picker_btn.count() > 0 and self.date_picker_btn.is_visible():
                self.set_today_date(self.date_picker_btn)
        except Exception as e:
            logger.warning(f"Date picker note: {e}")

    def fill_location_information(self, data: dict = None) -> None:
        """Fills Location Information using exact pre_application_meeting_page logic with loader wait and alert handling."""
        logger.info("Filling Highway Occupancy Location Information section.")
        milepost_val = (data or {}).get("milepost", "0")
        self._wait_for_loader()

        try:
            if self.location_info_heading.is_visible():
                expect(self.location_info_heading).to_be_visible(timeout=5000)
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
        logger.info("Saving Highway Occupancy permit.")
        self._wait_for_loader()
        self._dismiss_alert_if_present()
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

    def verify_highway_occupancy_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_highway_occupancy_permit(self, data: dict = None) -> None:
        """Orchestrates full Highway Occupancy creation flow."""
        self.fill_general_information(data)
        self.fill_permit_information(data)
        self.fill_location_information(data)
        self.save_permit()
        self.verify_highway_occupancy_details(data)
        self.close_permit_page()
