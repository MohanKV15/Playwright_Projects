import logging
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class SubmitApplicationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Main Submit Application button on the Home Page
        self.submit_app_button = page.locator("#btnSubmitApp")
        
        # Options displayed after clicking the submit button
        self.permit_app_text = page.get_by_text("Permit Application Submit a")
        self.license_app_text = page.get_by_text("License Application Submit a")
        self.permit_transfer_text = page.get_by_text("Permit Transfer Submit a new")
        self.name_change_text = page.get_by_text("Name Change Submit a new")

    def click_submit_application(self) -> None:
        """Clicks the 'Submit Application' button."""
        logger.info("Clicking '#btnSubmitApp' locator")
        self.submit_app_button.click()

    def verify_application_options_visible(self) -> None:
        """Verifies that all application options are visible after clicking the submit button."""
        logger.info("Asserting visibility of application submission options")
        expect(self.permit_app_text).to_be_visible()
        expect(self.license_app_text).to_be_visible()
        expect(self.permit_transfer_text).to_be_visible()
        expect(self.name_change_text).to_be_visible()
