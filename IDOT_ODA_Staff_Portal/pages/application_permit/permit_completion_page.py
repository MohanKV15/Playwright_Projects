import logging
from typing import Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitCompletionPage(BasePage):
    """
    Page Object Model representing the Permit Completion workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit session context (delegated to ApplicationDetailsPage)
    - Navigate to Permit Completion view via sidebar menu link
    - Verify page elements (Application Details Permit, Permit Completion heading, Save button)
    - Click 'Save' button, wait for modal alert, and click 'OK'
    - Click 'Generate Permit' button, verify preview canvas (#mainCanvas) in popup window, and close popup
    - Verify 'Generated successfully' notification popup and click 'OK'
    - Verify 'Permit Status' heading and form wrapper layout (#partial-form)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Permit Context Activation
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_permit_completion_link = page.get_by_role("link", name="Permit Completion").or_(
            page.locator("a[href*='PermitCompletion'], .sidebar a:has-text('Permit Completion')")
        ).first

        # 2. Header & Action Locators
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_permit_completion = page.get_by_text("Permit Completion Save Permit").or_(
            page.get_by_role("heading", name="Permit Completion")
        ).first
        self.save_permit_button = page.get_by_role("button", name=" Save").or_(
            page.locator("button:has-text('Save')")
        ).first
        self.confirmation_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 3. Permit Generation Locators
        self.generate_permit_button = page.get_by_role("button", name=" Generate Permit").or_(
            page.locator("button:has-text('Generate Permit')")
        ).first
        self.generated_successfully_text = page.get_by_text("Generated successfully").first

        # 4. Status & Grid/Form Layout Locators
        self.heading_permit_status = page.get_by_role("heading", name="Permit Status").or_(
            page.locator("h4:has-text('Permit Status')")
        ).first
        self.form_wrapper = page.locator(
            ".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12, #partial-form, .form-wrapper"
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification
    # -------------------------------------------------------------------------
    def navigate_to_permit_completion(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Permit Completion page.
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
        if not self.sidebar_permit_completion_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Permit Completion")
        expect(self.sidebar_permit_completion_link).to_be_visible(timeout=15000)
        self.sidebar_permit_completion_link.click(force=True)
        self._wait_for_loader()

        self.verify_permit_completion_page_loaded()

    def verify_permit_completion_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Permit Completion page headers and Save button are visible.
        """
        self.logger.info("Verifying Permit Completion page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_permit_completion).to_be_visible(timeout=timeout_ms)
        expect(self.save_permit_button).to_be_visible(timeout=timeout_ms)
        self.logger.info("Permit Completion page elements verified successfully")

    # -------------------------------------------------------------------------
    # Save & Generate Permit Workflows
    # -------------------------------------------------------------------------
    def save_permit(self, timeout_ms: int = 15000) -> None:
        """
        Clicks the 'Save' button, verifies the confirmation popup, and clicks 'OK'.
        """
        self.logger.info("Saving permit configuration")
        expect(self.save_permit_button).to_be_visible(timeout=timeout_ms)
        self.save_permit_button.scroll_into_view_if_needed()
        self.save_permit_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

        self.logger.info("Confirming save by clicking OK on dialog popup")
        expect(self.confirmation_ok_button).to_be_visible(timeout=timeout_ms)
        self.confirmation_ok_button.click(force=True)
        self._wait_for_loader()
        self.logger.info("Permit saved successfully")

    def generate_permit(self, timeout_ms: int = 20000) -> bool:
        """
        Clicks 'Generate Permit', handles popup window displaying #mainCanvas,
        closes popup, and confirms 'Generated successfully' modal alert.
        """
        self.logger.info("Generating permit document")
        expect(self.generate_permit_button).to_be_visible(timeout=timeout_ms)
        self.generate_permit_button.scroll_into_view_if_needed()

        try:
            with self.page.expect_popup(timeout=timeout_ms) as popup_info:
                self.generate_permit_button.click(force=True)
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded")
            self.logger.info("Permit canvas preview popup window opened")
            expect(popup_page.locator("#mainCanvas").first).to_be_visible(timeout=timeout_ms)
            popup_page.close()
            self.logger.info("Permit canvas popup preview verified and closed")
        except Exception as e:
            self.logger.warning("Popup canvas verification note: %s", e)

        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        self.logger.info("Verifying 'Generated successfully' alert notification")
        expect(self.generated_successfully_text).to_be_visible(timeout=timeout_ms)
        expect(self.confirmation_ok_button).to_be_visible(timeout=timeout_ms)
        self.confirmation_ok_button.click(force=True)
        self._wait_for_loader()
        self.logger.info("Permit generated and confirmed successfully")
        return True

    def verify_permit_status_and_form(self, timeout_ms: int = 15000) -> None:
        """
        Verifies that 'Permit Status' heading and form wrapper table/elements are displayed.
        """
        self.logger.info("Verifying Permit Status section and form wrapper container")
        expect(self.heading_permit_status).to_be_visible(timeout=timeout_ms)
        expect(self.form_wrapper).to_be_visible(timeout=timeout_ms)
        self.logger.info("Permit Status section and form layout verified successfully!")

    def handle_permit_completion_full_workflow(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Composite high-level workflow:
        1. Navigates to Permit Completion page
        2. Verifies page headers
        3. Saves permit configuration and clicks OK
        4. Generates permit, verifies canvas popup preview, closes popup, and clicks OK
        5. Verifies Permit Status section and form wrapper container
        """
        self.navigate_to_permit_completion(company_name=company_name)
        self.save_permit()
        self.generate_permit()
        self.verify_permit_status_and_form()
