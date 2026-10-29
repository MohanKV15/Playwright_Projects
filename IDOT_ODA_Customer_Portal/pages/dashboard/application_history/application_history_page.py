import logging
import re
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class ApplicationHistoryPage(BasePage):
    """
    Page Object Model representing the Customer Portal: Application History workflow.

    Encapsulates:
    - Navigation from Dashboard to Application History
    - Verification of Application History instructions and #AppHistoryTable
    - Dynamic application search using the 1st record row in the table
    - Exporting application history with dedicated downloads directory management
      (cleans older files so only the latest download is retained)
    - Toggling 'Include Inactive' filter checkbox and executing searches
    - Returning back to the Dashboard via 'Back'
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Header Locators
        self.app_history_dashboard_card = page.get_by_text(
            "Application History View your", exact=False
        ).first
        self.view_submitted_apps_btn = page.locator("#btnViewSubmittedApps")
        self.instructions_banner = page.get_by_text(
            "Applications History Instructions: Click on the application # to review the",
            exact=False,
        ).first

        # 2. Grid Table Locator
        self.app_history_table = page.locator("#AppHistoryTable")

        # 3. Search & Filter Locators
        self.search_input = (
            page.get_by_role(
                "textbox", name=re.compile(r"Search for your application", re.I)
            )
            .or_(page.locator("#search, input[placeholder*='Search']"))
            .first
        )
        self.search_button = (
            page.get_by_role("button", name=re.compile(r"Search", re.I))
            .or_(page.locator("#btnSearch, button:has-text('Search')"))
            .first
        )
        self.include_inactive_checkbox = (
            page.get_by_text("Include Inactive", exact=False)
            .or_(
                page.locator(
                    "label:has-text('Include Inactive'), .k-checkbox-label:has-text('Include Inactive')"
                )
            )
            .first
        )

        # 4. Action Buttons
        self.export_button = (
            page.get_by_role("button", name=re.compile(r"Export", re.I))
            .or_(page.locator("#btnExport, button:has-text('Export')"))
            .first
        )
        self.back_button = (
            page.get_by_role("button", name=re.compile(r"Back", re.I))
            .or_(page.locator("#btnBack, button:has-text('Back')"))
            .first
        )
        self.dashboard_marker = (
            page.locator("#btnSubmitApp")
            .or_(page.get_by_text("Submit an Application"))
            .first
        )

        # Dedicated Downloads Directory
        self.downloads_dir: Path = Config.DOWNLOADS_DIR

    # -----------------------------------------------------------------
    # Navigation & Verification Methods
    # -----------------------------------------------------------------
    def navigate_to_application_history(self) -> "ApplicationHistoryPage":
        """Navigates from Dashboard to Application History page."""
        self.logger.info("Navigating to Application History page")
        self._wait_for_loader(timeout=30000)

        if "CALanding" in self.page.url or "Account" in self.page.url:
            try:
                self.page.wait_for_url(
                    re.compile(r"CADashboardFull|4321CustomerPortalDashboardFull"),
                    timeout=20000,
                )
            except Exception:
                self.page.goto(
                    f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull",
                    wait_until="domcontentloaded",
                )

        self._wait_for_loader(timeout=30000)

        if self.instructions_banner.is_visible() and self.app_history_table.is_visible():
            return self

        expect(self.app_history_dashboard_card).to_be_visible(timeout=30000)
        expect(self.view_submitted_apps_btn).to_be_visible(timeout=30000)
        self.view_submitted_apps_btn.click()
        self._wait_for_loader(timeout=30000)

        self.verify_application_history_page()
        self.logger.info("Successfully navigated to Application History page")
        return self

    def verify_application_history_page(self, timeout_ms: int = 15000) -> "ApplicationHistoryPage":
        """Asserts visibility of instructions banner and #AppHistoryTable grid."""
        self.logger.info("Verifying Application History instructions and #AppHistoryTable")
        expect(self.instructions_banner).to_be_visible(timeout=timeout_ms)
        expect(self.app_history_table).to_be_visible(timeout=timeout_ms)
        return self

    # -----------------------------------------------------------------
    # Search & Filter Methods (Always uses 1st record)
    # -----------------------------------------------------------------
    def get_first_record_application_number(self) -> str:
        """
        Dynamically extracts the application identifier from the 1st record row in #AppHistoryTable.
        Guarantees searching by the actual 1st record in the grid.
        """
        app_id = self.get_grid_first_record_identifier(
            self.app_history_table,
            pattern=r"\b\d{3}-\d+\b",
        )
        self.logger.info(f"Retrieved 1st record application identifier: '{app_id}'")
        return app_id

    def search_application(self, application_no: Optional[str] = None) -> "ApplicationHistoryPage":
        """
        Searches for an application using the search input.
        If application_no is not provided, automatically uses the 1st record in the table.
        """
        target_app_no = application_no or self.get_first_record_application_number()
        self.logger.info(f"Searching for application: '{target_app_no}'")
        self.search_input.scroll_into_view_if_needed()
        self.search_input.click()
        self.search_input.fill(target_app_no)
        self.click_search()
        return self

    def clear_search(self) -> "ApplicationHistoryPage":
        """Clears the search textbox value."""
        self.logger.info("Clearing search input")
        self.search_input.scroll_into_view_if_needed()
        self.search_input.click()
        self.search_input.fill("")
        return self

    def click_search(self) -> "ApplicationHistoryPage":
        """Clicks the 'Search' button using KendoButton and waits for grid update."""
        self.logger.info("Clicking 'Search' button")
        self.click_kendo_button(self.search_button)
        self._wait_for_loader()
        return self

    def toggle_include_inactive(self) -> "ApplicationHistoryPage":
        """Toggles the 'Include Inactive' filter checkbox."""
        self.logger.info("Toggling 'Include Inactive' filter checkbox")
        self.include_inactive_checkbox.scroll_into_view_if_needed()
        try:
            self.include_inactive_checkbox.click()
        except Exception:
            self.check_kendo_checkbox(self.include_inactive_checkbox)
        self._wait_for_loader()
        return self

    # -----------------------------------------------------------------
    # Export & Downloads Management (Ensures single latest file)
    # -----------------------------------------------------------------
    def export_applications(self, timeout_ms: int = 30000) -> Path:
        """
        Triggers 'Export', cleans the download directory beforehand,
        and saves the latest exported file into the downloads folder.
        Returns the saved file Path and verifies it exists and is not empty.
        """
        self.logger.info("Exporting applications history to downloads folder")
        return self.download_export_file(
            self.export_button,
            default_filename="ApplicationsHistoryExport.xlsx",
            timeout_ms=timeout_ms,
        )

    # -----------------------------------------------------------------
    # Back to Dashboard
    # -----------------------------------------------------------------
    def click_back(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Back' button and verifies navigation back to the Dashboard."""
        self.logger.info("Clicking 'Back' button to return to Dashboard")
        self.back_button.scroll_into_view_if_needed()
        self.click_kendo_button(self.back_button)
        self._wait_for_loader()

        expect(self.dashboard_marker).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Successfully returned to Dashboard. Current URL: {self.page.url}")

    # -----------------------------------------------------------------
    # Full End-to-End Workflow Orchestration
    # -----------------------------------------------------------------
    def complete_application_history_workflow(self) -> Path:
        """
        Executes full Application History workflow matching recorded user codegen:
        1. Navigates to Application History
        2. Searches by 1st record application number
        3. Clears search input
        4. Exports history and saves latest file to downloads folder
        5. Clicks Search
        6. Toggles 'Include Inactive' & Searches
        7. Toggles 'Include Inactive' & Searches
        8. Clicks 'Back' and returns to Dashboard
        """
        self.navigate_to_application_history()
        self.search_application()
        self.clear_search()
        downloaded_file = self.export_applications()
        self.click_search()
        self.toggle_include_inactive()
        self.click_search()
        self.toggle_include_inactive()
        self.click_search()
        self.click_back()
        return downloaded_file

