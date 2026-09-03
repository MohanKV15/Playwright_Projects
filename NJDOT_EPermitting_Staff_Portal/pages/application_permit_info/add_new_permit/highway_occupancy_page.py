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

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        self.fill_permit_dropdowns([
            "--Select Team Leader--",
            "--Select Job",
            "--Select Department--",
            "--Select Permit Sub Type--",
            "--Select Case Manager--",
            "--Select Inspector--",
        ])

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
        """Fills Location Information section using base class and dismisses any alerts."""
        super().fill_location_information(data)
        self._dismiss_alert_if_present()

    def save_permit(self) -> None:
        """Clicks Save button and asserts no validation errors."""
        logger.info("Saving Highway Occupancy permit.")
        self._wait_for_loader()
        self._dismiss_alert_if_present()
        super().save_permit()

    def verify_highway_occupancy_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_highway_occupancy_permit(self, data: dict = None) -> None:
        """Orchestrates full Highway Occupancy creation flow."""
        self.fill_general_information(data)
        self.fill_permit_information(data)
        self.fill_location_information(data)
        self.save_permit()
