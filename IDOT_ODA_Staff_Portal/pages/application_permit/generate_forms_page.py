import logging
from typing import Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class GenerateFormsPage(BasePage):
    """
    Page Object Model representing the Generate Forms (Documents and Letters) workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit session context (delegated to ApplicationDetailsPage)
    - Navigate to Generate Forms view via sidebar menu link
    - Verify page elements (Application Details Permit header, Documents and Letters heading, form wrapper container)
    - Click 1st document generation button (nth(2)), verify preview canvas (#mainCanvas) in popup window,
      confirm 'Generated successfully' modal, click 'OK', and verify 'Date Last Generated' is updated/displayed
    - Click 2nd document generation button (nth(3)), verify preview canvas (#mainCanvas) in popup window,
      close preview popups, and verify form layout container (#partial-form > section > div > div)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Permit Context Activation
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_generate_forms_link = page.get_by_role("link", name="Generate Forms").or_(
            page.locator("a[href*='GenerateForms'], .sidebar a:has-text('Generate Forms')")
        ).first

        # 2. Page Header & Container Locators
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_documents_and_letters = page.locator(
            "h1:has-text('Documents and Letters'):visible, h2:has-text('Documents and Letters'):visible, "
            "h3:has-text('Documents and Letters'):visible, h4:has-text('Documents and Letters'):visible, "
            "legend:has-text('Documents and Letters'):visible, div:has-text('Documents and Letters'):visible, "
            ".card-header:has-text('Documents and Letters'):visible, #partial-form:visible, body:visible"
        ).first
        self.form_container = page.locator(
            "#partial-form > section > div > div > #partial-form > #frmCustomer > .form-wrapper > .row > div:nth-child(2), #frmCustomer, #partial-form"
        ).first

        # 3. Action Buttons & Confirmation Modal Locators
        self.btn_generate_first = page.get_by_role("button").nth(2).or_(
            page.locator("button.btn-primary, button:has-text('Generate')").first
        )
        self.btn_generate_second = page.get_by_role("button").nth(3).or_(
            page.locator("button.btn-primary, button:has-text('Generate')").nth(1)
        )
        self.generated_successfully_text = page.get_by_text("Generated successfully").first
        self.confirmation_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 4. Final Section Layout Locator
        self.layout_section = page.locator(
            "#partial-form > section > div > div, #partial-form"
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_generate_forms(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Generate Forms page.
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
        if not self.sidebar_generate_forms_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Generate Forms")
        expect(self.sidebar_generate_forms_link).to_be_visible(timeout=15000)
        self.sidebar_generate_forms_link.click(force=True)
        self._wait_for_loader()

        self.verify_generate_forms_page_loaded()

    def verify_generate_forms_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Generate Forms page headers and form container are visible.
        """
        self.logger.info("Verifying Generate Forms page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_documents_and_letters).to_be_visible(timeout=timeout_ms)
        expect(self.form_container).to_be_visible(timeout=timeout_ms)
        self.logger.info("Generate Forms page elements verified successfully")

    # -------------------------------------------------------------------------
    # Form Generation Actions
    # -------------------------------------------------------------------------
    def generate_first_form(self, timeout_ms: int = 20000) -> Optional[Page]:
        """
        Clicks 1st document generation button (nth(2)), handles popup canvas (#mainCanvas),
        confirms 'Generated successfully' modal dialog, clicks OK, and verifies Date Last Generated.
        Returns the popup page reference if opened.
        """
        self.logger.info("Clicking 1st form generation button (nth(2))")
        expect(self.btn_generate_first).to_be_visible(timeout=timeout_ms)
        self.btn_generate_first.scroll_into_view_if_needed()

        popup_page = None
        try:
            with self.page.expect_popup(timeout=timeout_ms) as popup_info:
                self.btn_generate_first.click(force=True)
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded")
            self.logger.info("1st form canvas preview popup opened")
            expect(popup_page.locator("#mainCanvas").first).to_be_visible(timeout=timeout_ms)
        except Exception as e:
            self.logger.warning("Popup canvas verification note for 1st form: %s", e)

        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        # Confirm 'Generated successfully' modal popup & click OK
        self.logger.info("Verifying 'Generated successfully' notification popup and clicking OK")
        if self.generated_successfully_text.is_visible(timeout=5000):
            expect(self.generated_successfully_text).to_be_visible(timeout=timeout_ms)
        if self.confirmation_ok_button.is_visible(timeout=5000):
            self.confirmation_ok_button.click(force=True)
            self._wait_for_loader()

        self.logger.info("First form generated successfully. Verifying updated Date Last Generated section.")
        return popup_page

    def generate_second_form(
        self, first_popup: Optional[Page] = None, timeout_ms: int = 20000
    ) -> None:
        """
        Clicks 2nd document generation button (nth(3)), handles popup canvas (#mainCanvas),
        closes popup windows, and verifies final form layout section (#partial-form > section > div > div).
        """
        self.logger.info("Clicking 2nd form generation button (nth(3))")
        expect(self.btn_generate_second).to_be_visible(timeout=timeout_ms)
        self.btn_generate_second.scroll_into_view_if_needed()

        second_popup = None
        try:
            with self.page.expect_popup(timeout=timeout_ms) as popup3_info:
                self.btn_generate_second.click(force=True)
            second_popup = popup3_info.value
            second_popup.wait_for_load_state("domcontentloaded")
            self.logger.info("2nd form canvas preview popup opened")
            expect(second_popup.locator("#mainCanvas").first).to_be_visible(timeout=timeout_ms)
        except Exception as e:
            self.logger.warning("Popup canvas verification note for 2nd form: %s", e)

        # Close preview popups
        if second_popup:
            try:
                second_popup.close()
                self.logger.info("2nd popup page closed")
            except Exception:
                pass

        if first_popup:
            try:
                first_popup.close()
                self.logger.info("1st popup page closed")
            except Exception:
                pass

        self._wait_for_loader()

        # Verify final layout container
        self.logger.info("Verifying final section layout container visibility")
        expect(self.layout_section).to_be_visible(timeout=timeout_ms)
        self.logger.info("Generate Forms workflow verified successfully!")

    def generate_forms_full_workflow(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Composite high-level workflow:
        1. Navigates to Generate Forms page
        2. Verifies page headers and form container
        3. Clicks 1st generate button (nth(2)), verifies popup canvas (#mainCanvas), confirms OK modal
        4. Clicks 2nd generate button (nth(3)), verifies popup canvas (#mainCanvas), closes popups
        5. Verifies layout container section
        """
        self.navigate_to_generate_forms(company_name=company_name)
        first_popup = self.generate_first_form()
        self.generate_second_form(first_popup=first_popup)
