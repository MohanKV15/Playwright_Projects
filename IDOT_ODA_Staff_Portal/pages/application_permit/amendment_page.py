import logging
from typing import Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class AmendmentPage(BasePage):
    """
    Page Object Model representing the Amendment / Modification Requests workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit context (delegated to ApplicationDetailsPage)
    - Navigate to Amendment page via sidebar menu link (4321ModificationStaffFull)
    - Verify page elements (Application Details Permit, Modification Requests heading, .k-grid-content)
    - Click 'Add New Amendment'
    - Verify notification / alert dialog ('Sign is already erected,')
    - Dismiss alert by clicking 'OK'
    - Verify returned to Modification Requests listing view
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Permit Context
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_amendment_link = page.locator(
            "a[href*='ModificationStaffFull'], .sidebar a:has-text('Amendment'), nav a:has-text('Amendment')"
        ).filter(visible=True).first

        # 2. Listing View Elements (4321ModificationStaffFull)
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_modification_requests = page.get_by_role("heading", name="Modification Requests").first
        self.text_modification_add_new = page.get_by_text("Modification Requests Add New").first
        self.grid_content = page.locator(".k-grid-content").first
        self.add_amendment_button = page.locator(
            "button:has-text('Add New Amendment'), a:has-text('Add New Amendment'), [role='button']:has-text('Add New Amendment')"
        ).first
        self.grid_rows = page.locator(".k-grid-content table tbody tr")

        # 3. Alert / Modal Dialog Elements
        self.alert_sign_erected_text = page.get_by_text("Sign is already erected,").first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), button:has-text('OK')")
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification
    # -------------------------------------------------------------------------
    def navigate_to_amendment(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application session via company search and navigates to Amendment page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        first_row = self.app_details.permit_grid_rows.first

        # Activate permit session by clicking action button on 1st record row
        action_btn = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_amendment_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Amendment")
        expect(self.sidebar_amendment_link).to_be_visible(timeout=15000)
        self.sidebar_amendment_link.click(force=True)
        self._wait_for_loader()

        self.page.wait_for_url("**/4321ModificationStaffFull**", timeout=20000)
        self.verify_amendment_page_loaded()

    def verify_amendment_page_loaded(self) -> None:
        """
        Verifies that Amendment page headers, grid content, and Add New Amendment button are visible.
        """
        self.logger.info("Verifying Amendment page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=15000)
        expect(self.heading_modification_requests).to_be_visible(timeout=15000)
        expect(self.text_modification_add_new).to_be_visible(timeout=15000)
        expect(self.grid_content).to_be_visible(timeout=15000)
        expect(self.add_amendment_button).to_be_visible(timeout=15000)

    # -------------------------------------------------------------------------
    # Amendment Actions & Dialog Handling
    # -------------------------------------------------------------------------
    def click_add_new_amendment(self) -> None:
        """
        Clicks 'Add New Amendment' button and asserts the sign erected notification appears.
        """
        self.logger.info("Clicking 'Add New Amendment' button")
        self.add_amendment_button.click(force=True)
        self._wait_for_loader()

    def verify_sign_erected_alert(self) -> None:
        """
        Asserts that the 'Sign is already erected,' alert dialog is displayed.
        """
        self.logger.info("Verifying 'Sign is already erected,' dialog is visible")
        expect(self.alert_sign_erected_text).to_be_visible(timeout=15000)

    def dismiss_alert_and_verify_listing(self) -> None:
        """
        Clicks 'OK' on the notification dialog and confirms return to the listing view.
        """
        self.logger.info("Dismissing alert dialog by clicking OK")
        self.dialog_ok_button.click()
        self._wait_for_loader()

        self.logger.info("Verifying listing view is visible after dismissing alert")
        expect(self.text_modification_add_new).to_be_visible(timeout=15000)

    def handle_add_amendment_workflow(self) -> None:
        """
        High-level workflow:
        1. Clicks 'Add New Amendment'
        2. Validates 'Sign is already erected,' dialog
        3. Dismisses alert via 'OK'
        4. Validates listing page view
        """
        self.click_add_new_amendment()
        self.verify_sign_erected_alert()
        self.dismiss_alert_and_verify_listing()
