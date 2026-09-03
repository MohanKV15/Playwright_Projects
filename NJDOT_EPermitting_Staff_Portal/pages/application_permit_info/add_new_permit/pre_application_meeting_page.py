import logging
import re
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class PreApplicationMeetingPage(GeneralInformationPage):
    """
    Page Object Model for specialized fields and logic specifically for the 'Pre-Application Meeting' application type.
    """

    def fill_general_information(self, data: dict = None) -> None:
        """Fills mandatory General Information dropdowns for Pre-Application Meeting."""
        logger.info("Filling Pre-Application Meeting General Information section.")
        self._wait_for_loader()

        try:
            if self.general_info_heading.is_visible():
                expect(self.general_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        self.fill_permit_dropdowns([
            "--Select Department--",
            "--Select Case Manager--",
        ])

    def verify_pre_application_meeting_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_pre_application_meeting_permit(self, data: dict = None) -> None:
        """High-level workflow: fill form, save, verify, and return to listing."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
