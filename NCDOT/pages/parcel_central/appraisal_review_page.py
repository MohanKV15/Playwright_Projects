import logging
import os
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage
from utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class AppraisalReviewPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Appraisal Review:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Navigates to 'Appraisal Review' via #navigationMenu2 sidebar menu.
      - Verifies Landing page container (#partialForm #partial-form).
      - Opens Appraisal Review Details via row action button (#tcAppraisalReviewEditIPV).
      - Clicks 'Edit' (#btnEditReviewDetailsTab), then 'Save' (#btnSaveReviewDetailsTab).
      - Switches to 'Log' tab (#AppraisalReviewTabs) via separated KendoTabStrip component.
      - Performs Log operations (Call Data, Notes, Attachment) using Faker data and separated Kendo components:
        * Adds Call Data with dummy Subject, saves, and returns via #btnBacknotes.
        * Adds Notes with dummy Subject, saves, and returns via #btnBacknotes.
        * Adds Attachment: selects 1st available Document Type from dropdown via separated KendoDropdown component,
          uploads dummy file, enters dummy Subject, and saves via #SaveDocumentBtn.
      - Verifies clean state without errors across all operations.
    """

    # Section Constants
    TAB_LOG: str = "Log"
    TAB_STATUS: str = "Status"
    DEFAULT_SAMPLE_FILENAME: str = "dummy_sample.txt"

    def __init__(self, page: Page):
        super().__init__(page)

        # ---------------------------------------------------------------------
        # 1. Navigation & Landing Container
        # ---------------------------------------------------------------------
        self.appraisal_review_nav_link = (
            page.locator("#navigationMenu2, #navigationMenu")
            .get_by_text("Appraisal Review", exact=True)
            .or_(page.locator("nav, ul, .k-panelbar").get_by_text("Appraisal Review", exact=True))
            .or_(page.get_by_text("Appraisal Review", exact=True))
        )
        self.landing_content_container = page.locator("#partialForm #partial-form, #partial-form")

        # ---------------------------------------------------------------------
        # 2. Row Action Button & Review Details Container
        # ---------------------------------------------------------------------
        self.row_review_edit_button = page.locator(
            "#tcAppraisalReviewEditIPV:visible, a#tcAppraisalReviewEditIPV, button#tcAppraisalReviewEditIPV"
        )
        self.review_details_container = page.locator(
            "#AppraisalReviewTabs, #partial-form, #divAppraisalReviewDetails"
        )

        # ---------------------------------------------------------------------
        # 3. Appraisal Review Action Buttons
        # ---------------------------------------------------------------------
        self.edit_review_button = page.locator(
            "#btnEditReviewDetailsTab:visible, button#btnEditReviewDetailsTab"
        ).or_(page.get_by_role("button", name=re.compile(r"Edit", re.I)))

        self.save_review_button = page.locator(
            "#btnSaveReviewDetailsTab:visible, button#btnSaveReviewDetailsTab"
        ).or_(page.get_by_role("button", name=re.compile(r"Save", re.I)))

        self.cancel_review_button = page.locator(
            "#btnCancelReviewDetailsTab:visible, button#btnCancelReviewDetailsTab"
        )
        self.back_to_reviews_button = page.locator(
            "#backbtnreview:visible, button#backbtnreview"
        )

        # ---------------------------------------------------------------------
        # 4. Details TabStrip (#AppraisalReviewTabs)
        # ---------------------------------------------------------------------
        self.appraisal_review_tabs = page.locator("#AppraisalReviewTabs")

        # ---------------------------------------------------------------------
        # 5. Log Tab Locators & Triggers
        # ---------------------------------------------------------------------
        self.log_container = page.locator(
            "#divLogTable:visible, #divLgTable:visible, button#btnAddCallData:visible"
        )
        self.log_table_header = page.get_by_text(
            "Type --Select Type-- Date - From To Subject Create Package Refresh Add Call"
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

        # ---------------------------------------------------------------------
        # 6. Log Form Locators (Call Data / Notes)
        # ---------------------------------------------------------------------
        self.log_subject_input = (
            page.locator("input#log_subject:visible, input[name='log_subject']:visible")
            .or_(page.get_by_role("textbox", name=re.compile(r"Subject", re.I)))
        )
        self.log_save_button = page.locator(
            "#btnSubmit:visible, button#btnSubmit:visible, button:visible:has-text('Save')"
        )
        self.log_back_button = page.locator(
            "#btnBacknotes:visible, button#btnBacknotes:visible"
        )

        # ---------------------------------------------------------------------
        # 7. Add Attachment Form Locators
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # 8. Error / Validation Alerts
        # ---------------------------------------------------------------------
        self.error_alerts = page.locator(
            ".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible"
        )

    # =========================================================================
    # Navigation & Subtab Switching
    # =========================================================================

    def navigate_to_appraisal_review(self) -> "AppraisalReviewPage":
        """
        Navigates to Appraisal Review sub-menu in the left navigation sidebar
        and verifies the landing container visibility.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        self.logger.info("Navigating to Appraisal Review sub-menu via sidebar")
        self._wait_for_loader()
        self.appraisal_review_nav_link.first.wait_for(state="visible", timeout=15000)
        self.appraisal_review_nav_link.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        expect(self.landing_content_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        return self

    def open_appraisal_review_details(self, row_index: int = 0) -> "AppraisalReviewPage":
        """
        Opens Appraisal Review Details by clicking the row action button (#tcAppraisalReviewEditIPV).

        Args:
            row_index (int): 0-based index of the target row in the grid (default: 0).

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        self.logger.info(f"Opening Appraisal Review Details (row_index={row_index})")
        self._wait_for_loader()
        self.row_review_edit_button.first.wait_for(state="visible", timeout=15000)
        self.row_review_edit_button.nth(row_index).click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.review_details_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Appraisal Review Details opened successfully.")
        return self

    def click_edit_review(self) -> "AppraisalReviewPage":
        """Clicks 'Edit' button on Appraisal Review Details."""
        self.logger.info("Appraisal Review Details: Clicking 'Edit'")
        self.edit_review_button.first.wait_for(state="visible", timeout=15000)
        self.edit_review_button.first.click()
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        return self

    def click_save_review(self) -> "AppraisalReviewPage":
        """Clicks 'Save' button on Appraisal Review Details and handles any dialog popups."""
        self.logger.info("Appraisal Review Details: Clicking 'Save'")
        self.save_review_button.first.wait_for(state="visible", timeout=15000)
        self.save_review_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        self.logger.info("Appraisal Review Details saved successfully.")
        return self

    def edit_and_save_review_details(self) -> "AppraisalReviewPage":
        """
        Composed workflow: clicks Edit, then Save, verifying clean state.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        return self.click_edit_review().click_save_review()

    def switch_review_tab(self, tab_name: str) -> "AppraisalReviewPage":
        """
        Switches between tabs on the #AppraisalReviewTabs widget using KendoTabStrip.

        Args:
            tab_name (str): Name of the subtab (e.g. 'Status', 'Log').

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        self.logger.info(f"Switching to review tab '{tab_name}' via KendoTabStrip component")
        self._wait_for_loader()
        self.kendo_tabstrip.select_tab(self.appraisal_review_tabs, tab_name)
        self.page.wait_for_timeout(300)
        self._wait_for_loader()
        return self

    # =========================================================================
    # Section: Log Tab Operations
    # =========================================================================

    def navigate_to_log_tab(self) -> "AppraisalReviewPage":
        """
        Navigates to Log tab on #AppraisalReviewTabs, verifies table visibility,
        and checks for zero error alerts.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        self.logger.info("Log Tab: Navigating to Log tab and verifying table display")
        self.switch_review_tab(self.TAB_LOG)
        expect(self.log_container.first.or_(self.log_table_header).first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Log Tab: Verified table displayed cleanly without errors.")
        return self

    def _create_log_entry(self, trigger_button: Locator, subject: str, entry_type: str = "Entry") -> None:
        """
        Encapsulated helper to open log form, enter subject, save, and return to grid.

        Args:
            trigger_button (Locator): Action button (e.g. Add Call Data or Add Notes).
            subject (str): Subject line to enter.
            entry_type (str): Human-readable entry description for logging.
        """
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

    def add_call_data(self, subject: Optional[str] = None) -> "AppraisalReviewPage":
        """
        Adds a Call Data entry with dynamic Faker subject, saves, and returns.

        Args:
            subject (Optional[str]): Custom subject string. Auto-generated if None.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        c_subj = subject or f"Call {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_call_data_button, c_subj, entry_type="Call Data")
        self.verify_no_errors()
        return self

    def add_notes(self, subject: Optional[str] = None) -> "AppraisalReviewPage":
        """
        Adds a Notes entry with dynamic Faker subject, saves, and returns.

        Args:
            subject (Optional[str]): Custom subject string. Auto-generated if None.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        n_subj = subject or f"Note {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self._create_log_entry(self.add_notes_button, n_subj, entry_type="Notes")
        self.verify_no_errors()
        return self

    # =========================================================================
    # Section: Add Attachment Granular & Composed Operations
    # =========================================================================

    def _get_or_create_dummy_file(self) -> str:
        """
        Ensures a valid sample file exists for attachment upload using Config.TESTDATA_DIR.

        Returns:
            str: Absolute path to the dummy sample file.
        """
        testdata_dir = str(Config.TESTDATA_DIR)
        os.makedirs(testdata_dir, exist_ok=True)
        sample_path = os.path.join(testdata_dir, self.DEFAULT_SAMPLE_FILENAME)
        if not os.path.exists(sample_path):
            with open(sample_path, "w") as f:
                f.write("This is a dummy test attachment for NCDOT appraisal review automation.")
        return sample_path

    def open_add_attachment_modal(self) -> "AppraisalReviewPage":
        """Clicks 'Add Attachment' button and waits for container visibility."""
        self.logger.info("Log Tab: Opening 'Add Attachment' modal container")
        attach_btn = self.add_attachment_button.first
        attach_btn.wait_for(state="visible", timeout=15000)
        attach_btn.click()
        self.attachment_container.first.wait_for(state="visible", timeout=15000)
        self._wait_for_loader()
        return self

    def select_attachment_doc_type(self, doc_type: Optional[str] = None) -> "AppraisalReviewPage":
        """Selects Document Type via separated KendoDropdown component (defaults to 1st option)."""
        self.logger.info(f"Log Tab: Selecting Document Type ({doc_type or '1st valid option'})")
        if doc_type:
            self.kendo_dropdown.select_option(self.doc_type_dropdown, doc_type)
        else:
            self.kendo_dropdown.select_first_option(self.doc_type_dropdown)
        self.page.wait_for_timeout(300)
        return self

    def upload_attachment_file(self, file_path: Optional[str] = None) -> str:
        """Uploads file to the Kendo Upload widget."""
        upload_path = file_path or self._get_or_create_dummy_file()
        self.logger.info(f"Log Tab: Setting attachment file '{os.path.basename(upload_path)}'")
        file_inp = self.file_input.first
        file_inp.set_input_files(upload_path)
        self.page.wait_for_timeout(500)
        return upload_path

    def fill_attachment_subject(self, subject: Optional[str] = None) -> str:
        """Fills Subject input on the attachment form."""
        att_subj = subject or f"Att {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self.logger.info(f"Log Tab: Entering attachment subject '{att_subj}'")
        subj_inp = self.attachment_subject_input.first
        subj_inp.wait_for(state="visible", timeout=10000)
        subj_inp.fill(att_subj)
        self.page.wait_for_timeout(300)
        return att_subj

    def save_attachment(self) -> "AppraisalReviewPage":
        """Clicks Save (#SaveDocumentBtn), handles alert dialogs, and returns to log table."""
        self.logger.info("Log Tab: Saving attachment (#SaveDocumentBtn)")
        save_btn = self.attachment_save_button.first
        save_btn.wait_for(state="visible", timeout=15000)
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        expect(self.log_container.first.or_(self.log_table_header).first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        return self

    def add_attachment(
        self,
        file_path: Optional[str] = None,
        subject: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> "AppraisalReviewPage":
        """
        High-level orchestrator: Opens attachment container, selects 1st Document Type
        via KendoDropdown, uploads dummy file, enters dummy Subject, and saves.

        Args:
            file_path (Optional[str]): Path of file to upload (auto-generated if None).
            subject (Optional[str]): Subject line (auto-generated if None).
            doc_type (Optional[str]): Document type name (selects 1st valid if None).

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        self.open_add_attachment_modal()
        self.select_attachment_doc_type(doc_type=doc_type)
        self.upload_attachment_file(file_path=file_path)
        self.fill_attachment_subject(subject=subject)
        self.save_attachment()
        self.logger.info("Attachment uploaded and saved successfully.")
        return self

    # =========================================================================
    # Error Verification
    # =========================================================================

    def verify_no_errors(self) -> "AppraisalReviewPage":
        """
        Verifies that no error alerts or validation messages are present.

        Returns:
            AppraisalReviewPage: Current page instance for fluent chaining.
        """
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self
