import logging
from typing import Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class OriginalPermitPage(BasePage):
    """
    Page Object Model representing the Original Permit view
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit session context (delegated to ApplicationDetailsPage)
    - Navigate to Original Permit view via sidebar menu link
    - Verify page elements (Application Details Permit header, Sign Information heading,
      Location Information heading, and #partial-form container layout)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Permit Context Activation
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_original_permit_link = page.get_by_role("link", name="Original Permit").or_(
            page.locator("a[href*='OriginalPermit'], .sidebar a:has-text('Original Permit')")
        ).first

        # 2. Page Verification Locators
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_sign_information = page.get_by_role("heading", name="Sign Information").or_(
            page.locator("h4:has-text('Sign Information')")
        ).first
        self.heading_location_information = page.get_by_role("heading", name="Location Information").or_(
            page.locator("h4:has-text('Location Information')")
        ).first
        self.partial_form_container = page.locator(
            "#partial-form > section > div > div, #partial-form, .form-wrapper"
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_original_permit(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Original Permit page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        action_btn = self.app_details.permit_grid_rows.first.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_original_permit_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Original Permit")
        expect(self.sidebar_original_permit_link).to_be_visible(timeout=15000)
        self.sidebar_original_permit_link.click(force=True)
        self._wait_for_loader()

        self.verify_original_permit_page_loaded()

    def verify_original_permit_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Original Permit headers, section headings, and form layout container are visible.
        """
        self.logger.info("Verifying Original Permit page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_sign_information).to_be_visible(timeout=timeout_ms)
        expect(self.heading_location_information).to_be_visible(timeout=timeout_ms)
        expect(self.partial_form_container).to_be_visible(timeout=timeout_ms)
        self.logger.info("Original Permit page verified successfully!")

    def original_permit_full_workflow(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Composite high-level workflow:
        1. Navigates to Original Permit page
        2. Verifies page headers, Sign Information, Location Information, and layout container
        """
        self.navigate_to_original_permit(company_name=company_name)
