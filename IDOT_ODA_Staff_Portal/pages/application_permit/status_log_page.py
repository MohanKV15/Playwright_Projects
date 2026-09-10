import logging
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDatePicker, KendoDropdown

logger = logging.getLogger(__name__)
fake = Faker()


class StatusLogPage(BasePage):
    """
    Page Object Model representing the Status Log & Add Status workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit session context (delegated to ApplicationDetailsPage)
    - Navigate to Status Log view via sidebar menu link
    - Verify page elements (Application Details Permit header, Status Log heading, .k-grid-content)
    - Click 'Add Status' button
    - Verify Status Log form header (Status Log Save Back Action)
    - Select Action Type (1st valid option / 'Application Status') via Kendo UI DropDownList
    - Select Action Item (1st valid option / 'Amended Permit') via Kendo UI DropDownList
    - Populate Date field using present day date (via KendoDatePicker / calendar select)
    - Fill Comments textbox using dynamic Faker generated text
    - Click 'Save', verify 'Operation completed' confirmation modal, click 'OK',
      and verify return to Status Log listing view.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_datepicker = KendoDatePicker(page)

        # 1. Navigation & Context Locators
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_status_log_link = page.get_by_role("link", name="Status Log").or_(
            page.locator("a[href*='StatusLog'], a[href*='Status'], .sidebar a:has-text('Status Log')")
        ).first

        # 2. Listing View Elements
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_status_log = page.get_by_role("heading", name="Status Log").or_(
            page.get_by_text("Status Log")
        ).filter(visible=True).first
        self.grid_content = page.locator(".k-grid-content").first
        self.add_status_button = page.get_by_role("button", name=" Add Status").or_(
            page.get_by_role("button", name=" Add Status")
        ).or_(
            page.get_by_role("button", name="Add Status")
        ).or_(
            page.locator("button:has-text('Add Status'), a:has-text('Add Status'), [role='button']:has-text('Add Status'), .k-button:has-text('Add Status')")
        ).first

        # 3. Status Form Locators (#frmStatus)
        self.status_form_container = page.locator("#partial-form, #frmStatus").first
        self.status_form_header = page.get_by_text("Status Log Save Back Action").or_(
            page.get_by_role("heading", name="Status Log")
        ).first
        self.action_type_trigger = page.locator("#frmStatus").get_by_text("--Select Action Type--").or_(
            page.locator("#frmStatus span.k-input").first
        ).first
        self.action_item_trigger = page.locator("#frmStatus").get_by_text("--Action Item--").or_(
            page.locator("#frmStatus span.k-input").nth(1)
        ).first
        self.datepicker_select_btn = page.get_by_role("button", name="select").first.or_(
            page.locator("#frmStatus .k-datepicker .k-select").first
        )
        self.date_input = page.locator(
            "#frmStatus input[data-role='datepicker'], #frmStatus .k-datepicker input, #StatusDate, [name='StatusDate']"
        ).first
        self.comments_input = page.get_by_role("textbox", name="Comments").or_(
            page.locator("#Comments, [name='Comments'], textarea[name*='Comment' i]")
        ).first
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name=" Save")
        ).or_(
            page.get_by_role("button", name="Save")
        ).or_(
            page.locator("button:has-text('Save')")
        ).first
        self.operation_completed_text = page.get_by_text("Operation completed").or_(
            page.get_by_text("Operation completed successfully.")
        ).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first
        self.status_log_listing_text = page.get_by_text("Status Log Add Status Action").or_(
            page.get_by_role("heading", name="Status Log")
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_status_log(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Status Log page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        action_btn = self.app_details.permit_grid_rows.first.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_status_log_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Status Log")
        expect(self.sidebar_status_log_link).to_be_visible(timeout=15000)
        self.sidebar_status_log_link.click(force=True)
        self._wait_for_loader()

        self.verify_status_log_page_loaded()

    def verify_status_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Status Log page headers, grid container, and Add Status button are visible.
        """
        self.logger.info("Verifying Status Log page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_status_log).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)
        self.logger.info("Status Log page elements verified successfully")

    # -------------------------------------------------------------------------
    # Form Actions
    # -------------------------------------------------------------------------
    def click_add_status(self, timeout_ms: int = 15000) -> None:
        """
        Clicks 'Add Status' button and verifies the Status Log form appears.
        """
        self.logger.info("Clicking 'Add Status' button")
        expect(self.add_status_button).to_be_visible(timeout=timeout_ms)
        self.add_status_button.scroll_into_view_if_needed()
        self.add_status_button.click(force=True)
        self._wait_for_loader()

        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.status_form_header).to_be_visible(timeout=timeout_ms)
        self.logger.info("Status Log form displayed")

    def select_dropdown_first_or_text(
        self, trigger_locator: Locator, preferred_text: Optional[str] = None
    ) -> str:
        """
        Selects option from Kendo UI DropDownList:
        If preferred_text is given and visible, selects preferred_text;
        otherwise selects 1st valid option in the list.
        """
        self.logger.info("Selecting Kendo dropdown option (preferred: '%s')", preferred_text)

        # 1. UI Selection via role='option' click if trigger clicked
        if preferred_text:
            try:
                if self.kendo_dropdown.select_by_locator(trigger_locator, preferred_text):
                    self._wait_for_loader()
                    return preferred_text
            except Exception:
                pass

        # 2. Direct click trigger & option selection fallback
        try:
            expect(trigger_locator).to_be_visible(timeout=5000)
            trigger_locator.click(force=True)
            self.page.wait_for_timeout(300)

            if preferred_text:
                opt = self.page.get_by_role("option", name=preferred_text).or_(
                    self.page.locator(".k-animation-container:visible li, .k-list-container:visible li, [role='option']").filter(has_text=preferred_text)
                ).first
                if opt.is_visible(timeout=3000):
                    opt.click(force=True)
                    self._wait_for_loader()
                    return preferred_text
        except Exception as e:
            self.logger.warning("UI dropdown click note: %s", e)

        # 3. Select 1st valid option from list
        selected_text = self.kendo_dropdown.select_first_valid_option(trigger_locator)
        self._wait_for_loader()
        return selected_text or (preferred_text or "")

    def set_present_day_date(self) -> str:
        """
        Populates Date field with present day (today's) date via KendoDatePicker component.
        """
        self.logger.info("Setting present day date in Status Log date field")
        today_date = self.kendo_datepicker.select_present_day_date(
            container="#frmStatus", field_id="StatusDate"
        )

        # Fallback UI calendar button click and present day selection
        if self.datepicker_select_btn.is_visible(timeout=1000):
            try:
                self.datepicker_select_btn.click(force=True)
                self.page.wait_for_timeout(200)
                cal = self.page.locator(".k-calendar:visible").first
                if cal.is_visible(timeout=1000):
                    today_cell = cal.locator("td.k-today a, td.k-state-focused a, a.k-link").first
                    if today_cell.is_visible(timeout=500):
                        today_cell.click(force=True)
            except Exception as e:
                self.logger.warning("Calendar UI popup interaction note: %s", e)

        return today_date

    def fill_and_submit_status_form(
        self,
        action_type: str = "Application Status",
        action_item: str = "Amended Permit",
        comments: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> Dict[str, str]:
        """
        Fills Status Log form details:
        - Selects Action Type (1st valid option / 'Application Status')
        - Selects Action Item (1st valid option / 'Amended Permit')
        - Sets present day date
        - Fills Comments with dynamic Faker generated text
        - Saves form, verifies 'Operation completed' confirmation modal, clicks OK.
        Returns dictionary of submitted values.
        """
        comm_text = comments or f"Status log test comment {fake.word().capitalize()} {fake.random_int(100, 999)}: {fake.sentence(nb_words=6)}"

        # 1. Select Action Type (1st valid option in dropdown list)
        sel_type = self.select_dropdown_first_or_text(self.action_type_trigger, action_type)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

        # 2. Select Action Item (1st valid option in dropdown list)
        # Ensure dependent dropdown is enabled (not disabled by aria-disabled='true')
        try:
            self.page.wait_for_selector("#frmStatus span.k-dropdown:not([aria-disabled='true'])", timeout=5000)
        except Exception:
            pass
        sel_item = self.select_dropdown_first_or_text(self.action_item_trigger, action_item)

        # 3. Set present day date
        sel_date = self.set_present_day_date()

        # 4. Fill Comments with Faker text
        self.logger.info(f"Filling Comments field: '{comm_text}'")
        expect(self.comments_input).to_be_visible(timeout=timeout_ms)
        self.comments_input.click(force=True)
        self.comments_input.clear()
        self.comments_input.fill(comm_text)

        # 5. Click Save
        self.logger.info("Saving Status Log details")
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.save_button.scroll_into_view_if_needed()
        self.save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

        # 6. Confirm 'Operation completed' confirmation modal alert & click OK
        self.logger.info("Verifying 'Operation completed' confirmation modal alert")
        expect(self.operation_completed_text).to_be_visible(timeout=timeout_ms)
        expect(self.dialog_ok_button).to_be_visible(timeout=timeout_ms)
        self.dialog_ok_button.click(force=True)
        self._wait_for_loader()

        # 7. Verify return to Status Log listing view
        self.logger.info("Verifying return to Status Log page listing view")
        expect(self.status_log_listing_text).to_be_visible(timeout=timeout_ms)

        return {
            "action_type": sel_type,
            "action_item": sel_item,
            "date": sel_date,
            "comments": comm_text,
        }

    def add_status_log_full_workflow(
        self,
        company_name: str = "IDOTOAtest2",
        action_type: str = "Application Status",
        action_item: str = "Amended Permit",
        comments: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Composite high-level workflow:
        1. Navigates to Status Log page
        2. Clicks 'Add Status'
        3. Fills Action Type, Action Item, present day date, and Faker comments
        4. Saves form, confirms OK dialog, and verifies return to listing view
        """
        self.navigate_to_status_log(company_name=company_name)
        self.click_add_status()
        return self.fill_and_submit_status_form(
            action_type=action_type,
            action_item=action_item,
            comments=comments,
        )
