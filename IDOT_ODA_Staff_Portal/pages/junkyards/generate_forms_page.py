import logging
from typing import Optional
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.generate_forms_page import GenerateFormsPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage

logger = logging.getLogger(__name__)


class JunkyardGenerateFormsPage(GenerateFormsPage):
    """
    Optimized Page Object Model representing the Junkyards Generate Forms (Documents and Letters) module
    in the IDOT Outdoor Advertising Staff Portal.

    Subclasses GenerateFormsPage to directly inherit shared form-generation workflows:
    - Search company on Junkyard/Permit Search ('IDOTOAtest2')
    - Select 1st record row to activate permit session context
    - Navigate via Junkyards sidebar to 'Generate Forms'
    - Assert headers ('Junkyard Details Permit', 'Documents and Letters')
    - Directly invoke parent class form generation logic (1st & 2nd document preview canvases, popups, OK modals)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Junkyards Specific Sidebar & Header Locators
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_generate_forms_link = page.get_by_role("link", name="Generate Forms").filter(visible=True).or_(
            page.locator("a[href*='DocsandLetters'], a[href*='GenerateForms']").filter(visible=True)
        ).first
        self.header_junkyard_details_permit = page.get_by_text("Junkyard Details Permit").or_(
            page.get_by_text("Application Details Permit")
        ).first
        self.heading_documents_and_letters = page.get_by_role("heading", name="Documents and Letters").or_(
            page.locator(
                "h1:has-text('Documents and Letters'):visible, h2:has-text('Documents and Letters'):visible, "
                "legend:has-text('Documents and Letters'):visible, #partial-form:visible"
            )
        ).first

    def dismiss_ok_popups(self, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """Safely dismisses visible OK modal popups."""
        dismissed = 0
        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:visible:has-text('OK')"
        ).first
        for _ in range(max_clicks):
            try:
                if ok_btn.is_visible(timeout=timeout_ms):
                    ok_btn.click(force=True)
                    self.page.wait_for_timeout(400)
                    dismissed += 1
                else:
                    break
            except Exception:
                break
        return dismissed

    def navigate_to_junkyard_generate_forms(self, company_name: str = "IDOTOAtest2") -> str:
        """
        Navigates to Junkyard Generate Forms page after activating permit session context.
        """
        self.logger.info("Navigating to Junkyard Generate Forms for company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self._wait_for_loader()
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.sidebar_generate_forms_link.is_visible():
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        expect(self.sidebar_generate_forms_link).to_be_visible(timeout=20000)
        self.sidebar_generate_forms_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.dismiss_ok_popups(timeout_ms=1000, max_clicks=1)
        self.verify_junkyard_generate_forms_page_loaded()
        return record_info

    def verify_junkyard_generate_forms_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Verifies that Junkyard Details Permit header, Documents and Letters heading, and form container are visible."""
        expect(self.header_junkyard_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_documents_and_letters).to_be_visible(timeout=timeout_ms)
        expect(self.form_container).to_be_visible(timeout=timeout_ms)

    def generate_first_form(self, timeout_ms: int = 20000) -> Optional[Page]:
        """Reuses parent class 1st form generation flow with modal handling."""
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        popup = super().generate_first_form(timeout_ms=timeout_ms)
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2)
        return popup

    def generate_second_form(
        self, first_popup: Optional[Page] = None, timeout_ms: int = 20000
    ) -> None:
        """Reuses parent class 2nd form generation flow with modal handling."""
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        super().generate_second_form(first_popup=first_popup, timeout_ms=timeout_ms)
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=2)

    def generate_forms_full_workflow(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Executes complete Junkyard Generate Forms workflow.
        """
        self.navigate_to_junkyard_generate_forms(company_name=company_name)
        first_popup = self.generate_first_form()
        self.generate_second_form(first_popup=first_popup)
