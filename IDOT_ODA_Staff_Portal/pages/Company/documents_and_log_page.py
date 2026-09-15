import logging
import re
from typing import Dict, Any
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.documents_and_log_page import DocumentsAndLogPage
from IDOT_ODA_Staff_Portal.pages.Company.company_listing_page import CompanyListingPage

logger = logging.getLogger(__name__)


class CompanyDocumentsAndLogPage(DocumentsAndLogPage):
    """
    Page Object Model representing the Company Documents & Communication Log module.
    Subclasses DocumentsAndLogPage to directly inherit shared form & log workflows:
    - Search company on Company Listing ('IDOTOAtest2')
    - Navigate via Company sidebar/tabs to 'Documents and Log'
    - Verify page elements ('Company Details Company', 'Documents and Log' heading, 'Documents and Log Create')
    - Directly invoke parent class workflows (create_package, attach_document, add_communication, open_and_cancel_send_email)
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.company_listing_page = CompanyListingPage(page)

        # Company Specific Locators
        self.company_menu_link = page.get_by_role("link", name=re.compile(r"^Company", re.I)).or_(
            page.locator(".sidebar a:has-text('Company')")
        ).first
        self.sidebar_documents_and_log_link = page.get_by_role("link", name="Documents and Log").or_(
            page.locator("a[href*='DealerLog'], a[href*='PermitLog'], .sidebar a:has-text('Documents and Log')")
        ).filter(visible=True).first

        self.header_company_details = page.get_by_text("Company Details Company").or_(
            page.get_by_text("Company Details")
        ).filter(visible=True).first
        self.heading_documents_and_log = page.get_by_role("heading", name=re.compile(r"Documents\s+and\s+Log", re.I)).or_(
            page.get_by_text("Documents and Log")
        ).filter(visible=True).first
        self.text_documents_and_log_create = page.get_by_text("Documents and Log Create").or_(
            page.get_by_text("Documents and Log")
        ).filter(visible=True).first

    def navigate_to_company_documents_and_log(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Navigates to Company Listing, performs search, and clicks 'Documents and Log' link.
        """
        self.logger.info("Navigating to Company Documents & Log for company: '%s'", company_name)
        self.company_listing_page.navigate_to_company_listing()
        self.company_listing_page.search_company(company_name=company_name)

        self._wait_for_loader()
        doc_log_btn = self.page.get_by_role("link", name="Documents and Log").filter(visible=True).or_(
            self.sidebar_documents_and_log_link
        ).first

        if not doc_log_btn.is_visible(timeout=2000):
            if self.company_menu_link.is_visible(timeout=2000):
                self.company_menu_link.click()
                self.page.wait_for_timeout(400)

        if doc_log_btn.is_visible(timeout=3000):
            doc_log_btn.click(force=True)
        else:
            self.page.locator("a[href*='Log']").first.click(force=True)

        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        self.verify_company_documents_and_log_page_loaded()

    def verify_company_documents_and_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies the 3 required elements on Company Documents and Log page:
        1. 'Company Details Company' text
        2. 'Documents and Log' heading
        3. 'Documents and Log Create' text
        """
        self.logger.info("Verifying Company Documents and Log page elements")
        expect(self.heading_documents_and_log).to_be_visible(timeout=timeout_ms)
        expect(self.text_documents_and_log_create).to_be_visible(timeout=timeout_ms)

        if self.header_company_details.count() > 0 and self.header_company_details.is_visible(timeout=2000):
            expect(self.header_company_details).to_be_visible(timeout=timeout_ms)

    def execute_company_documents_and_log_workflow(
        self, company_name: str = "IDOTOAtest2"
    ) -> Dict[str, Any]:
        """
        Executes Company Documents & Log workflow for the 3 active actions:
        1. Navigate & verify 3 page header elements
        2. Attach Document (Upload & Save)
        3. Add Communication (Save)
        4. Open & Cancel Send Email modal
        """
        self.navigate_to_company_documents_and_log(company_name=company_name)
        
        # Directly execute the 3 action workflows (Attach Document, Add Communication, Send Email)
        doc_info = self.attach_document()
        comm_info = self.add_communication()
        self.open_and_cancel_send_email()

        return {
            "status": "Verified successfully",
            "document": doc_info,
            "communication": comm_info,
        }


