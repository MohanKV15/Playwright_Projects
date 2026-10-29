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
    - Exporting application history to dedicated downloads directory (latest file retained)
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
        self.search_input = page.get_by_role(
            "textbox", name=re.compile(r"Search for your application", re.I)
        )
        self.search_button = page.get_by_role("button", name=re.compile(r"Search", re.I))
        self.include_inactive_checkbox = page.get_by_text("Include Inactive", exact=False)

        # 4. Action Buttons
        self.export_button = page.get_by_role("button", name=re.compile(r"Export", re.I))
        self.back_button = page.get_by_role("button", name=re.compile(r"Back", re.I))
        self.dashboard_marker = page.locator("#btnSubmitApp")

    # -----------------------------------------------------------------
    # Navigation & Verification Methods
    # -----------------------------------------------------------------
    def navigate_to_application_history(self) -> "ApplicationHistoryPage":
        """Navigates from Dashboard to Application History page."""
        self.logger.info("Navigating to Application History page")
        self._wait_for_loader()

        if self.instructions_banner.is_visible() and self.app_history_table.is_visible():
            return self

        expect(self.app_history_dashboard_card).to_be_visible(timeout=30000)
        self.view_submitted_apps_btn.click()
        self._wait_for_loader()

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
        self.search_input.fill(target_app_no)
        self.click_search()
        return self

    def clear_search(self) -> "ApplicationHistoryPage":
        """Clears the search textbox value."""
        self.logger.info("Clearing search input")
        self.search_input.fill("")
        return self

    def click_search(self) -> "ApplicationHistoryPage":
        """Clicks the 'Search' button and waits for grid update."""
        self.logger.info("Clicking 'Search' button")
        self.search_button.click()
        self._wait_for_loader()
        return self

    def toggle_include_inactive(self) -> "ApplicationHistoryPage":
        """Toggles the 'Include Inactive' filter checkbox."""
        self.logger.info("Toggling 'Include Inactive' filter checkbox")
        self.include_inactive_checkbox.click()
        self._wait_for_loader()
        return self

    # -----------------------------------------------------------------
    # Export & Downloads Management (Ensures latest AppHistory file)
    # -----------------------------------------------------------------
    def export_applications(self, timeout_ms: int = 30000) -> Path:
        """
        Triggers 'Export', cleans previous application history exports,
        and saves the latest exported file into the downloads folder.
        """
        self.logger.info("Exporting applications history to downloads folder")
        return self.download_export_file(
            self.export_button,
            default_filename="AppHistory_Details.csv",
            clean_pattern="AppHistory*",
            timeout_ms=timeout_ms,
        )

    # -----------------------------------------------------------------
    # Back to Dashboard
    # -----------------------------------------------------------------
    def click_back(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Back' button and verifies navigation back to the Dashboard."""
        self.logger.info("Clicking 'Back' button to return to Dashboard")
        self.back_button.click()
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
