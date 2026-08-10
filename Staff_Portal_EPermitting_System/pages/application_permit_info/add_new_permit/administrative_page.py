import logging
import re
from playwright.sync_api import Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class AdministrativePage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Administrative' application type.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.design_job_input = page.get_by_role("textbox", name=re.compile(r"Design Job", re.I)).or_(
            page.locator("#design_job, input[name*='DesignJob']")
        ).first
        self.upc_input = page.get_by_role("textbox", name=re.compile(r"UPC", re.I)).or_(
            page.locator("#upc_no, input[name*='UPC']")
        ).first

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

        self.fill_permit_dropdowns([
            "--Select District Office--",
            "--Select Department Project",
            "--Select Department Project--",
            "--Select Supervising Engineer",
            "--Select Access Case Manager--",
            "--Select Case Manager--",
            "--Select Permit Sub Type--",
        ])

    def fill_location_information(self, data: dict = None) -> None:
        """Fills Location Information section using base class and dismisses any alerts."""
        super().fill_location_information(data)
        self._dismiss_alert_if_present()

    def save_permit(self) -> None:
        """Clicks Save button and asserts no validation errors."""
        logger.info("Saving Administrative permit.")
        self._wait_for_loader()
        self._dismiss_alert_if_present()
        super().save_permit()

    def verify_administrative_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_administrative_permit(self, data: dict = None) -> None:
        """High-level workflow method to create administrative permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
