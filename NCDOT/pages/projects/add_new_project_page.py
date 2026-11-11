import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker("en_US")


class AddNewProjectPage(ProjectBasePage):
    """
    Page Object Model representing the NCDOT Right of Way (ROW)
    Project Creation and Configuration workflow.

    Enforces corporate rules:
      - Dynamic data generation via Faker.
      - Always selects 1st available dropdown option.
      - Always selects present day date for datepickers.
      - Strictly maintains format 'ABC12.1.ADE' for WBS.
      - Sequential WBS -> Division -> cascading County selection with waits.
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
        self.project_division_dropdown = page.locator(".k-window:visible .k-dropdown").first
        self.letting_type_dropdown = page.locator(".k-window:visible .k-dropdown").nth(1)
        self.letting_date_button = page.locator(".k-window:visible .k-datepicker .k-select")
        self.letting_date_input = page.locator(".k-window:visible input#PRLetDt")
        self.modal_save_button = page.locator(".k-window:visible").get_by_role("button", name=re.compile(r"Save", re.I))

        # 3. Project Information Details (#frmPrjView070101)
        self.edit_button = page.get_by_role("button", name=re.compile(r"Edit", re.I))
        self.stip_dropdown = page.locator("#frmPrjView070101 .k-dropdown").first
        self.acquisition_type_dropdown = page.locator("#frmPrjView070101 .k-dropdown").nth(1)
        self.edit_save_button = page.locator("#frmPrjView070101").get_by_role("button", name=re.compile(r"Save", re.I))

        # 4. WBS Grid & Modal
        self.kendo_grid_content = page.locator(".k-grid-content")
        self.add_new_wbs_button = page.locator("#AddNewWbs-btn:visible")
        self.wbs_dialog = page.locator("#AddNewWBSWindow, .k-window:visible").filter(has_text="Add/Modify WBS")
        self.wbs_input = page.locator("#WBS:visible, input#WBS:visible")
        self.wbs_fa_input = page.locator("#FA_Project_No:visible, input#FA_Project_No:visible")
        self.wbs_division_dropdown = page.locator("#AddNewWBSWindow span[aria-owns='Division_ids_listbox'], #AddNewWBSWindow .k-dropdown").first
        self.wbs_county_multiselect = page.locator("#AddNewWBSWindow .k-multiselect-wrap, #AddNewWBSWindow .k-multiselect").first
        self.wbs_desc_input = page.locator("#WBS_Description:visible, textarea#WBS_Description:visible")
        self.wbs_save_button = page.locator("#PrjWbsSaveBtn:visible, button#PrjWbsSaveBtn").first

        # 5. Parcel Elements for newly created project
        self.parcel_no_input = page.locator(
            "input#tract_no:visible, input#Parcel_No:visible, input[name*='Parcel_No']:visible"
        ).or_(page.get_by_role("textbox", name="Parcel No *"))
        self.property_tax_id_input = page.locator("input#rwr_parcelid:visible, input#Property_Tax_Id:visible, input[name*='Tax_Id']:visible").or_(
            page.get_by_role("textbox", name="Property Tax ID *")
        )
        self.deed_book_page_input = page.locator("input#title_company:visible, input#Deed_Book_Page:visible, input[name*='Deed']:visible").or_(
            page.get_by_role("textbox", name="Deed Book/Page *")
        )
        self.parcel_save_button = page.locator(
            "#divProjectDetailsTabDisplay button:visible, .k-window:visible button:visible, button:visible"
        ).filter(has_text=re.compile(r"^\s*Save\b", re.I)).first

    # =========================================================================
    # Step-by-Step Workflow Actions
    # =========================================================================

    def verify_project_filters_visible(self, timeout_ms: int = 35000) -> "AddNewProjectPage":
        """Waits for page load and table's '+ Add New Project' button visibility."""
        self._wait_for_loader()
        expect(self.add_new_project_button.first).to_be_visible(timeout=timeout_ms)
        return self

    def open_add_new_project_modal(self) -> "AddNewProjectPage":
        """Clicks '+ Add New Project' to open modal dialog."""
        self._wait_for_loader()
        self.add_new_project_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_project_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.project_id_input.first).to_be_visible(timeout=15000)
        return self

    def fill_and_save_new_project(self, project_id: Optional[str] = None) -> "AddNewProjectPage":
        """Fills 'Add New Project' modal with Faker data, 1st options & present day date."""
        p_id = project_id or str(fake.random_int(10000000, 99999999))
        self.logger.info(f"Creating Project with ID: '{p_id}'")
        self.project_id_input.first.click()
        self.project_id_input.first.fill(p_id)
        self.kendo_dropdown.select_first_option(self.project_division_dropdown)
        self.kendo_dropdown.select_first_option(self.letting_type_dropdown)
        self.kendo_datepicker.select_present_day(
            trigger_locator=self.letting_date_button.first,
            input_target=self.letting_date_input.first,
        )
        self.modal_save_button.first.click()
        self._wait_for_loader()
        return self

    def edit_project_information(self) -> "AddNewProjectPage":
        """Clicks Edit and selects 1st option for STIP and Acquisition Type."""
        self.edit_button.first.click()
        self._wait_for_loader()
        self.kendo_dropdown.select_first_option(self.stip_dropdown)
        self.kendo_dropdown.select_first_option(self.acquisition_type_dropdown)
        self.edit_save_button.first.click()
        self._wait_for_loader()
        return self

    def add_wbs(
        self,
        wbs_code: Optional[str] = None,
        fa: Optional[str] = None,
        wbs_description: Optional[str] = None,
    ) -> "AddNewProjectPage":
        """
        Adds WBS code using strict format pattern and dropdown options sequentially:
          1. Fill WBS * field, then wait.
          2. Verify Division * dropdown is visible, open and select 1st option, wait for cascading County list.
          3. Verify County * dropdown is visible, open to see County list, and select 1st option from list, wait.
          4. Click Save and verify modal closes.
        """
        code = wbs_code or f"{fake.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{fake.random_int(10, 99)}.{fake.random_int(1, 9)}.{fake.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        self.logger.info(f"Adding WBS Code: '{code}'")
        expect(self.kendo_grid_content.first).to_be_visible(timeout=15000)
        self.add_new_wbs_button.click()
        self._wait_for_loader()
        expect(self.wbs_dialog.first).to_be_visible(timeout=10000)

        # 1. Fill WBS * field, then wait
        self.logger.info(f"WBS: Filling WBS code '{code}'")
        self.wbs_input.first.click()
        self.wbs_input.first.fill(code)
        self.wbs_input.first.press("Tab")
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Optional FA field
        if fa and self.wbs_fa_input.first.is_visible():
            self.wbs_fa_input.first.fill(fa)
            self.page.wait_for_timeout(300)

        # 2. Then we can see the Division * dropdown, select 1st option, wait for cascading County list
        self.logger.info("WBS: Verifying Division * dropdown is visible")
        expect(self.wbs_division_dropdown).to_be_visible(timeout=10000)
        self.page.wait_for_timeout(800)
        self.logger.info("WBS: Opening Division * dropdown and selecting 1st option")
        self.wbs_division_dropdown.click()
        self.page.wait_for_timeout(500)
        div_opt = self.page.locator(
            "#Division_ids_listbox li[role='option'], .k-animation-container:visible li[role='option']"
        ).first
        div_opt.wait_for(state="visible", timeout=8000)
        self.logger.info(f"WBS: Selected Division '{div_opt.inner_text().strip()}'")
        div_opt.click()
        self.page.wait_for_timeout(1500)
        self._wait_for_loader()

        # 3. Then we can see the County * dropdown, open to see County list, and select 1st option
        self.logger.info("WBS: Verifying County * dropdown is visible")
        expect(self.wbs_county_multiselect).to_be_visible(timeout=10000)
        self.page.wait_for_timeout(800)
        self.logger.info("WBS: Opening County * dropdown to see County list")
        self.wbs_county_multiselect.click()
        self.page.wait_for_timeout(800)

        county_options = self.page.locator(
            "#County_ids_listbox li[role='option'], .k-animation-container:visible li[role='option'], .k-animation-container:visible li"
        )
        county_options.first.wait_for(state="visible", timeout=10000)
        chosen_county = county_options.first
        self.logger.info(f"WBS: Selecting 1st County from list: '{chosen_county.inner_text().strip()}'")
        chosen_county.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Optional WBS Description
        if wbs_description and self.wbs_desc_input.first.is_visible():
            self.wbs_desc_input.first.fill(wbs_description)
            self.page.wait_for_timeout(300)

        # 4. Save WBS modal
        self.logger.info("WBS: Clicking Save")
        self.wbs_save_button.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.page.locator(".k-window:visible").filter(has_text="Add/Modify WBS")).to_have_count(0, timeout=15000)
        self.logger.info("WBS: Successfully saved and closed.")
        return self

    def add_parcel(
        self,
        parcel_no: Optional[str] = None,
        property_tax_id: Optional[str] = None,
        deed_book_page: Optional[str] = None,
    ) -> "AddNewProjectPage":
        """Adds a new Parcel record using Faker data if not specified."""
        p_no = parcel_no or str(fake.random_int(1000, 9999))
        tax_id = property_tax_id or str(fake.random_int(1000, 9999))
        book_page = deed_book_page or f"{fake.word()}{fake.random_int(10, 99)}"

        self.logger.info(f"Adding Parcel: No='{p_no}', TaxID='{tax_id}', Deed='{book_page}'")
        self.add_new_parcel_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_parcel_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        self.parcel_no_input.first.wait_for(state="visible", timeout=15000)
        self.parcel_no_input.first.click()
        self.parcel_no_input.first.fill(p_no)
        self.property_tax_id_input.first.click()
        self.property_tax_id_input.first.fill(tax_id)
        self.deed_book_page_input.first.click()
        self.deed_book_page_input.first.fill(book_page)
        self.parcel_save_button.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        return self

