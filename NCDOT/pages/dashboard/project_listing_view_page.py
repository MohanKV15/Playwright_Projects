import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.core.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)
fake = Faker()


class ProjectListingViewPage(BasePage):
    """
    Page Object Model representing the NCDOT Project Listing View & Tab Operations:
      - Searches project by Project ID (default '2224761').
      - Opens project information details.
      - Parcels tab: Clicks 'Add New', focuses 'Parcel No *', clicks 'Cancel'.
      - Role Assignment tab: Navigates to tab and verifies display.
      - Task Assignment tab: Navigates to tab and verifies display.
      - Log tab: Adds Call Data & Notes using dynamic Faker data, then closes page.
    """

    DEFAULT_TEST_PROJECT_ID = "2224761"

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Project Listing Search Filters & Grid
        self.project_id_search_input = page.get_by_role("textbox", name="Project ID/TIP").or_(
            page.locator("input#Project_Id, input[name='Project_Id']")
        )
        self.refresh_button = page.get_by_role("button", name=re.compile(r"Refresh", re.I)).or_(
            page.locator("#btnRefresh, button:has-text('Refresh')")
        )
        self.grid_tbody = page.locator("tbody, .k-grid-content tbody")
        self.first_row_link = page.locator("tbody tr").first.locator("a").first.or_(
            page.locator("tbody").get_by_role("link").filter(has_text=re.compile(r"^$")).first
        )

        # 2. Project Information & Tab Display Container
        self.project_info_container = page.locator("#frmPrjView070101, #divProjectDetails").or_(
            page.get_by_text("Project Information Project").first
        )
        self.tabstrip = page.locator("#TabstripProjectDetails")
        self.tab_display_container = page.locator("#divProjectDetailsTabDisplay > #partial-form > section > div > div").or_(
            page.locator("#divProjectDetailsTabDisplay")
        )

        # 3. Parcels Tab Elements
        self.parcel_add_new_button = page.locator("#AddNewParcelBtn01:visible").or_(
            page.locator("#divProjectDetailsTabDisplay button:visible").filter(has_text=re.compile(r"Add New", re.I))
        )
        self.parcel_no_input = page.get_by_role("textbox", name="Parcel No *").or_(
            page.locator("input#Parcel_No:visible, input[name*='Parcel_No']:visible")
        )
        self.parcel_cancel_button = page.locator(
            "#divProjectDetailsTabDisplay button:visible, .k-window:visible button:visible"
        ).filter(has_text=re.compile(r"^\s*Cancel\b", re.I))

        # 4. Log Tab Elements
        self.add_call_data_button = page.locator("#btnAddCallData:visible, button:visible:has-text('Add Call Data')")
        self.add_notes_button = page.locator("#btnAddNotes:visible, button:visible:has-text('Add Notes')")
        self.subject_input = page.get_by_role("textbox", name=re.compile(r"Subject", re.I)).or_(
            page.locator("input#log_subject:visible, input#Subject:visible, input[name*='Subject']:visible")
        )
        self.save_log_button = page.locator("#btnSubmit:visible, button:visible:has-text('Save')")
        self.back_notes_button = page.locator("#btnBacknotes:visible")

    # =========================================================================
    # Step-by-Step Actions
    # =========================================================================

    def login_and_navigate_to_projects(self) -> "ProjectListingViewPage":
        """Authenticates via direct entry URL and prepares project dashboard."""
        from pages.login.login_page import LoginPage
        login_p = LoginPage(self.page)
        login_p.navigate_to_login()
        login_p.login(
            email=Config.DEFAULT_USER,
            password=Config.DEFAULT_PASSWORD,
            pin=Config.DEFAULT_PIN,
        )
        self._wait_for_loader()
        expect(self.project_id_search_input.first).to_be_visible(timeout=35000)
        return self

    def search_project_by_id(self, project_id: str = DEFAULT_TEST_PROJECT_ID) -> "ProjectListingViewPage":
        """Fills Project ID/TIP in the search filter, clicks Refresh, and waits for grid."""
        self.logger.info(f"Filtering Project Listing by Project ID: '{project_id}'")
        self._wait_for_loader()
        self.project_id_search_input.first.click()
        self.project_id_search_input.first.fill(project_id)
        self.refresh_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.grid_tbody.first).to_be_visible(timeout=15000)
        return self

    def open_project_details(self) -> "ProjectListingViewPage":
        """Clicks the project link in the filtered row and verifies project information."""
        self.logger.info("Opening Project Details from search results grid")
        self._wait_for_loader()
        self.first_row_link.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.verify_project_information_visible()
        return self

    def verify_project_information_visible(self, timeout_ms: int = 30000) -> "ProjectListingViewPage":
        """Verifies the Project Information details view is visible."""
        self._wait_for_loader()
        expect(self.project_info_container.first).to_be_visible(timeout=timeout_ms)
        self.logger.info("Project Information container is visible.")
        return self

    # -------------------------------------------------------------------------
    # Tab Navigations & Actions (DRY & Reusable)
    # -------------------------------------------------------------------------

    def switch_to_tab(self, tab_name: str) -> "ProjectListingViewPage":
        """Navigates to specified project details tab and verifies content display."""
        self.logger.info(f"Navigating to tab: '{tab_name}'")
        self._wait_for_loader()
        tab_link = self.tabstrip.locator("span.k-link", has_text=tab_name).or_(
            self.tabstrip.get_by_text(tab_name, exact=True)
        ).first
        tab_link.wait_for(state="visible", timeout=10000)
        tab_link.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.tab_display_container.first).to_be_visible(timeout=15000)
        return self

    def navigate_to_parcels_tab(self) -> "ProjectListingViewPage":
        """Navigates to the Parcels tab."""
        return self.switch_to_tab("Parcels")

    def open_parcels_tab_and_cancel_add_new(self) -> "ProjectListingViewPage":
        """Clicks Parcels tab, clicks 'Add New', focuses 'Parcel No *', then clicks 'Cancel'."""
        self.navigate_to_parcels_tab()

        self.logger.info("Parcels Tab: Clicking 'Add New'")
        self.parcel_add_new_button.first.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        self.logger.info("Parcels Tab: Focusing 'Parcel No *' textbox")
        expect(self.parcel_no_input.first).to_be_visible(timeout=10000)
        self.parcel_no_input.first.click()
        self.page.wait_for_timeout(300)

        self.logger.info("Parcels Tab: Clicking 'Cancel'")
        self.parcel_cancel_button.first.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()
        return self

    def navigate_to_role_assignment_tab(self) -> "ProjectListingViewPage":
        """Navigates to Role Assignment tab and verifies tab content display."""
        return self.switch_to_tab("Role Assignment")

    def navigate_to_task_assignment_tab(self) -> "ProjectListingViewPage":
        """Navigates to Task Assignment tab and verifies tab content display."""
        return self.switch_to_tab("Task Assignment")

    def navigate_to_log_tab(self) -> "ProjectListingViewPage":
        """Navigates to the Log tab and verifies tab content visibility."""
        return self.switch_to_tab("Log")

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

    def close_page(self) -> None:
        """Closes the current browser page."""
        self.logger.info("Closing page after completing operations.")
        try:
            self.page.close()
        except Exception as e:
            self.logger.debug(f"Page close note: {e}")
