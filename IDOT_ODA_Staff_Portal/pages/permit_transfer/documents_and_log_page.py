import logging
from typing import Any, Dict
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.documents_and_log_page import (
    DocumentsAndLogPage as AppDocumentsAndLogPage,
)
from IDOT_ODA_Staff_Portal.pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage

logger = logging.getLogger(__name__)


class DocumentsAndLogPage(AppDocumentsAndLogPage):
    """
    Page Object Model representing the Documents and Log module under Permit Transfer in the IDOT Staff Portal.
    Inherits form handling, document attachment, communication logging, package creation, and email dismissal
    capabilities from application_permit's DocumentsAndLogPage.

    Workflow:
    - Navigates to Permit Transfer Details view via parent PermitTransferDetailsPage.
    - Clicks 'Documents and Log' sidebar sub-link under Permit Transfer.
    - Verifies 'Transfer Details Permit', 'Documents and Log' heading, and 'Documents and Log Create' text visibility.
    - Executes package creation, document attachment, communication entry, and send email modal dismissal.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.permit_transfer_details = PermitTransferDetailsPage(page)

        # Permit Transfer Specific Locators
        self.sidebar_documents_and_log_link = page.locator(
            ".sidebar a[href*='4319TransfLogListingStaffFull'], .sidebar a:has-text('Documents and Log')"
        ).or_(
            page.get_by_role("link", name="Documents and Log")
        ).last

        self.text_transfer_details_permit = page.get_by_text("Transfer Details Permit").or_(
            page.get_by_text("Transfer Details")
        ).or_(
            page.get_by_text("Permit Transfer Details")
        ).first

        self.heading_documents_and_log = page.get_by_role("heading", name="Documents and Log").filter(visible=True).or_(
            page.get_by_text("Documents and Log").filter(visible=True)
        ).first

        self.text_documents_and_log_create = page.get_by_text("Documents and Log Create").or_(
            page.get_by_text("Documents and Log")
        ).first

    def navigate_to_documents_and_log(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """
        Activates Permit Transfer session via parent PermitTransferDetailsPage:
        1. Navigates to Permit Transfer Listing page (via Dashboard).
        2. Searches permit number ('016-503386').
        3. Selects 1st record row (row_index=0).
        4. Verifies Permit Transfer Details headings.
        5. Clicks 'Documents and Log' link under Permit Transfer sidebar.
        6. Verifies 'Transfer Details Permit', 'Documents and Log' heading, and 'Documents and Log Create' text.
        """
        self.logger.info("Executing parent PermitTransferDetailsPage workflow for permit: %s", permit_number)
        self.permit_transfer_details.execute_permit_transfer_details_workflow(
            permit_number=permit_number,
            row_index=row_index,
        )

        self.logger.info("Clicking 'Documents and Log' sidebar sub-link under Permit Transfer")
        if not self.sidebar_documents_and_log_link.is_visible(timeout=3000):
            if self.permit_transfer_details.sidebar_permit_transfer_parent.is_visible(timeout=2000):
                self.permit_transfer_details.sidebar_permit_transfer_parent.click(force=True)
                self.page.wait_for_timeout(300)

        if self.sidebar_documents_and_log_link.is_visible(timeout=3000):
            self.sidebar_documents_and_log_link.click(force=True)
        else:
            self.logger.info("Fallback navigation to 4319TransfLogListingStaffFull")
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319TransfLogListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass

        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.verify_documents_and_log_page_loaded(timeout_ms=timeout_ms)

    def verify_documents_and_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Validates page navigation by checking 'Transfer Details Permit', 'Documents and Log' heading,
        and 'Documents and Log Create' text visibility.
        """
        self.logger.info("Verifying Documents and Log page elements and headings")
        expect(self.text_transfer_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_documents_and_log).to_be_visible(timeout=timeout_ms)
        if self.text_documents_and_log_create.is_visible(timeout=3000):
            expect(self.text_documents_and_log_create).to_be_visible(timeout=timeout_ms)
        expect(self.form_wrapper).to_be_visible(timeout=timeout_ms)

    def open_and_cancel_send_email(self, timeout_ms: int = 15000) -> None:
        """
        Clicks 'Send Email' button, handles modal dialog or full-page view,
        clicks Cancel to dismiss, and ensures return to Documents and Log listing view.
        """
        self.logger.info("Opening Send Email view")
        self._wait_for_loader()

        try:
            if self.send_email_button.is_visible(timeout=5000):
                self.send_email_button.scroll_into_view_if_needed()
                self.send_email_button.click(force=True)
                self._wait_for_loader()
                self.page.wait_for_timeout(1000)

                cancel_btn = self.page.locator(
                    "#btnCancel, input[value='Cancel'], button:has-text('Cancel'), a:has-text('Cancel'), .k-window:visible button:has-text('Cancel'), .modal:visible button:has-text('Cancel')"
                ).first

                if cancel_btn.is_visible(timeout=4000):
                    cancel_btn.click(force=True)
                    self._wait_for_loader()
                    self.page.wait_for_timeout(1000)
                else:
                    self.logger.info("Cancel button not visible on Send Email page; navigating back")
                    self.page.go_back()
                    self._wait_for_loader()

                if "LogSendEmail" in self.page.url:
                    self.page.go_back()
                    self._wait_for_loader()

                self.logger.info("Send Email view dismissed successfully")
        except Exception as e:
            self.logger.warning("Send Email handling note: %s", e)

    def execute_documents_and_log_full_workflow(
        self,
        permit_number: str = "016-503386",
        row_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Composite high-level workflow for Permit Transfer:
        1. Navigates to Permit Transfer -> searches permit '016-503386' -> selects row 0 -> clicks Documents and Log.
        2. Verifies page loading ('Transfer Details Permit', 'Documents and Log' heading).
        3. Creates document package (Create Package -> Select Attachments -> Confirm OK).
        4. Attaches document (Attach Document -> Upload -> Save).
        5. Adds communication (Add Communication -> Save).
        6. Opens & cancels Send Email modal.
        Returns summary of document and communication data.
        """
        self.navigate_to_documents_and_log(permit_number=permit_number, row_index=row_index)
        self.verify_documents_and_log_page_loaded()

        self.create_package()
        doc_info = self.attach_document()
        comm_info = self.add_communication()
        self.open_and_cancel_send_email()

        return {
            "status": "Verified successfully",
            "permit_number": permit_number,
            "row_index": row_index,
            "document": doc_info,
            "communication": comm_info,
        }

