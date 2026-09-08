import logging
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.pages.add_paper_application.primary_highway_page import PrimaryHighwayPage

logger = logging.getLogger(__name__)


class DirectionalSignPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Add Paper Application - Directional Sign
    workflow in the IDOT Outdoor Advertising Staff Portal.
    Inherits form filling, company search, file attachment, and verification
    logic from PrimaryHighwayPage.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.directional_sign_button = page.locator("#btnDirectionalSign")
        self.applicant_app_number_label = page.get_by_text("Applicant Application Number").first

    def select_directional_sign_type(self) -> None:
        """Clicks '#btnDirectionalSign' to launch the Directional Sign application form."""
        self.logger.info("Selecting Directional Sign application type (#btnDirectionalSign)")
        self._wait_for_loader()
        expect(self.directional_sign_button).to_be_visible(timeout=20000)
        self.directional_sign_button.click(force=True)
        self._wait_for_loader()
        expect(self.applicant_app_number_label).to_be_visible(timeout=25000)

    def verify_directional_sign_form_visible(self) -> None:
        """Verifies that the Directional Sign form and Applicant Application Number label are visible."""
        self.logger.info("Verifying Directional Sign form is visible")
        self._wait_for_loader()
        expect(self.applicant_app_number_label).to_be_visible(timeout=20000)
