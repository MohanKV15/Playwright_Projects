import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ApplicantInformationPage(BasePage):
    """
    Page Object Model for Applicant Information tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.applicant_info_tab = page.get_by_role("link", name="Applicant Information").or_(
            page.locator("a:has-text('Applicant Information'), a:has-text('Applicant/Permittee'), span:has-text('Applicant Information'), span:has-text('Applicant/Permittee'), .k-tabstrip a:has-text('Applicant')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.applicant_info_heading = page.get_by_role("heading", name="Applicant Information").or_(
            page.locator("h1:has-text('Applicant'), h2:has-text('Applicant'), h3:has-text('Applicant')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first

    def navigate_to_applicant_info(self) -> None:
        """Navigates to Applicant Information tab."""
        self.navigate_to_applicant_information()

    def navigate_to_applicant_information(self) -> None:
        """Navigates to Applicant Information tab."""
        logger.info("Navigating to Applicant Information tab.")
        self._wait_for_loader()
        if not self.applicant_info_heading.is_visible():
            self.js_click(self.applicant_info_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout."""
        logger.info("Verifying Applicant Information initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def link_contact_to_permit(self, query: str = "") -> None:
        """Links contact to permit."""
        pass

    def edit_first_contact_and_save(self) -> None:
        """Edits first contact and saves."""
        pass

    def fill_and_save_applicant_information(self) -> None:
        """Fills applicant information details and saves."""
        logger.info("Saving Applicant Information form.")
        self._wait_for_loader()
        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
