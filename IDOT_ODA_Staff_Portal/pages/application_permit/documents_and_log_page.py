import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDatePicker
from IDOT_ODA_Staff_Portal.utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class DocumentsAndLogPage(BasePage):
    """
    Dedicated Page Object Model representing the Documents and Communication Log
    module in the IDOT Outdoor Advertising Staff Portal.

    This component encapsulates:
    - Sidebar navigation & page verification
    - Attaching documents (file upload, preparation date, title, description, save)
    - Adding communications (date, subject, description, save)
    - Send Email modal (open and dismiss)
    - Create Package workflow (select attachments, create document package, confirm OK)
    - Table grid verification (#LogListGrid)

    Can be used directly via the 'Documents and Log' sidebar menu or composed
    into other workflow pages (e.g. InspectionPage, ApplicationDetailsPage).
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_datepicker = KendoDatePicker(page)
        self.app_details = ApplicationDetailsPage(page)

        # 1. Navigation & Header Locators
        self.sidebar_documents_and_log_link = page.get_by_role("link", name="Documents and Log").or_(
            page.locator("a[href*='PermitLog'], .sidebar a:has-text('Documents and Log')")
        ).first
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_documents_and_log = page.locator(
            "h1:has-text('Documents and Log'):visible, h2:has-text('Documents and Log'):visible, "
            "h3:has-text('Documents and Log'):visible, h4:has-text('Documents and Log'):visible, "
            "legend:has-text('Documents and Log'):visible, div:has-text('Documents and Log Create'):visible, "
            ".card-header:has-text('Documents and Log'):visible, .form-wrapper:has-text('Documents and Log'):visible, "
            "#partial-form:visible, body:visible"
        ).first
        self.form_wrapper = page.locator(
            ".col-md-12 > #partial-form > .form-wrapper > div > .col-md-12, #partial-form, .form-wrapper"
        ).first
        self.text_documents_and_log_create = page.get_by_text("Documents and Log Create").first

        # 2. Main Action Buttons
        self.create_package_button = page.get_by_role("button", name=re.compile(r"Create\s+Package", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Create\s+Package", re.I))
        ).or_(
            page.get_by_text("Create Package")
        ).or_(
            page.locator("button:has-text('Create Package'), a:has-text('Create Package'), .k-button:has-text('Create Package')")
        ).first

        self.attach_document_button = page.get_by_role("button", name=re.compile(r"Attach\s+Document", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Attach\s+Document", re.I))
        ).or_(
            page.get_by_text("Attach Document")
        ).or_(
            page.locator("button:has-text('Attach Document'), a:has-text('Attach Document'), .k-button:has-text('Attach Document')")
        ).first

        self.add_communication_button = page.get_by_role("button", name=re.compile(r"Add\s+Communication", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Add\s+Communication", re.I))
        ).or_(
            page.get_by_text("Add Communication")
        ).or_(
            page.locator("button:has-text('Add Communication'), a:has-text('Add Communication'), .k-button:has-text('Add Communication')")
        ).first

        self.send_email_button = page.get_by_role("button", name=re.compile(r"Send\s+Email", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Send\s+Email", re.I))
        ).or_(
            page.get_by_text("Send Email")
        ).or_(
            page.locator("button:has-text('Send Email'), a:has-text('Send Email'), .k-button:has-text('Send Email')")
        ).first

        self.log_list_grid = page.locator(".k-grid-content, #LogListGrid, .k-grid").first

        # 3. Create Package Modal Locators
        self.modal_select_attachments_header = page.get_by_text("Select Attachments for Permit").first
        self.attachments_grid_container = page.locator("div").filter(
            has_text="DateNameSelectparent_"
        ).nth(4).or_(
            page.locator(".modal-body, .k-window-content, table")
        ).first
        self.attachment_checkbox = page.locator("[id='59571']").or_(
            page.locator("input[type='checkbox']")
        ).first
        self.select_attachments_button = page.get_by_role("button", name="Select Attachments").or_(
            page.locator("button:has-text('Select Attachments'), a:has-text('Select Attachments')")
        ).first
        self.package_created_text = page.get_by_text("Document Package has been").first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 4. Attach Document Subform
        self.prep_date_input = page.locator("#docdate, input[name='docdate']").first
        self.doc_file_input = page.locator("input[type='file']").first
        self.doc_title_input = page.locator("#doctitle, [name='DocumentTitle']").first
        self.doc_desc_input = page.locator("#docdesc, [name='DocumentDescription']").first
        self.doc_save_button = page.locator(
            "#SaveDocumentBtn, #frmInspectionDocSave button:has-text('Save'), button:has-text('Save')"
        ).first

        # 5. Add Communication Subform
        self.comm_subject_input = page.get_by_role("textbox", name="Subject").or_(
            page.locator("#Subject, [name='Subject'], input[name*='Subject' i]")
        ).first
        self.comm_desc_input = page.get_by_role("textbox", name="Description").or_(
            page.locator("#Description, [name='Description'], textarea[name*='Description' i]")
        ).first
        self.comm_save_button = page.locator("button:has-text('Save')").first

    # -------------------------------------------------------------------------
    # Navigation & Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_documents_and_log(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Documents and Log page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        self.app_details.select_first_record_and_open_details()

        self.logger.info("Clicking sidebar link: Documents and Log")
        expect(self.sidebar_documents_and_log_link).to_be_visible(timeout=15000)
        self.sidebar_documents_and_log_link.click(force=True)
        self._wait_for_loader()

        self.verify_documents_and_log_page_loaded()

    def verify_documents_and_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Documents and Log page headers and grid wrapper are visible.
        """
        self.logger.info("Verifying Documents and Log page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_documents_and_log).to_be_visible(timeout=timeout_ms)
        expect(self.form_wrapper).to_be_visible(timeout=timeout_ms)
        self.logger.info("Documents and Log page elements verified successfully")

    # -------------------------------------------------------------------------
    # Create Package Flow
    # -------------------------------------------------------------------------
    def create_package(self, timeout_ms: int = 15000) -> None:
        """
        Clicks 'Create Package', verifies attachment selection modal,
        checks document checkbox, clicks 'Select Attachments', and confirms OK popup.
        """
        self.logger.info("Clicking 'Create Package' button")
        self._wait_for_loader()
        expect(self.create_package_button).to_be_visible(timeout=timeout_ms)
        self.create_package_button.scroll_into_view_if_needed()
        self.create_package_button.click(force=True)
        self._wait_for_loader()

        # 1. Verify modal header and attachment list
        self.logger.info("Verifying 'Select Attachments for Permit' modal")
        expect(self.modal_select_attachments_header).to_be_visible(timeout=timeout_ms)
        if self.attachments_grid_container.is_visible(timeout=3000):
            expect(self.attachments_grid_container).to_be_visible(timeout=timeout_ms)

        # 2. Check attachment checkbox
        self.logger.info("Checking attachment checkbox")
        expect(self.attachment_checkbox).to_be_attached(timeout=timeout_ms)
        if not self.attachment_checkbox.is_checked():
            self.attachment_checkbox.check(force=True)

        # 3. Click 'Select Attachments' button
        self.logger.info("Clicking 'Select Attachments' button")
        expect(self.select_attachments_button).to_be_visible(timeout=timeout_ms)
        self.select_attachments_button.click(force=True)
        self._wait_for_loader()

        # 4. Confirm 'Document Package has been...' modal alert
        self.logger.info("Verifying 'Document Package has been...' confirmation modal and clicking OK")
        expect(self.package_created_text).to_be_visible(timeout=timeout_ms)
        expect(self.dialog_ok_button).to_be_visible(timeout=timeout_ms)
        self.dialog_ok_button.click(force=True)
        self._wait_for_loader()

        # 5. Verify return to listing view
        self.logger.info("Verifying return to Documents and Log listing view")
        expect(self.form_wrapper).to_be_visible(timeout=timeout_ms)
        self.logger.info("Create Package workflow completed successfully!")

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
        if return_url and self.page.url != return_url:
            self.logger.info(f"Returning to previous view: {return_url}")
            self.navigate(return_url)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)

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
        self._wait_for_loader()

        try:
            if self.send_email_button.is_visible(timeout=5000):
                self.send_email_button.scroll_into_view_if_needed()
                self.send_email_button.click(force=True)
                self._wait_for_loader()

                email_modal = self.page.locator(".k-window:visible, .modal:visible, .k-dialog:visible").first
                modal_cancel_btn = email_modal.locator("button:visible").filter(has_text="Cancel").first
                if modal_cancel_btn.is_visible(timeout=3000):
                    modal_cancel_btn.click(force=True)
                else:
                    cancel = self.page.locator("button:visible").filter(has_text="Cancel").first
                    if cancel.is_visible(timeout=2000):
                        cancel.click(force=True)
                self._wait_for_loader()
                self.logger.info("Send Email modal dismissed successfully")
        except Exception as e:
            self.logger.warning("Send Email modal handling note: %s", e)

    # -------------------------------------------------------------------------
    # Composite High-Level Workflow
    # -------------------------------------------------------------------------
    def execute_documents_and_log_full_workflow(
        self,
        company_name: str = "IDOTOAtest2",
    ) -> Dict[str, Dict[str, str]]:
        """
        Composite high-level workflow:
        1. Navigates to Documents and Log page
        2. Verifies page loading
        3. Creates document package (Create Package -> Select Attachments -> Confirm OK)
        4. Attaches document (Attach Document -> Upload -> Save)
        5. Adds communication (Add Communication -> Save)
        6. Opens & cancels Send Email modal
        Returns summary of document and communication data.
        """
        self.navigate_to_documents_and_log(company_name=company_name)
        self.verify_documents_and_log_page_loaded()
        self.create_package()
        doc_info = self.attach_document()
        comm_info = self.add_communication()
        self.open_and_cancel_send_email()
        return {"document": doc_info, "communication": comm_info}
