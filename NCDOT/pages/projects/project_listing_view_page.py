import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker()


class ProjectListingViewPage(ProjectBasePage):
    """
    Page Object Model representing the NCDOT Project Listing View & Tab Operations:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Parcels tab: Clicks 'Add New', focuses 'Parcel No *', clicks 'Cancel'.
      - Role & Task Assignment tabs: Navigates to tabs and verifies display.
      - Log tab: Adds Call Data & Notes using dynamic Faker data, then closes page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Parcels Tab Form Elements
        self.parcel_no_input = page.locator(
            "input#tract_no:visible, input#Parcel_No:visible, input[name*='Parcel_No']:visible"
        ).or_(page.get_by_role("textbox", name="Parcel No *"))

        self.parcel_cancel_button = page.locator(
            "#divProjectDetailsTabDisplay button:visible, .k-window:visible button:visible, #btnBack:visible, button:visible"
        ).filter(has_text=re.compile(r"^\s*Cancel\b", re.I)).first

        # Log Tab Elements
        self.add_call_data_button = page.locator("#btnAddCallData:visible, button:visible:has-text('Add Call Data')")
        self.add_notes_button = page.locator("#btnAddNotes:visible, button:visible:has-text('Add Notes')")
        self.subject_input = page.get_by_role("textbox", name=re.compile(r"Subject", re.I)).or_(
            page.locator("input#log_subject:visible, input#Subject:visible, input[name*='Subject']:visible")
        )
        self.save_log_button = page.locator("#btnSubmit:visible, button:visible:has-text('Save')")
        self.back_notes_button = page.locator("#btnBacknotes:visible")

    # =========================================================================
    # Page-Specific Tab Workflows
    # =========================================================================

    def open_parcels_tab_and_cancel_add_new(self) -> "ProjectListingViewPage":
        """Clicks Parcels tab, clicks 'Add New', focuses 'Parcel No *', then clicks 'Cancel'."""
        self.navigate_to_parcels_tab()

        self.logger.info("Parcels Tab: Clicking 'Add New'")
        self.add_new_parcel_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_parcel_button.first.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        self.logger.info("Parcels Tab: Focusing 'Parcel No *' textbox")
        expect(self.parcel_no_input.first).to_be_visible(timeout=15000)
        self.parcel_no_input.first.click()
        self.page.wait_for_timeout(300)

        self.logger.info("Parcels Tab: Clicking 'Cancel'")
        self.parcel_cancel_button.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()
        return self

    def _create_log_entry(self, add_button: Locator, subject: str, entry_type: str = "Entry") -> None:
        """Helper to create a log entry, save, and return back to log table."""
        self.logger.info(f"Log Tab: Creating {entry_type} with subject '{subject}'")
        add_button.first.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()
        self.subject_input.first.click()
        self.subject_input.first.fill(subject)
        self.save_log_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        self.logger.info("Log Tab: Returning to log list via Back button")
        self.back_notes_button.first.wait_for(state="visible", timeout=15000)
        self.back_notes_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

    def open_log_tab_and_add_call_data_and_notes(
        self,
        call_data_subject: Optional[str] = None,
        notes_subject: Optional[str] = None,
        close_page_when_done: bool = True,
    ) -> "ProjectListingViewPage":
        """
        Clicks Log tab, adds Call Data & Notes using dynamic Faker data,
        navigates back to log table, and closes the page once complete.
        """
        self.navigate_to_log_tab()

        call_subj = call_data_subject or f"Call {fake.word().capitalize()} {fake.random_int(100, 999)}"
        notes_subj = notes_subject or f"Note {fake.word().capitalize()} {fake.random_int(100, 999)}"

        self._create_log_entry(self.add_call_data_button, call_subj, entry_type="Call Data")
        self._create_log_entry(self.add_notes_button, notes_subj, entry_type="Notes")

        if close_page_when_done:
            self.close_page()

        return self

