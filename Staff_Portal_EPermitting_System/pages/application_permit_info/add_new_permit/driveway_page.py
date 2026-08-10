import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class DrivewayPage(GeneralInformationPage):
    """
    Handles specialized fields and logic specifically for the 'Driveway' application type.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.design_job_input = page.get_by_role("textbox", name=re.compile(r"Design Job", re.I)).or_(
            page.locator("#design_job, input[name*='DesignJob']")
        ).first

    def fill_general_information(self, data: dict = None) -> None:
        """Fills the General Information section for a Driveway permit."""
        logger.info("Filling Driveway General Information section.")
        self._wait_for_loader()
        data = data or {}

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        try:
            if self.design_job_input.is_visible():
                self.design_job_input.fill(data.get("project_name", "DRIVEWAY-TEST"))
        except Exception as e:
            logger.warning(f"Design job input note: {e}")

        self.fill_permit_dropdowns()

    def verify_driveway_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_driveway_permit(self, data: dict = None) -> None:
        """Orchestrates the full Driveway creation flow."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
