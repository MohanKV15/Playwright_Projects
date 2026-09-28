import logging
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown, KendoDatePicker

logger = logging.getLogger(__name__)


class FeeSchedulePage(BasePage):
    """
    Optimized Page Object Model representing the Fee Schedule module in the IDOT ODA Staff Portal.
    Handles sidebar navigation, listing validation, dynamic application type dropdown selection,
    present day date entry, saving, and verifying created records in the grid.
    """

    APPLICATION_TYPES: List[str] = [
        "Business Area Sign - Primary Highway",
        "Business Area Sign - Interstate Highway",
        "Advertising Registration",
        "Directional Sign, Official Sign or Official Notice",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_datepicker = KendoDatePicker(page)

        # Listing Page Locators
        self.heading_fee_schedule = page.get_by_role("heading", name=re.compile(r"Fee\s+Schedule", re.I)).or_(
            page.locator(".page-header, .page-title, h1, h2, h3, h4, .title, legend").filter(has_text=re.compile(r"Fee\s+Schedule", re.I))
        ).first
        self.text_fee_schedule_info = page.get_by_text(re.compile(r"Fee\s+Schedule\s*\(Select", re.I)).or_(
            page.get_by_text("(Select the option below and click Search)")
        ).first
        self.grid_content = page.locator(".k-grid-content, #gridFeeSchedule, table").first
        self.add_fee_schedule_button = page.get_by_role("button", name=re.compile(r"Add\s+Fee\s+Schedule", re.I)).or_(
            page.locator("#btnAddFeeSchedule, button:has-text('Add Fee Schedule')")
        ).first

        # Details Form Locators
        self.heading_save_cancel = page.get_by_text(re.compile(r"Fee\s+Schedule\s+Save\s+Cancel", re.I)).or_(
            page.get_by_text("Save Cancel")
        ).first
        self.form_details = page.locator("#frmFeeScheduleDetails")
        self.date_picker_btn = self.form_details.get_by_role("button", name="select").or_(
            self.form_details.locator(".k-datepicker .k-select, button:has-text('select')")
        ).first
        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("#btnSave, button:has-text('Save')")
        ).first
        self.operation_completed_text = page.get_by_text(re.compile(r"Operation\s+completed", re.I)).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # Search Form Locators
        self.form_search = page.locator("#frmFeeSearch")
        self.search_button = self.form_search.get_by_role("button", name=re.compile(r"Search", re.I)).or_(
            page.locator("#btnSearch, button:has-text('Search')")
        ).first
        self.grid_rows = page.locator(".k-grid-content table tbody tr, #gridFeeSchedule tbody tr")

    # -------------------------------------------------------------------------
    # Reusable Helpers
    # -------------------------------------------------------------------------
    def _select_dropdown(self, container: Locator, option_text: str) -> None:
        """Unified helper to click and select an option from a Kendo dropdown."""
        trigger = container.locator(".k-dropdown, [data-role='dropdownlist']").or_(
            container.get_by_text(re.compile(r"Select\s+Type|Business\s+Area|Advertising|Directional", re.I))
        ).first
        expect(trigger).to_be_visible(timeout=10000)
        trigger.click(force=True)
        self.page.wait_for_timeout(200)

        keyword = option_text.split(" - ")[0] if " - " in option_text else option_text.split(",")[0]
        option = self.page.get_by_role("option", name=re.compile(re.escape(keyword), re.I)).or_(
            self.page.locator(".k-animation-container:visible li, .k-list-container:visible li").filter(
                has_text=re.compile(re.escape(keyword), re.I)
            )
        ).first

        if option.is_visible(timeout=2000):
            option.click(force=True)
        else:
            container_id = container.evaluate("el => el.id || ''")
            self.kendo_dropdown.select(f"#{container_id}", option_text=keyword)
        self.page.wait_for_timeout(200)

    # -------------------------------------------------------------------------
    # Core Actions
    # -------------------------------------------------------------------------
    def navigate_to_fee_schedule_listing(self, timeout_ms: int = 20000) -> None:
        """Navigates to Fee Schedule Listing and validates headers."""
        self.logger.info("Navigating to Fee Schedule Listing page")
        self._wait_for_loader()

        if "FeeScheduleListing" in self.page.url and self.add_fee_schedule_button.is_visible(timeout=1000):
            return

        dash_link = self.page.locator(".sidebar a:has-text('Dashboard'), a[href*='Dashboard']").first
        if dash_link.is_visible(timeout=1500):
            dash_link.click(force=True)
            self._wait_for_loader()

        parent_menu = self.page.locator(".sidebar a.k-header:has-text('Fee Schedule'), .sidebar li:has-text('Fee Schedule') > a").first
        sub_link = self.page.locator(".sidebar ul.k-group a:has-text('Fee Schedule Listing'), .sidebar a[href*='FeeScheduleListing']").first

        try:
            parent_menu.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass

        if not sub_link.is_visible(timeout=1000):
            parent_menu.click(force=True)
            self.page.wait_for_timeout(400)

        if sub_link.is_visible(timeout=3000):
            sub_link.click(force=True)
            self._wait_for_loader()

        if "FeeScheduleListing" not in self.page.url:
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319FeeScheduleListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass
            self._wait_for_loader()

        expect(self.heading_fee_schedule).to_be_visible(timeout=timeout_ms)
        expect(self.text_fee_schedule_info).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

    def click_add_fee_schedule(self, timeout_ms: int = 20000) -> None:
        """Clicks '+ Add Fee Schedule' button and verifies details form displays."""
        self.logger.info("Clicking Add Fee Schedule button")
        expect(self.add_fee_schedule_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.add_fee_schedule_button)
        self._wait_for_loader()

        expect(self.heading_fee_schedule).to_be_visible(timeout=timeout_ms)
        expect(self.heading_save_cancel).to_be_visible(timeout=timeout_ms)

    def select_application_type(self, application_type: Optional[str] = None) -> str:
        """Dynamically selects an application type from dropdown."""
        target_type = application_type or random.choice(self.APPLICATION_TYPES)
        self.logger.info("Selecting Application Type: '%s'", target_type)
        self._select_dropdown(self.form_details, target_type)
        return target_type

    def select_present_day_date(self, timeout_ms: int = 10000) -> str:
        """Selects present day date using Kendo DatePicker calendar widget."""
        today = datetime.now()
        today_day = str(today.day)
        today_formatted = today.strftime("%m/%d/%Y")
        self.logger.info("Selecting present day date: %s", today_formatted)

        if self.date_picker_btn.is_visible(timeout=timeout_ms):
            self.date_picker_btn.click(force=True)
            self.page.wait_for_timeout(200)

            day_cell = self.page.locator(".k-calendar:visible td:not(.k-other-month) a").filter(
                has_text=re.compile(rf"^{today_day}$")
            ).or_(self.page.locator(".k-calendar:visible td.k-today a")).first

            if day_cell.is_visible(timeout=2000):
                day_cell.click(force=True)
            else:
                self.kendo_datepicker.set_date_by_id("frmFeeScheduleDetails input[data-role='datepicker']", today_formatted)
        else:
            self.kendo_datepicker.select_present_day_date(container=self.form_details)

        self.page.wait_for_timeout(200)
        return today_formatted

    def save_and_confirm(self, timeout_ms: int = 20000) -> None:
        """Clicks Save button, asserts 'Operation completed' dialog, and confirms OK."""
        self.logger.info("Saving Fee Schedule record")
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.save_button)
        self._wait_for_loader()

        expect(self.operation_completed_text).to_be_visible(timeout=timeout_ms)
        expect(self.dialog_ok_button).to_be_visible(timeout=timeout_ms)
        self.dialog_ok_button.click(force=True)
        self.page.wait_for_timeout(300)
        self._wait_for_loader()

    def search_by_application_type(self, application_type: str, timeout_ms: int = 15000) -> None:
        """Searches by application type on the Fee Schedule search filter."""
        self.logger.info("Searching Fee Schedule by Application Type: '%s'", application_type)
        self._wait_for_loader()
        self._select_dropdown(self.form_search, application_type)

        expect(self.search_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.search_button)
        self._wait_for_loader()

    def verify_record_in_grid(self, application_type: str, timeout_ms: int = 15000) -> bool:
        """Verifies that a record matching the application type exists in the grid table."""
        self.logger.info("Verifying record in grid for: '%s'", application_type)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

        keyword = application_type.split(" - ")[0] if " - " in application_type else application_type.split(",")[0]
        matched_row = self.grid_rows.filter(has_text=re.compile(re.escape(keyword), re.I)).first
        expect(matched_row).to_be_visible(timeout=timeout_ms)
        return True

    # -------------------------------------------------------------------------
    # Composite End-to-End Workflow
    # -------------------------------------------------------------------------
    def execute_add_and_verify_fee_schedule_workflow(
        self, application_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete Fee Schedule workflow:
        1. Navigate to Fee Schedule Listing.
        2. Click '+ Add Fee Schedule'.
        3. Dynamically select application type.
        4. Select present day date in calendar.
        5. Save and confirm Operation completed modal.
        6. Filter by the saved application type and click Search.
        7. Verify that the saved record appears in the grid.
        """
        self.navigate_to_fee_schedule_listing()
        self.click_add_fee_schedule()
        chosen_type = self.select_application_type(application_type=application_type)
        selected_date = self.select_present_day_date()
        self.save_and_confirm()
        self.search_by_application_type(application_type=chosen_type)
        is_verified = self.verify_record_in_grid(application_type=chosen_type)

        return {
            "status": "Verified successfully",
            "application_type": chosen_type,
            "effective_date": selected_date,
            "grid_verified": is_verified,
        }
