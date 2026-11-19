import logging
import re
from typing import Optional
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)


class WorkflowAssignmentModal:
    """
    Component representing the 'Add/Edit Workflow Assignment' modal dialog.
    Encapsulates modal-specific elements and controls.
    """

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.locator(".k-window:visible, [role='dialog']:visible").filter(
            has_text="Add/Edit Workflow Assignment"
        )
        self.role_dropdown = self.dialog.locator(".k-dropdown").first
        self.staff_dropdown = self.dialog.locator(".k-dropdown").nth(1)
        self.save_button = self.dialog.locator("button#save89:visible, button:visible").filter(
            has_text=re.compile(r"Save", re.I)
        ).first
        self.cancel_button = self.dialog.locator("button#cancel678:visible, button:visible").filter(
            has_text=re.compile(r"Cancel", re.I)
        ).first


class WorkflowAssignmentPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Workflow Assignment workflow:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Selects parcel record from Parcels grid to enter Parcel Central.
      - Navigates to Workflow Assignment sub-menu and opens modal dialog.
      - Selects Role and Staff via enterprise Kendo component handlers.
      - Saves the assignment, gracefully handling duplicate assignment alert popups.
    """

    DEFAULT_ROLE = "A/G Assigned Attorney"
    DEFAULT_STAFF = "A Ravi"

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Parcels Tab Grid Locators
        self.parcels_grid_tbody = page.locator("#divProjectDetailsTabDisplay tbody, .k-grid-content tbody")
        self.parcel_edit_buttons = page.locator(
            "#btnGeneralParcelPrjEdit:visible, a#btnGeneralParcelPrjEdit:visible, button#btnGeneralParcelPrjEdit:visible"
        )

        # 2. Parcel Central Navigation & Containers
        self.workflow_nav_link = page.locator(
            "#navigationMenu, nav, ul, .k-panelbar, body"
        ).get_by_text("Workflow Assignment", exact=True)
        self.workflow_content_container = page.locator("#partialForm #partial-form, #partial-form")
        self.add_new_workflow_button = page.locator(
            "button#AddNewAssignement987:visible, button:visible"
        ).filter(has_text=re.compile(r"Add New", re.I))

        # 3. Modal Dialog Component
        self.modal = WorkflowAssignmentModal(page)

    # Backward compatibility properties for direct locator access
    @property
    def workflow_dialog(self) -> Locator:
        return self.modal.dialog

    @property
    def role_dropdown(self) -> Locator:
        return self.modal.role_dropdown

    @property
    def staff_dropdown(self) -> Locator:
        return self.modal.staff_dropdown

    @property
    def modal_save_button(self) -> Locator:
        return self.modal.save_button

    @property
    def modal_cancel_button(self) -> Locator:
        return self.modal.cancel_button

    # =========================================================================
    # Parcel Central Navigation & Selection
    # =========================================================================

    def open_parcel_in_parcel_central(
        self,
        parcel_identifier: Optional[str] = "111",
        row_index: int = 0,
        timeout_ms: int = 30000,
    ) -> "WorkflowAssignmentPage":
        """
        Selects a parcel record from the Parcels grid and clicks '#btnGeneralParcelPrjEdit'
        to navigate into Parcel Central.
        """
        self.logger.info(f"Opening Parcel in Parcel Central (identifier='{parcel_identifier}', index={row_index})")
        self._wait_for_loader()
        self.parcel_edit_buttons.first.wait_for(state="visible", timeout=timeout_ms)

        if parcel_identifier:
            row = self.page.locator("tbody tr, .k-grid-content tr").filter(
                has_text=re.compile(re.escape(parcel_identifier), re.I)
            )
            if row.count() > 0 and row.first.is_visible():
                row.first.locator(self.parcel_edit_buttons).first.click()
            else:
                self.logger.warning(f"Row matching '{parcel_identifier}' not found. Selecting index {row_index}.")
                self.parcel_edit_buttons.nth(row_index).click()
        else:
            self.parcel_edit_buttons.nth(row_index).click()

        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.kendo_dropdown.wait_for_cascading(index=4, timeout_ms=15000)
        self._wait_for_loader()
        return self

    def navigate_to_workflow_assignment(self) -> "WorkflowAssignmentPage":
        """Clicks 'Workflow Assignment' in Parcel Central left navigation and verifies view."""
        self.logger.info("Navigating to Workflow Assignment sub-menu")
        self._wait_for_loader()
        self.workflow_nav_link.first.wait_for(state="visible", timeout=15000)
        self.workflow_nav_link.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.workflow_content_container.first).to_be_visible(timeout=15000)
        expect(self.add_new_workflow_button.first).to_be_visible(timeout=15000)
        return self

    # =========================================================================
    # Workflow Assignment Modal Operations
    # =========================================================================

    def open_add_new_workflow_modal(self) -> "WorkflowAssignmentPage":
        """Clicks '+ Add New' button and verifies modal dialog is displayed."""
        self.logger.info("Opening Add New Workflow Assignment modal")
        self.add_new_workflow_button.first.wait_for(state="visible", timeout=10000)
        self.add_new_workflow_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.modal.dialog.first).to_be_visible(timeout=15000)
        return self

    def select_role(self, role_name: Optional[str] = DEFAULT_ROLE) -> "WorkflowAssignmentPage":
        """Selects Role in dropdown using KendoDropdown component (by name or 1st option)."""
        self.logger.info(f"Workflow Assignment: Selecting Role '{role_name or '1st available'}'")
        self.kendo_dropdown.select_option(self.modal.role_dropdown, role_name)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        return self

    def select_staff_type(self, staff_type: str = "Internal Staff of this Role Type") -> "WorkflowAssignmentPage":
        """Selects radio button for Staff Type."""
        self.logger.info(f"Workflow Assignment: Selecting Staff Type '{staff_type}'")
        radio = self.modal.dialog.get_by_label(staff_type).or_(
            self.modal.dialog.locator(f"input[type='radio'][value*='{staff_type}']")
        ).first
        if radio.is_visible(timeout=3000):
            radio.check(force=True)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()
        return self

    def select_staff(self, staff_name: Optional[str] = DEFAULT_STAFF) -> "WorkflowAssignmentPage":
        """Selects Staff in dropdown using KendoDropdown component (by name or 1st option)."""
        self.logger.info(f"Workflow Assignment: Selecting Staff '{staff_name or '1st available'}'")
        self.kendo_dropdown.select_option(self.modal.staff_dropdown, staff_name)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        return self

    def save_workflow_assignment(self) -> "WorkflowAssignmentPage":
        """
        Saves assignment and delegates duplicate alert/window handling to KendoDialog.
        """
        self.logger.info("Workflow Assignment: Clicking Save (#save89)")
        self.modal.save_button.wait_for(state="visible", timeout=10000)
        self.modal.save_button.click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Handle duplicate assignment alert if present, then dismiss window cleanly
        if self.kendo_dialog.handle_alert(pattern=r"already exist|already saved|saved already|Alert", button_text="OK"):
            self.kendo_dialog.close_window(window_title="Add/Edit Workflow Assignment")

        self._wait_for_loader()
        expect(self.modal.dialog).to_have_count(0, timeout=15000)
        self.logger.info("Workflow Assignment successfully saved/acknowledged and closed.")
        return self

    def add_workflow_assignment(
        self,
        role_name: Optional[str] = DEFAULT_ROLE,
        staff_type: Optional[str] = "Internal Staff of this Role Type",
        staff_name: Optional[str] = DEFAULT_STAFF,
    ) -> "WorkflowAssignmentPage":
        """
        Executes complete modal workflow:
          1. Opens modal.
          2. Selects Role.
          3. Selects Staff Type (if specified).
          4. Selects Staff.
          5. Saves assignment.
        """
        return (
            self.open_add_new_workflow_modal()
            .select_role(role_name=role_name)
            .select_staff_type(staff_type=staff_type)
            .select_staff(staff_name=staff_name)
            .save_workflow_assignment()
        )
