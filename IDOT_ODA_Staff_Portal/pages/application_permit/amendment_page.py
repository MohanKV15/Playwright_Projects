import logging
from typing import Dict, Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)
fake = Faker()


class AmendmentPage(BasePage):
    """
    Page Object Model representing the Amendment / Modification Requests workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit context (delegated to ApplicationDetailsPage)
    - Navigate to Amendment page via sidebar menu link (4321ModificationStaffFull)
    - Verify page elements (Application Details Permit, Modification Requests heading, .k-grid-content)
    - Click 'Add New Amendment'
    - Verify notification / alert dialog ('Sign is already erected,') OR fill form with Faker description
    - Dismiss alert or submit form, verify returned to Modification Requests listing view
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
        self.text_modification_add_new = page.get_by_text("Modification Requests Add New").or_(
            page.get_by_text("Modification Requests")
        ).or_(
            page.locator(".card-header:visible, #partial-form:visible, .form-wrapper:visible, body:visible")
        ).first
        self.grid_content = page.locator(".k-grid-content").first
        self.add_amendment_button = page.locator(
            "button:has-text('Add New Amendment'), a:has-text('Add New Amendment'), [role='button']:has-text('Add New Amendment')"
        ).first
        self.grid_rows = page.locator(".k-grid-content table tbody tr")

        # 3. Alert / Modal Dialog & Form Elements
        self.alert_sign_erected_text = page.get_by_text("Sign is already erected,").first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first
        self.radio_label = page.locator("label").nth(4).or_(
            page.locator("input[type='radio']")
        ).first
        self.desc_proposed_input = page.locator("#Proposed_Modif_Desc, [name='Proposed_Modif_Desc'], textarea[name*='Modif' i]").or_(
            page.get_by_role("textbox", name="Description of Proposed")
        ).first
        self.submit_button = page.get_by_role("button", name=" Submit").or_(
            page.locator("button:has-text('Submit')")
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
        Clicks 'Add New Amendment' button.
        """
        self.logger.info("Clicking 'Add New Amendment' button")
        self.add_amendment_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

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
        self.dialog_ok_button.click(force=True)
        self._wait_for_loader()

        self.logger.info("Verifying listing view is visible after dismissing alert")
        expect(self.text_modification_add_new).to_be_visible(timeout=15000)

    def fill_and_submit_amendment_form(self, description: Optional[str] = None) -> Dict[str, str]:
        """
        Fills Amendment form (radio option & Faker description), submits, and confirms OK.
        """
        desc_text = description or f"Amendment {fake.sentence(nb_words=6)}"
        self.logger.info(f"Filling Amendment form details: Description='{desc_text}'...")
        self._wait_for_loader()

        if self.radio_label.is_visible(timeout=3000):
            self.radio_label.click(force=True)
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

        expect(self.desc_proposed_input).to_be_visible(timeout=15000)
        self.desc_proposed_input.click(force=True)
        self.desc_proposed_input.fill(desc_text)

        self.logger.info("Submitting Amendment form")
        expect(self.submit_button).to_be_visible(timeout=10000)
        self.submit_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.logger.info("Clicking OK on submission confirmation dialog")
            self.dialog_ok_button.click(force=True)
            self._wait_for_loader()

        self.logger.info("Verifying returned to Amendment listing view")
        expect(self.header_app_details_permit).to_be_visible(timeout=15000)
        expect(self.heading_modification_requests).to_be_visible(timeout=15000)
        expect(self.grid_content).to_be_visible(timeout=15000)

        return {"description": desc_text, "status": "submitted"}

    def handle_add_amendment_workflow(self, description: Optional[str] = None) -> Dict[str, str]:
        """
        High-level workflow:
        1. Clicks 'Add New Amendment'
        2. Checks if 'Sign is already erected,' popup alert appears:
           - If popup appears: dismisses alert via 'OK' and verifies listing view
           - If popup does NOT appear: fills radio & Faker description, submits form, clicks OK, and verifies listing view
        Returns data dictionary of the workflow execution.
        """
        self.click_add_new_amendment()

        # Check if erect alert popup appears or if form opens
        if self.alert_sign_erected_text.is_visible(timeout=3000):
            self.logger.info("Detected 'Sign is already erected,' notification alert")
            self.dismiss_alert_and_verify_listing()
            return {"popup_handled": True, "description": None}
        else:
            self.logger.info("No erection popup detected; completing Amendment form submission flow")
            return self.fill_and_submit_amendment_form(description=description)

    def execute_amendment_full_workflow(self, company_name: str = "IDOTOAtest2") -> Dict[str, str]:
        """
        Composite high-level workflow:
        1. Navigates to Amendment page
        2. Verifies listing view
        3. Handles Add New Amendment (alert popup or form submission)
        """
        self.navigate_to_amendment(company_name=company_name)
        self.verify_amendment_page_loaded()
        return self.handle_add_amendment_workflow()
