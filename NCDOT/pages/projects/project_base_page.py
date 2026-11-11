import logging
import re
from typing import Optional
from playwright.sync_api import Locator, Page, expect
from pages.core.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)


class ProjectBasePage(BasePage):
    """
    ProjectBasePage: Enterprise POM base class for all Project Management workflows.
    Encapsulates shared Project Listing filters, project navigation, tabstrip switching,
    and common Project Details containers.
    """

    DEFAULT_TEST_PROJECT_ID = "2224761"

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Project Listing Search Filters & Table Grid
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

        # 2. Project Information Details Container
        self.project_info_container = page.locator("#frmPrjView070101, #divProjectDetails").or_(
            page.get_by_text("Project Information Project").first
        )

        # 3. Project Details Tabstrip & Container
        self.tabstrip = page.locator("#TabstripProjectDetails")
        self.tab_display_container = page.locator("#divProjectDetailsTabDisplay > #partial-form > section > div > div").or_(
            page.locator("#divProjectDetailsTabDisplay")
        )

        # 4. Parcels Tab Trigger (Shared across Project Views)
        self.add_new_parcel_button = page.locator("#AddNewParcelBtn01:visible").or_(
            page.locator("#divProjectDetailsTabDisplay button:visible").filter(has_text=re.compile(r"Add New", re.I))
        )

    # =========================================================================
    # Shared Navigation & Search Actions
    # =========================================================================

    def login_and_navigate_to_projects(self) -> "ProjectBasePage":
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
        expect(
            self.project_id_search_input.first.or_(
                self.page.get_by_role("button", name=re.compile(r"Add New Project", re.I))
            ).first
        ).to_be_visible(timeout=35000)
        return self

    def search_project_by_id(self, project_id: str = DEFAULT_TEST_PROJECT_ID) -> "ProjectBasePage":
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

    def open_project_details(self) -> "ProjectBasePage":
        """Clicks the project link in the filtered row and verifies project information."""
        self.logger.info("Opening Project Details from search results grid")
        self._wait_for_loader()
        self.first_row_link.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.verify_project_information_visible()
        return self

    def verify_project_information_visible(self, timeout_ms: int = 30000) -> "ProjectBasePage":
        """Verifies the Project Information details view is visible."""
        self._wait_for_loader()
        expect(self.project_info_container.first).to_be_visible(timeout=timeout_ms)
        self.logger.info("Project Information container is visible.")
        return self

    # =========================================================================
    # Tab Navigations (DRY across all Project pages)
    # =========================================================================

    def switch_to_tab(self, tab_name: str) -> "ProjectBasePage":
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

    def navigate_to_parcels_tab(self) -> "ProjectBasePage":
        """Navigates to the Parcels tab."""
        return self.switch_to_tab("Parcels")

    def navigate_to_role_assignment_tab(self) -> "ProjectBasePage":
        """Navigates to Role Assignment tab and verifies tab content display."""
        return self.switch_to_tab("Role Assignment")

    def navigate_to_task_assignment_tab(self) -> "ProjectBasePage":
        """Navigates to Task Assignment tab and verifies tab content display."""
        return self.switch_to_tab("Task Assignment")

    def navigate_to_log_tab(self) -> "ProjectBasePage":
        """Navigates to the Log tab and verifies tab content visibility."""
        return self.switch_to_tab("Log")

