import logging
import re
from typing import Optional
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)


class TaskAssignmentPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Task Assignment workflow:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Selects parcel record from Parcels grid to enter Parcel Central.
      - Navigates to Task Assignment sub-menu in left sidebar.
      - Selects the 1st record (or specified record) in the Task Assignment table.
      - Clicks 'Edit', then 'Save'.
      - Verifies changes are saved without error.
      - Clicks 'Back' to return to the task assignment list.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Content Containers
        self.task_assignment_nav_link = page.locator(
            "#navigationMenu, nav, ul, .k-panelbar, body"
        ).get_by_text("Task Assignment", exact=True)

        self.task_content_container = page.locator("#partialForm #partial-form, #partial-form")

        # 2. Task Assignment Grid & Action Elements
        self.task_rows = page.locator("tbody tr, .k-grid-content tr")
        self.task_assign_edit_buttons = page.locator(
            "#btnTaskAssignEdit:visible, a#btnTaskAssignEdit:visible, button#btnTaskAssignEdit:visible"
        )

        # 3. Form Action Buttons & Detail Containers
        self.edit_button = page.get_by_role("button", name=re.compile(r"^\s*Edit\s*$", re.I)).or_(
            page.locator("button#btnEdit:visible, button:visible:has-text('Edit')")
        )

        self.save_button = page.get_by_role("button", name=re.compile(r"^\s*Save\s*$", re.I)).or_(
            page.locator("button#btnSave:visible, button:visible:has-text('Save')")
        )

        self.task_details_view_container = page.locator("#partial-form").nth(1).or_(
            page.locator("#partialForm #partial-form, #partial-form")
        )

        self.back_button = page.get_by_role("button", name=re.compile(r"^\s*Back\s*$", re.I)).or_(
            page.locator("button#btnBack:visible, button:visible:has-text('Back')")
        )

        self.error_alerts = page.locator(".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible")

    # =========================================================================
    # Task Assignment Navigation
    # =========================================================================

    def navigate_to_task_assignment(self) -> "TaskAssignmentPage":
        """Clicks 'Task Assignment' in Parcel Central left navigation and verifies view container."""
        self.logger.info("Navigating to Task Assignment sub-menu")
        self._wait_for_loader()
        self.task_assignment_nav_link.first.wait_for(state="visible", timeout=15000)
        self.task_assignment_nav_link.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.task_content_container.first).to_be_visible(timeout=15000)
        return self

    # =========================================================================
    # Task Assignment Table Operations
    # =========================================================================

    def select_task_record(
        self,
        row_index: int = 0,
        record_name: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> "TaskAssignmentPage":
        """
        Selects a task record from the grid. If record_name is provided, matches by row name;
        otherwise selects the 1st available record (row_index=0) and clicks '#btnTaskAssignEdit'.
        """
        self.logger.info(f"Selecting Task Record (name='{record_name}', index={row_index})")
        self._wait_for_loader()
        self.task_assign_edit_buttons.first.wait_for(state="visible", timeout=timeout_ms)

        if record_name:
            target_row = self.page.locator("tbody tr, .k-grid-content tr").filter(
                has_text=re.compile(re.escape(record_name), re.I)
            )
            if target_row.count() > 0 and target_row.first.is_visible():
                target_row.first.locator(
                    "#btnTaskAssignEdit:visible, a#btnTaskAssignEdit:visible, button#btnTaskAssignEdit:visible"
                ).first.click()
            else:
                self.logger.warning(f"Row '{record_name}' not found. Selecting index {row_index}.")
                self.task_assign_edit_buttons.nth(row_index).click()
        else:
            self.task_assign_edit_buttons.nth(row_index).click()

        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        return self

    def click_edit(self) -> "TaskAssignmentPage":
        """Clicks 'Edit' button on task details form."""
        self.logger.info("Task Assignment Details: Clicking 'Edit'")
        self.edit_button.first.wait_for(state="visible", timeout=10000)
        self.edit_button.first.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()
        return self

    def click_save(self) -> "TaskAssignmentPage":
        """Clicks 'Save' button and verifies details view is displayed without errors."""
        self.logger.info("Task Assignment Details: Clicking 'Save'")
        self.save_button.first.wait_for(state="visible", timeout=10000)
        self.save_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Handle any alert if present
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success", button_text="OK")
        self._wait_for_loader()

        expect(self.task_details_view_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Task Assignment successfully saved without errors.")
        return self

    def click_back(self) -> "TaskAssignmentPage":
        """Clicks 'Back' button to return to the task assignment table."""
        self.logger.info("Task Assignment Details: Clicking 'Back'")
        self.back_button.first.wait_for(state="visible", timeout=10000)
        self.back_button.first.click()
        self.page.wait_for_timeout(800)
        self._wait_for_loader()
        expect(self.task_content_container.first).to_be_visible(timeout=15000)
        self.logger.info("Returned to Task Assignment listing successfully.")
        return self

    def verify_no_errors(self) -> "TaskAssignmentPage":
        """Verifies that no danger alerts or validation error messages are displayed."""
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self

    def edit_and_save_task(
        self,
        row_index: int = 0,
        record_name: Optional[str] = None,
    ) -> "TaskAssignmentPage":
        """
        Executes complete edit-and-save flow:
          1. Selects task record (1st record by default).
          2. Clicks Edit.
          3. Clicks Save.
          4. Verifies no error.
          5. Clicks Back.
        """
        return (
            self.select_task_record(row_index=row_index, record_name=record_name)
            .click_edit()
            .click_save()
            .click_back()
        )

