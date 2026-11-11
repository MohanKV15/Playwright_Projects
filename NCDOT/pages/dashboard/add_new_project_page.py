import logging
import re
from typing import Optional
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)


class AddNewProjectPage(BasePage):
    """
    Page Object Model representing the NCDOT Right of Way (ROW)
    Project Creation and Configuration workflow.

    Enforces corporate rules:
      - Always selects 1st available dropdown option.
      - Always selects present day date for datepickers.
      - Strictly maintains format 'ABC12.1.ADE' for WBS.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Project Listing & Filter
        self.project_filter_container = page.locator("#partial-form").filter(
            has_text="Project Division"
        ).or_(page.get_by_text("Project Division --Select Project Division--"))
        self.add_new_project_button = page.get_by_role("button", name=re.compile(r"Add New Project", re.I))

        # 2. 'Add New Project' Modal
        self.project_id_input = page.get_by_role("textbox", name="Project ID/TIP *")
        self.project_division_dropdown = page.get_by_label("Add New Project").get_by_text("--Select Project Division--").or_(
            page.locator(".k-window:visible .k-dropdown").first
        )
        self.letting_type_dropdown = page.get_by_label("Add New Project").get_by_text("--Select Letting Type--").or_(
            page.locator(".k-window:visible .k-dropdown").nth(1)
        )
        self.letting_date_button = page.locator(".k-window:visible .k-datepicker .k-select")
        self.letting_date_input = page.locator(".k-window:visible input#PRLetDt")
        self.modal_save_button = page.locator(".k-window:visible").get_by_role("button", name=re.compile(r"Save", re.I))

        # 3. Project Information Details (#frmPrjView070101)
        self.project_info_container = page.locator("#frmPrjView070101, #divProjectDetails")
        self.edit_button = page.get_by_role("button", name=re.compile(r"Edit", re.I))
        self.stip_dropdown = page.locator("#frmPrjView070101").get_by_text("--Select STIP/NON-STIP--").or_(
            page.locator("#frmPrjView070101 .k-dropdown").first
        )
        self.acquisition_type_dropdown = page.locator("#frmPrjView070101").get_by_text("--Select Acquisition Type--").or_(
            page.locator("#frmPrjView070101 .k-dropdown").nth(1)
        )
        self.edit_save_button = page.locator("#frmPrjView070101").get_by_role("button", name=re.compile(r"Save", re.I))

        # 4. WBS Grid & Modal
        self.kendo_grid_content = page.locator(".k-grid-content")
        self.add_new_wbs_button = page.get_by_role("button", name=re.compile(r"Add New", re.I))
        self.wbs_dialog = page.get_by_role("dialog", name="Add/Modify WBS").or_(
            page.locator(".k-window:visible").filter(has_text="Add/Modify WBS")
        )
        self.wbs_input = page.get_by_role("textbox", name="WBS *")
        self.wbs_division_dropdown = page.locator("#div_projectCRUD_WBSClone").get_by_text("--Select Division--").or_(
            page.locator("#div_projectCRUD_WBSClone .k-dropdown").first
        )
        self.wbs_county_dropdown = page.locator("#div_projectCRUD_WBSClone").get_by_text("--Select County--").or_(
            page.locator("#div_projectCRUD_WBSClone .k-dropdown").nth(1)
        ).or_(page.get_by_role("listbox").nth(5))
        self.wbs_save_button = page.locator("#div_projectCRUD_WBSClone, .k-window:visible").get_by_role(
            "button", name=re.compile(r"Save", re.I)
        )

        # 5. Project Details Tabs & Parcels
        self.tabstrip = page.locator("#TabstripProjectDetails")
        self.tab_display_container = page.locator("#divProjectDetailsTabDisplay > #partial-form > section > div > div").or_(
            page.locator("#divProjectDetailsTabDisplay")
        )
        self.parcels_tab = self.tabstrip.get_by_text("Parcels")
        self.add_new_parcel_button = page.get_by_role("button", name=re.compile(r"Add New", re.I))
        self.parcel_no_input = page.get_by_role("textbox", name="Parcel No *")
        self.property_tax_id_input = page.get_by_role("textbox", name="Property Tax ID *")
        self.deed_book_page_input = page.get_by_role("textbox", name="Deed Book/Page *")
        self.parcel_save_button = page.get_by_role("button", name=re.compile(r"Save", re.I))

        # 6. Role & Task Assignment & Log Tabs
        self.role_assignment_tab = self.tabstrip.get_by_text("Role Assignment")
        self.task_assignment_tab = self.tabstrip.get_by_text("Task Assignment")
        self.log_tab = self.tabstrip.get_by_text("Log")

    # =========================================================================
    # Step-by-Step Workflow Actions
    # =========================================================================

    def login_and_navigate_to_projects(self) -> "AddNewProjectPage":
        """Authenticates via direct entry URL and prepares project dashboard."""
        from pages.login.login_page import LoginPage
        login_p = LoginPage(self.page)
        login_p.navigate_to_login()
        login_p.login(
            email=Config.DEFAULT_USER,
            password=Config.DEFAULT_PASSWORD,
            pin=Config.DEFAULT_PIN,
        )
        self.verify_project_filters_visible()
        return self

    def verify_project_filters_visible(self, timeout_ms: int = 35000) -> "AddNewProjectPage":
        """Waits for page load and table's '+ Add New Project' button visibility."""
        self._wait_for_loader()
        expect(self.add_new_project_button.first).to_be_visible(timeout=timeout_ms)
        return self

    def open_add_new_project_modal(self) -> "AddNewProjectPage":
        """Clicks '+ Add New Project' to open modal dialog."""
        self._wait_for_loader()
        self.add_new_project_button.first.click()
        self._wait_for_loader()
        expect(self.project_id_input.first).to_be_visible(timeout=10000)
        return self

    def fill_and_save_new_project(self, project_id: str) -> "AddNewProjectPage":
        """Fills 'Add New Project' modal with 1st options & present day date."""
        self.project_id_input.first.click()
        self.project_id_input.first.fill(project_id)
        self.kendo_dropdown.select_first_option(self.project_division_dropdown.first)
        self.kendo_dropdown.select_first_option(self.letting_type_dropdown.first)
        self.kendo_datepicker.select_present_day(
            trigger_locator=self.letting_date_button.first,
            input_target=self.letting_date_input.first,
        )
        self.modal_save_button.first.click()
        self._wait_for_loader()
        return self

    def verify_project_information_visible(self, timeout_ms: int = 30000) -> "AddNewProjectPage":
        """Asserts visibility of Project Information details container."""
        self._wait_for_loader()
        expect(self.project_info_container.first).to_be_visible(timeout=timeout_ms)
        return self

    def edit_project_information(self) -> "AddNewProjectPage":
        """Clicks Edit and selects 1st option for STIP and Acquisition Type."""
        self.edit_button.first.click()
        self._wait_for_loader()
        self.kendo_dropdown.select_first_option(self.stip_dropdown.first)
        self.kendo_dropdown.select_first_option(self.acquisition_type_dropdown.first)
        self.edit_save_button.first.click()
        self._wait_for_loader()
        return self

    def add_wbs(self, wbs_code: str = "ABC12.1.ADE") -> "AddNewProjectPage":
        """Adds WBS code using strict format pattern and 1st dropdown options."""
        expect(self.kendo_grid_content.first).to_be_visible(timeout=15000)
        self.add_new_wbs_button.first.click()
        self._wait_for_loader()
        expect(self.wbs_dialog.first).to_be_visible(timeout=10000)

        self.wbs_input.first.click()
        self.wbs_input.first.fill(wbs_code)
        self.kendo_dropdown.select_first_option(self.wbs_division_dropdown.first)
        self.kendo_dropdown.select_first_option(self.wbs_county_dropdown.first)
        self.wbs_save_button.first.click()
        self._wait_for_loader()
        return self

    def navigate_to_parcels_tab(self) -> "AddNewProjectPage":
        """Navigates to the Parcels tab and verifies container."""
        self._wait_for_loader()
        self.page.locator("#TabstripProjectDetails span.k-link", has_text="Parcels").click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.tab_display_container.first).to_be_visible(timeout=15000)
        return self

    def add_parcel(
        self,
        parcel_no: str = "1234",
        property_tax_id: str = "2344",
        deed_book_page: str = "test12",
    ) -> "AddNewProjectPage":
        """Adds a new Parcel record."""
        self.add_new_parcel_button.first.click()
        self._wait_for_loader()
        self.parcel_no_input.first.click()
        self.parcel_no_input.first.fill(parcel_no)
        self.property_tax_id_input.first.click()
        self.property_tax_id_input.first.fill(property_tax_id)
        self.deed_book_page_input.first.click()
        self.deed_book_page_input.first.fill(deed_book_page)
        self.parcel_save_button.first.click()
        self._wait_for_loader()
        return self

    def navigate_to_role_assignment_tab(self) -> "AddNewProjectPage":
        """Navigates to Role Assignment tab and verifies display."""
        self._wait_for_loader()
        self.page.locator("#TabstripProjectDetails span.k-link", has_text="Role Assignment").click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.tab_display_container.first).to_be_visible(timeout=15000)
        return self

    def navigate_to_task_assignment_tab(self) -> "AddNewProjectPage":
        """Navigates to Task Assignment tab and verifies tab content display."""
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)
        self.page.locator("#TabstripProjectDetails span.k-link", has_text="Task Assignment").click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.tab_display_container.first).to_be_visible(timeout=15000)
        return self

    def navigate_to_log_tab(self) -> "AddNewProjectPage":
        """Navigates to the Log tab and verifies tab content visibility."""
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)
        self.page.locator("#TabstripProjectDetails span.k-link", has_text="Log").click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.tab_display_container.first).to_be_visible(timeout=15000)
        return self
