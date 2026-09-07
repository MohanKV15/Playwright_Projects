import logging
import re
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.pages.add_paper_application.primary_highway_page import PrimaryHighwayPage

logger = logging.getLogger(__name__)


class AdvertisingRegistrationPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Add Paper Application - Advertising Registration
    workflow in the IDOT Outdoor Advertising Staff Portal.
    Inherits form filling, company search, file attachment, and verification
    logic from PrimaryHighwayPage.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.adv_registration_button = page.locator("#btnAdvRegistration")
        self.applicant_app_number_label = page.get_by_text("Applicant Application Number").first

    def select_advertising_registration_type(self) -> None:
        """Clicks '#btnAdvRegistration' to launch the Advertising Registration application form."""
        self.logger.info("Selecting Advertising Registration application type (#btnAdvRegistration)")
        self._wait_for_loader()
        expect(self.adv_registration_button).to_be_visible(timeout=20000)
        self.adv_registration_button.click(force=True)
        self._wait_for_loader()
        expect(self.applicant_app_number_label).to_be_visible(timeout=25000)

    def verify_advertising_registration_form_visible(self) -> None:
        """Verifies that the Advertising Registration form and Applicant Application Number label are visible."""
        self.logger.info("Verifying Advertising Registration form is visible")
        self._wait_for_loader()
        expect(self.applicant_app_number_label).to_be_visible(timeout=20000)
