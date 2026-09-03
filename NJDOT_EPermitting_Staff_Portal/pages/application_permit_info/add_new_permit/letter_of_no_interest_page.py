import logging
from playwright.sync_api import expect, Page
from pages.application_permit_info.general_information_page import GeneralInformationPage

logger = logging.getLogger(__name__)


class LetterOfNoInterestPage(GeneralInformationPage):
    """
    Page Object Model for specialized fields and logic specifically for the 'Letter of No Interest' application type.
    """

    def fill_general_information(self, data: dict = None) -> None:
        """Fills General Information section for Letter of No Interest."""
        logger.info("Filling Letter of No Interest General Information section.")
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

    def verify_letter_of_no_interest_details(self, data: dict = None) -> None:
        """Verifies successful permit creation."""
        self.verify_permit_saved()

    def create_letter_of_no_interest_permit(self, data: dict = None) -> None:
        """Executes complete creation flow for Letter of No Interest permit."""
        self.fill_general_information(data)
        self.fill_location_information(data)
        self.save_permit()
