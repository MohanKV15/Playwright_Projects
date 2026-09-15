import logging
from typing import Dict
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.documents_and_log_page import DocumentsAndLogPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage

logger = logging.getLogger(__name__)


class JunkyardDocumentsAndLogPage(DocumentsAndLogPage):
    """
    Optimized Page Object Model representing the Junkyards Documents & Communication Log module
    in the IDOT Outdoor Advertising Staff Portal.

    Subclasses DocumentsAndLogPage to directly inherit shared form & log workflows:
    - Search company on Junkyard/Permit Search ('IDOTOAtest2')
    - Select 1st record row to activate permit session context
    - Navigate via Junkyards sidebar to 'Documents and Log'
    - Verify page headers ('Junkyard Details Permit', 'Documents and Log')
    - Directly invoke parent workflows (create_package, attach_document, add_communication, open_and_cancel_send_email)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Junkyards Specific Sidebar & Header Locators
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_documents_and_log_link = page.get_by_role("link", name="Documents and Log").filter(visible=True).or_(
            page.locator("a[href*='PermitLog']").filter(visible=True)
        ).first
        self.header_junkyard_details_permit = page.get_by_text("Junkyard Details Permit").or_(
            page.get_by_text("Application Details Permit")
        ).first
        self.heading_documents_and_log = page.get_by_role("heading", name="Documents and Log").filter(visible=True).or_(
            page.locator(
                "h1:has-text('Documents and Log'):visible, h2:has-text('Documents and Log'):visible, "
                "legend:has-text('Documents and Log'):visible, #partial-form:visible"
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

    def navigate_to_junkyard_documents_and_log(self, company_name: str = "IDOTOAtest2") -> str:
        """
        Navigates to Junkyard Documents and Log page after activating permit session context.
        """
        self.logger.info("Navigating to Junkyard Documents & Log for company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self._wait_for_loader()
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.sidebar_documents_and_log_link.is_visible():
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        expect(self.sidebar_documents_and_log_link).to_be_visible(timeout=20000)
        self.sidebar_documents_and_log_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.dismiss_ok_popups(timeout_ms=1000, max_clicks=1)
        self.verify_junkyard_documents_and_log_page_loaded()
        return record_info

    def verify_junkyard_documents_and_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Verifies that Junkyard Details Permit header and Documents and Log heading are visible."""
        expect(self.header_junkyard_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_documents_and_log).to_be_visible(timeout=timeout_ms)

    def execute_junkyard_documents_and_log_full_workflow(
        self, company_name: str = "IDOTOAtest2"
    ) -> Dict[str, Dict[str, str]]:
        """
        Executes complete Junkyard Documents & Log workflow using parent class implementations.
        """
        self.navigate_to_junkyard_documents_and_log(company_name=company_name)
        self.create_package()
        doc_info = self.attach_document()
        comm_info = self.add_communication()
        self.open_and_cancel_send_email()
        return {"document": doc_info, "communication": comm_info}
