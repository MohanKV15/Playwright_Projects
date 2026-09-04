import logging
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.pages.add_paper_application.primary_highway_page import PrimaryHighwayPage

logger = logging.getLogger(__name__)


class InterstateHighwayPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Add Paper Application - Interstate Highway
    workflow in the IDOT Outdoor Advertising Staff Portal.
    Inherits all form filling, company search, file attachment, and verification
    logic from PrimaryHighwayPage.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.interstate_highway_button = page.locator("#btnInterState")

    def select_interstate_highway_type(self) -> None:
        """Clicks '#btnInterState' to launch the Interstate Highway application form."""
        self.logger.info("Selecting Interstate Highway application type (#btnInterState)")
        self._wait_for_loader()
        expect(self.interstate_highway_button).to_be_visible(timeout=20000)
        self.interstate_highway_button.click(force=True)
        self._wait_for_loader()
        expect(self.select_company_button).to_be_visible(timeout=25000)
