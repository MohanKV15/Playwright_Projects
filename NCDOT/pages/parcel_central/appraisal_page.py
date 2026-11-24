import logging
import os
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker()


class AppraisalPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Appraisal:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Navigates to 'Appraisal' via #navigationMenu2 sidebar menu.
      - Verifies Appraisal Landing page ('Appraisal Drop Zone' and grid).
      - Opens Appraisal Details by clicking the row action button (#appraisalDetails).
      - Documents Tab: Navigates and verifies document container visibility.
      - Log Tab:
        * Adds Call Data with dummy Subject, saves, and returns via #btnBacknotes.
        * Adds Notes with dummy Subject, saves, and returns via #btnBacknotes.
        * Adds Attachment: selects 1st available Document Type from dropdown via separated KendoDropdown component,
          uploads dummy file, enters dummy Subject, and saves.
      - Verifies clean state without errors across all operations.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Landing Container
        self.appraisal_nav_link = (
            page.locator("#navigationMenu2, #navigationMenu")
            .get_by_text("Appraisal", exact=True)
            .or_(page.locator("nav, ul, .k-panelbar").get_by_text("Appraisal", exact=True))
            .or_(page.get_by_text("Appraisal", exact=True))
        )
        self.appraisal_drop_zone = page.locator(":has-text('Appraisal Drop Zone'), #appraisalGrid, .k-grid")

        # 2. Appraisal Details & Grid Actions
        self.appraisal_grid_rows = page.locator("tbody tr, .k-grid-content tr")
        self.row_edit_button = page.locator(
            ".editOwnerClass, button:has(.k-i-edit), button[name*='Edit'], button[id*='Edit']"
        )
        self.appraisal_details_container = page.locator("#appraisalDetails")

        # 3. Parcel Central Sub-Tabs Strip
        self.parcel_central_tabs = page.locator("#ParcelCentralTab")

        # 4. Documents Tab Locators
        self.documents_container = page.locator(
            ".col-md-12.pr-0, #partial-form:visible, #ParcelCentralTab-9:visible"
        )

        # 5. Log Tab Locators
        self.log_container = page.locator(
            "#divLogTable:visible, #divLgTable:visible, button#btnAddCallData:visible"
        )
        self.add_call_data_button = page.locator(
            "button#btnAddCallData:visible, button:visible:has-text('Add Call Data')"
        )
        self.add_notes_button = page.locator(
            "button#btnAddNotes:visible, button:visible:has-text('Add Notes')"
        )
        self.add_attachment_button = page.locator(
            "button#btnAddAttachment:visible, button:visible:has-text('Add Attachment')"
        )
        self.log_subject_input = (
            page.locator(
                "input#log_subject:visible, input[name='log_subject']:visible"
            )
            .or_(page.get_by_role("textbox", name=re.compile(r"Subject", re.I)))
        )
        self.log_save_button = page.locator(
            "#btnSubmit:visible, button#btnSubmit:visible, button:visible:has-text('Save')"
        )
        self.log_back_button = page.locator(
            "#btnBacknotes:visible, button#btnBacknotes:visible"
        )

        # 6. Add Attachment Form Locators
        self.attachment_container = page.locator("#CommLogDiv:visible, #divCommLog:visible")
        self.doc_type_dropdown = page.locator(
            "#CommLogDiv span.k-widget.k-dropdown, #CommLogDiv span.k-dropdown-wrap, #CommLogDiv .k-dropdown, span.k-widget.k-dropdown:has(#doctype_id)"
        )
        self.file_input = page.locator(
            "#CommLogDiv input#files[type='file'], input#files[type='file'], input[type='file']"
        )
        self.attachment_subject_input = page.locator(
            "#CommLogDiv input#doctitle:visible, input#doctitle:visible"
        )
        self.attachment_save_button = page.locator(
            "#SaveDocumentBtn:visible, button#SaveDocumentBtn, #CommLogDiv button:has-text('Save'), button:visible:has-text('Save')"
        )

        # 7. Error / Validation Alerts
        self.error_alerts = page.locator(
            ".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible"
        )

    # =========================================================================
    # Navigation & Subtab Switching
    # =========================================================================

    def navigate_to_appraisal(self) -> "AppraisalPage":
        """Navigates to Appraisal sub-menu and verifies Drop Zone / grid visibility."""
        self.logger.info("Navigating to Appraisal sub-menu via sidebar")
        self._wait_for_loader()
        self.appraisal_nav_link.first.wait_for(state="visible", timeout=15000)
        self.appraisal_nav_link.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        expect(self.appraisal_drop_zone.first).to_be_visible(timeout=15000)
        return self

    def open_appraisal_details(
        self,
        row_name: Optional[str] = "Brad Bass",
        row_index: int = 0,
    ) -> "AppraisalPage":
        """
        Opens Appraisal Details by clicking the edit/action button on the target row
        (or 1st available row) and verifies #appraisalDetails visibility.
        """
        self.logger.info(f"Opening Appraisal Details (row_name='{row_name}', index={row_index})")
        self._wait_for_loader()

        target_row = None
        if row_name:
            matched_rows = self.appraisal_grid_rows.filter(has_text=re.compile(re.escape(row_name), re.I))
            if matched_rows.count() > 0 and matched_rows.first.is_visible():
                target_row = matched_rows.first

        if target_row and target_row.locator(self.row_edit_button).count() > 0:
            target_row.locator(self.row_edit_button).first.click()
        elif self.row_edit_button.count() > 0:
            self.row_edit_button.nth(row_index).click()
        else:
            self.appraisal_grid_rows.first.locator("button, a").first.click()

        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.appraisal_details_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Appraisal Details opened successfully.")
        return self

    def switch_subtab(self, tab_name: str) -> "AppraisalPage":
        """Delegates subtab switching to the KendoTabStrip component and synchronizes loaders."""
        self.logger.info(f"Switching to subtab '{tab_name}' via KendoTabStrip component")
        self._wait_for_loader()
        self.kendo_tabstrip.select_tab(self.parcel_central_tabs, tab_name)
        self.page.wait_for_timeout(300)
        self._wait_for_loader()
        return self

    # =========================================================================
    # Section 1: Documents Tab Operations
    # =========================================================================

    def navigate_to_documents_tab(self) -> "AppraisalPage":
        """Clicks 'Documents' tab and verifies view container visibility."""
        self.logger.info("Documents Tab: Navigating and verifying container")
        self.switch_subtab("Documents")
        expect(self.documents_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Documents Tab: Verified successfully.")
        return self

    # =========================================================================
    # Section 2: Log Tab Operations
    # =========================================================================

    def navigate_to_log_tab(self) -> "AppraisalPage":
        """Navigates to Log tab, verifies log table is displayed, and checks for zero errors."""
        self.logger.info("Log Tab: Navigating to Log tab and verifying table display")
        self.switch_subtab("Log")
        expect(self.log_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Log Tab: Verified table displayed cleanly without errors.")
        return self

    def _create_log_entry(self, trigger_button: Locator, subject: str, entry_type: str = "Entry") -> None:
        """Helper to create a log entry (Call Data or Notes), save, and return via #btnBacknotes."""
        self.logger.info(f"Log Tab: Creating {entry_type} with subject '{subject}'")
        btn = trigger_button.first
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        subj = self.log_subject_input.first
        subj.wait_for(state="visible", timeout=15000)
        subj.click()
        subj.fill(subject)
        self.page.wait_for_timeout(300)

        save_btn = self.log_save_button.first
        save_btn.wait_for(state="visible", timeout=15000)
        save_btn.click()
        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        back_btn = self.log_back_button.first
        back_btn.wait_for(state="visible", timeout=15000)
        back_btn.click()
        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        self.log_container.first.wait_for(state="visible", timeout=15000)

    def add_call_data(self, subject: Optional[str] = None) -> "AppraisalPage":
        """Adds a Call Data entry using dummy Faker data, saves, and returns."""
        c_subj = subject or f"Call {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_call_data_button, c_subj, entry_type="Call Data")
        self.verify_no_errors()
        return self

    def add_notes(self, subject: Optional[str] = None) -> "AppraisalPage":
        """Adds a Notes entry using dummy Faker data, saves, and returns."""
        n_subj = subject or f"Note {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_notes_button, n_subj, entry_type="Notes")
        self.verify_no_errors()
        return self

    def _get_or_create_dummy_file(self) -> str:
        """Ensures a valid sample file exists for attachment upload and returns its absolute path."""
        testdata_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "testdata")
        os.makedirs(testdata_dir, exist_ok=True)
        sample_path = os.path.join(testdata_dir, "dummy_sample.txt")
        if not os.path.exists(sample_path):
            with open(sample_path, "w") as f:
                f.write("This is a dummy test attachment for NCDOT appraisal automation.")
        return sample_path

    def add_attachment(
        self,
        file_path: Optional[str] = None,
        subject: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> "AppraisalPage":
        """
        Adds an attachment:
          1. Clicks 'Add Attachment' and waits for #CommLogDiv container.
          2. Selects the 1st available Document Type option via KendoDropdown component (or specified doc_type).
          3. Uploads the dummy file.
          4. Enters Subject.
          5. Clicks Save and handles alert dialog via KendoDialog.
        """
        upload_path = file_path or self._get_or_create_dummy_file()
        att_subj = subject or f"Att {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self.logger.info(f"Log Tab: Adding Attachment (file='{os.path.basename(upload_path)}', subject='{att_subj}')")

        attach_btn = self.add_attachment_button.first
        attach_btn.wait_for(state="visible", timeout=15000)
        attach_btn.click()

        # Wait for #CommLogDiv container to open
        self.attachment_container.first.wait_for(state="visible", timeout=15000)
        self._wait_for_loader()

        # Select Document Type via separated KendoDropdown component
        if doc_type:
            self.kendo_dropdown.select_option(self.doc_type_dropdown, doc_type)
        else:
            self.kendo_dropdown.select_first_option(self.doc_type_dropdown)
        self.page.wait_for_timeout(300)

        # Upload file via file input
        file_inp = self.file_input.first
        file_inp.set_input_files(upload_path)
        self.page.wait_for_timeout(500)

        # Fill Subject
        subj_inp = self.attachment_subject_input.first
        subj_inp.wait_for(state="visible", timeout=10000)
        subj_inp.fill(att_subj)
        self.page.wait_for_timeout(300)

        # Click Save
        save_btn = self.attachment_save_button.first
        save_btn.wait_for(state="attached", timeout=15000)
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()

        # Verify returned to log table
        expect(self.log_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Attachment uploaded and saved successfully.")
        return self

    # =========================================================================
    # Error Verification
    # =========================================================================

    def verify_no_errors(self) -> "AppraisalPage":
        """Verifies that no error alerts or validation errors are displayed."""
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self
