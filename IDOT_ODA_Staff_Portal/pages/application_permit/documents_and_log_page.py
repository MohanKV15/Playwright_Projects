import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class DocumentsAndLogPage(BasePage):
    """
    Dedicated Page Object Model representing the Documents and Communication Log
    shared module in the IDOT Outdoor Advertising Staff Portal.

    This component encapsulates:
    - Attaching documents (file upload, preparation date, title, description, save)
    - Adding communications (date, subject, description, save)
    - Table grid verification (#LogListGrid)
    - Send Email modal (open and dismiss)

    Can be used directly for the 'Documents and Log' sidebar menu or composed
    into other workflow pages (e.g. InspectionPage, ApplicationDetailsPage).
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Main Action Buttons
        self.attach_document_button = page.locator("button:has-text('Attach Document')").first
        self.add_communication_button = page.locator("button:has-text('Add Communication')").first
        self.send_email_button = page.locator("button:has-text('Send Email')").first
        self.log_list_grid = page.locator(".k-grid-content, #LogListGrid, .k-grid").first

        # 2. Attach Document Subform
        self.prep_date_input = page.locator("#docdate, input[name='docdate']").first
        self.doc_file_input = page.locator("input[type='file']").first
        self.doc_title_input = page.locator("#doctitle, [name='DocumentTitle']").first
        self.doc_desc_input = page.locator("#docdesc, [name='DocumentDescription']").first
        self.doc_save_button = page.locator(
            "#SaveDocumentBtn, #frmInspectionDocSave button:has-text('Save'), button:has-text('Save')"
        ).first

        # 3. Add Communication Subform
        self.comm_subject_input = page.get_by_role("textbox", name="Subject").or_(
            page.locator("#Subject, [name='Subject'], input[name*='Subject' i]")
        ).first
        self.comm_desc_input = page.get_by_role("textbox", name="Description").or_(
            page.locator("#Description, [name='Description'], textarea[name*='Description' i]")
        ).first
        self.comm_save_button = page.locator("button:has-text('Save')").first

    # -------------------------------------------------------------------------
    # Attach Document Flow
    # -------------------------------------------------------------------------
    def attach_document(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        return_url: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Clicks 'Attach Document', sets Preparation Date with present day date,
        uploads dummy file, populates title and description, and saves the document.
        """
        doc_title = title or f"Doc {fake.word().capitalize()} {fake.random_int(100, 999)}"
        doc_desc = description or fake.sentence(nb_words=5)

        dummy_file = (
            Path(file_path)
            if file_path
            else Config.PROJECT_ROOT / "testdata" / "dummy.pdf"
        )
        assert dummy_file.exists(), f"Upload file not found at: {dummy_file}"

        self.logger.info(f"Attaching document: Title='{doc_title}', File='{dummy_file.name}'")
        expect(self.attach_document_button).to_be_visible(timeout=15000)
        self.attach_document_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        # 1. Populate Preparation Date with present day date (via KendoDatePicker component)
        self.kendo_datepicker.select_present_day_date(field_id="docdate")

        # 2. Upload file
        expect(self.doc_file_input).to_be_attached(timeout=10000)
        self.doc_file_input.set_input_files(str(dummy_file))
        self.page.wait_for_timeout(400)

        # 3. Fill document title and description
        if self.doc_title_input.is_visible():
            self.doc_title_input.fill(doc_title)

        if self.doc_desc_input.is_visible():
            self.doc_desc_input.fill(doc_desc)

        # 4. Save document
        expect(self.doc_save_button).to_be_visible(timeout=10000)
        self.doc_save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)
        self.logger.info(f"Document '{doc_title}' saved successfully")

        # Return to previous details URL if redirected away
        if return_url and "4321LogAttachStaffFull" in self.page.url:
            self.logger.info(f"Returning to previous view: {return_url}")
            self.navigate(return_url)
            self._wait_for_loader()
            self.page.wait_for_timeout(800)

        return {"title": doc_title, "description": doc_desc}

    # -------------------------------------------------------------------------
    # Add Communication Flow
    # -------------------------------------------------------------------------
    def add_communication(
        self,
        subject: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Clicks 'Add Communication', sets present day date, populates subject
        and description, and saves the entry.
        """
        comm_subject = subject or f"Comm {fake.word().capitalize()} {fake.random_int(100, 999)}"
        comm_desc = description or fake.sentence(nb_words=6)

        self.logger.info(f"Adding communication: Subject='{comm_subject}'")
        expect(self.add_communication_button).to_be_visible(timeout=15000)
        self.add_communication_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        # Select present day date
        self.kendo_datepicker.select_present_day_date()

        # Fill subject and description
        expect(self.comm_subject_input).to_be_visible(timeout=10000)
        self.comm_subject_input.fill(comm_subject)

        if self.comm_desc_input.is_visible():
            self.comm_desc_input.fill(comm_desc)

        # Save communication
        expect(self.comm_save_button).to_be_visible(timeout=10000)
        self.comm_save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)
        self.logger.info(f"Communication '{comm_subject}' saved successfully")

        return {"subject": comm_subject, "description": comm_desc}

    # -------------------------------------------------------------------------
    # Table Record Verification Flow
    # -------------------------------------------------------------------------
    def verify_record_in_table(self, expected_text: str, timeout_ms: int = 15000) -> None:
        """
        Verifies that once saved, the record row displays inside the grid table (#LogListGrid).
        """
        self.logger.info(f"Verifying record with text '{expected_text}' displays inside table")
        self._wait_for_loader()
        expect(self.log_list_grid).to_be_visible(timeout=timeout_ms)

        matching_row = self.page.locator(".k-grid-content tbody tr, #LogListGrid tbody tr").filter(
            has_text=expected_text
        ).first
        expect(matching_row).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Record successfully verified inside table: '{matching_row.inner_text().strip()}'")

    # -------------------------------------------------------------------------
    # Send Email Flow (Open & Dismiss)
    # -------------------------------------------------------------------------
    def open_and_cancel_send_email(self, timeout_ms: int = 15000) -> None:
        """
        Clicks 'Send Email' button, verifies the email modal is displayed,
        and clicks 'Cancel' on the modal to dismiss it.
        """
        self.logger.info("Opening Send Email modal")
        expect(self.send_email_button).to_be_visible(timeout=timeout_ms)
        self.send_email_button.click(force=True)
        self._wait_for_loader()

        # Verify email modal content
        modal_header = self.page.get_by_text(
            "Application Details Permit Number Company Name Company Number Company Details"
        ).first
        expect(modal_header).to_be_visible(timeout=timeout_ms)

        # Click visible Cancel button inside modal
        email_modal = self.page.locator(".k-window:visible, .modal:visible, .k-dialog:visible").first
        modal_cancel_btn = email_modal.locator("button:visible").filter(has_text="Cancel").first
        if modal_cancel_btn.is_visible(timeout=3000):
            modal_cancel_btn.click(force=True)
        else:
            self.page.locator("button:visible").filter(has_text="Cancel").first.click(force=True)

        self._wait_for_loader()
        self.logger.info("Send Email modal dismissed successfully")
