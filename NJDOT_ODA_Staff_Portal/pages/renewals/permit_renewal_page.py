import re
import logging
import datetime
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitRenewalPage(BasePage):
    """Page Object Model for the Permit Renewal section under Renewals module."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Menu Links
        self.renewals_menu_link = page.get_by_role("link", name="Renewals ")
        self.permit_renewal_link = page.get_by_role("link", name="Permit Renewal")

        # Headings & Containers
        self.annual_permit_renewal_heading = page.get_by_role("heading", name="Annual Permit Renewal")
        self.partial_form_first = page.locator("#partial-form").first
        self.log_heading = page.get_by_role("heading", name="Log", exact=True)
        self.partial_form_second = page.locator("#partial-form").nth(1)
        self.log_content_div = page.locator("div:nth-child(2) > .col-md-12")

        # Action Buttons
        self.generate_pre_renewal_btn = page.get_by_role("button", name=" Generate Pre-Renewal")
        self.generate_renewal_btn = page.get_by_role("button", name=" Generate Renewal")
        self.generate_paper_renewal_btn = page.get_by_role("button", name=" Generate Paper Renewal")
        self.status_update_permit_not_btn = page.get_by_role("button", name=" Status Update - Permit Not")
        self.status_update_permit_cancelled_btn = page.get_by_role("button", name=" Status Update - Permit Cancelled")

        # Dialogs / Popups
        self.kendo_ok_button = page.get_by_role("button", name="OK")
        self.kendo_cancel_button = page.get_by_role("button", name=" Cancel")
        self.proceed_button = page.get_by_role("button", name=" Proceed")

        # Modal Headings
        self.generate_pre_renewal_heading = page.get_by_role("heading", name="Generate Permit Pre-Renewal")
        self.generate_renewal_heading = page.get_by_role("heading", name="Generate Permit Renewals")
        self.log_details_heading = page.get_by_role("heading", name="Log Details")

        # Filter elements
        self.search_button = page.get_by_role("button", name=" Search")
        self.type_dropdown_trigger = page.locator("#frmFeeSearch").get_by_text("--Select Type--")
        self.name_search_input = page.get_by_role("textbox", name="Name")

        # Save Action in Details
        self.save_button = page.get_by_role("button", name=" Save")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all renewals links are visible."""
        logger.info("Expanding Renewals PanelBar navigation panel.")
        self._expand_kendo_panel("renewal")

    def navigate_to_permit_renewal(self) -> None:
        """Navigates to Renewals -> Permit Renewal and asserts initial page elements are visible."""
        logger.info("Navigating to Permit Renewal page")
        self._expand_navigation_menu()

        # If sub-menu link is not visible, toggle the parent Renewals menu link
        if not self.permit_renewal_link.is_visible():
            logger.info("Permit Renewal link not visible; clicking Renewals menu header to expand.")
            self.renewals_menu_link.click()
            self.page.wait_for_timeout(1000)

        self.permit_renewal_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

        # Assert initial view elements
        expect(self.annual_permit_renewal_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.log_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_second).to_be_visible(timeout=10000)
        expect(self.log_content_div).to_be_visible(timeout=10000)

    def generate_pre_renewal(self) -> None:
        """Triggers the 'Generate Pre-Renewal' flow and handles the confirmation alerts."""
        self._wait_for_loader()
        logger.info("Clicking Generate Pre-Renewal button")
        self.generate_pre_renewal_btn.click()
        self.page.wait_for_timeout(1000)

        expect(self.generate_pre_renewal_heading).to_be_visible(timeout=10000)

        logger.info("Clicking Proceed button on Pre-Renewal modal")
        self.page.locator("#partial-form").first.wait_for(state="visible", timeout=5000)
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

        # Handle the Kendo/Alert confirmation dialog "Are you sure you want to..."
        logger.info("Handling Pre-Renewal confirmation alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            active_dialog.wait_for(state="visible", timeout=8000)
            if active_dialog.get_by_text("Are you sure you want to").is_visible(timeout=3000):
                self.kendo_ok_button.click()
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Pre-Renewal confirmation dialog did not appear: {e}")

    def generate_renewal(self) -> None:
        """Triggers the 'Generate Renewal' flow and handles the alerts & exceptions conditionally."""
        self._wait_for_loader()
        logger.info("Clicking Generate Renewal button")
        self.generate_renewal_btn.click()
        self.page.wait_for_timeout(1000)

        expect(self.generate_renewal_heading).to_be_visible(timeout=10000)
        expect(self.page.locator("div").filter(has_text="Online Mail Customer email").nth(4)).to_be_visible(timeout=10000)

        logger.info("Clicking Proceed button on Renewal modal")
        self.proceed_button.click()
        self.page.wait_for_timeout(2000)

        # Handle first warning alert popup if it appears
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            if active_dialog.is_visible(timeout=5000):
                logger.info("Dismissing first renewal alert dialog")
                self.kendo_ok_button.click()
                self._wait_for_loader()
        except Exception:
            logger.info("First renewal alert did not appear")

        # Handle second exception popup "Exception occurred" if it appears
        try:
            active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
            if active_dialog.is_visible(timeout=5000):
                logger.info("Dismissing exception alert dialog")
                self.kendo_ok_button.click()
                self._wait_for_loader()
        except Exception:
            logger.info("Exception occurred alert did not appear")

        # If the main renewal modal is still open, close it using Cancel
        try:
            cancel_btn = self.page.locator(".k-window:visible, .k-dialog:visible").get_by_role("button", name=" Cancel").first
            if cancel_btn.is_visible(timeout=3000):
                logger.info("Clicking Cancel to close Renewal modal")
                cancel_btn.click()
                self._wait_for_loader()
        except Exception as e:
            logger.info(f"Renewal modal cancel button not found or clicked: {e}")

    def generate_paper_renewal(self) -> None:
        """Triggers the 'Generate Paper Renewal' flow and handles the error popup."""
        self._wait_for_loader()
        logger.info("Clicking Generate Paper Renewal button")
        self.generate_paper_renewal_btn.click()
        self._wait_for_loader()

        # Handle popup warning dialog "Something went wrong contact..."
        logger.info("Dismissing paper renewal error alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            active_dialog.wait_for(state="visible", timeout=8000)
            self.kendo_ok_button.click()
            self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Paper renewal error dialog did not appear: {e}")

    def status_update_permit_not(self) -> None:
        """Triggers the 'Status Update - Permit Not' flow and dismisses the popup."""
        self._wait_for_loader()
        logger.info("Verifying Status Update - Permit Not button is visible")
        expect(self.status_update_permit_not_btn).to_be_visible(timeout=10000)

        logger.info("Clicking Status Update - Permit Not button")
        self.status_update_permit_not_btn.click()
        
        logger.info("Dismissing alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            active_dialog.wait_for(state="visible", timeout=8000)
            self.kendo_ok_button.click()
            self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Status Update - Permit Not alert did not appear: {e}")

    def status_update_permit_cancelled(self) -> None:
        """Triggers the 'Status Update - Permit Cancelled' flow and asserts success popup."""
        self._wait_for_loader()
        logger.info("Clicking Status Update - Permit Cancelled button")
        self.status_update_permit_cancelled_btn.click()

        logger.info("Asserting Permit Status Updated alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        expect(active_dialog).to_be_visible(timeout=15000)
        expect(active_dialog.get_by_text("Permit Status Updated")).to_be_visible(timeout=10000)
        self.kendo_ok_button.click()
        self._wait_for_loader()

    def select_date_range_three_months_ago(self) -> None:
        """Opens From Date picker, navigates 3 months back, selects today's day (with fallback), and selects today's day on To Date picker."""
        self._wait_for_loader()
        import datetime
        today = datetime.datetime.now()
        today_day = str(today.day)

        logger.info("Opening From Date picker")
        self.page.get_by_role("button", name="select").first.click()
        self.page.wait_for_timeout(500)

        logger.info("Navigating 3 months back")
        for _ in range(3):
            self.page.get_by_role("button", name="Previous").click()
            self.page.wait_for_timeout(300)

        logger.info(f"Selecting day {today_day} for From Date")
        calendar_locator = self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible")
        day_link = calendar_locator.get_by_role("link", name=today_day, exact=True).first
        try:
            if day_link.is_visible(timeout=2000):
                self.js_click(day_link)
            else:
                logger.warning(f"Day {today_day} not found 3 months ago, falling back to day 15")
                self.js_click(calendar_locator.get_by_role("link", name="15", exact=True).first)
        except Exception:
            logger.warning(f"Failed to click day {today_day}, falling back to day 15")
            self.js_click(calendar_locator.get_by_role("link", name="15", exact=True).first)
        self.page.wait_for_timeout(500)

        logger.info("Opening To Date picker")
        self.page.get_by_role("button", name="select").nth(1).click()
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting day {today_day} for To Date")
        self.js_click(calendar_locator.get_by_role("link", name=today_day, exact=True).first)
        self.page.wait_for_timeout(500)

        logger.info("Clicking Search button to filter by Date Range")
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def filter_by_type_document(self) -> None:
        """Selects 'Document' in the Type dropdown and performs search."""
        self._wait_for_loader()
        logger.info("Opening Type dropdown")
        self.type_dropdown_trigger.click()
        self.page.wait_for_timeout(500)

        logger.info("Selecting option 'Document'")
        self.js_click(self.page.get_by_role("option", name="Document"))
        self.page.wait_for_timeout(500)

        logger.info("Clicking Search button to filter by Type")
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def get_first_record_name(self) -> str:
        """Reads and returns the name/title of the first record in the LogListGrid."""
        self._wait_for_loader()
        logger.info("Locating the first row of LogListGrid")
        self.page.wait_for_selector("#LogListGrid tbody tr", timeout=10000)
        first_row = self.page.locator("#LogListGrid tbody tr").first
        
        # Read the inner text of the Name/Title cell (3rd cell, index 2)
        name_cell = first_row.locator("td").nth(2)
        name_text = name_cell.inner_text().strip()
        logger.info(f"Retrieved first record name: '{name_text}'")
        return name_text

    def search_by_name(self, name: str) -> None:
        """Enters the name in the textbox and clicks search."""
        self._wait_for_loader()
        logger.info(f"Filtering grid by record name: '{name}'")
        self.name_search_input.click()
        self.name_search_input.fill(name)
        self.page.wait_for_timeout(500)

        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def view_and_close_first_record_document(self) -> None:
        """Clicks the View button of the first record, handles the resulting popup, and closes it."""
        self._wait_for_loader()
        logger.info("Clicking the View document button of the first record (popup expectation)")
        
        # In the grid, the View button is typically the first button or matches the 3rd to last cell action
        # Codegen used: page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2)
        view_btn = self.page.locator("#LogListGrid tbody tr").first.get_by_role("button").filter(has_text=re.compile(r"^$")).first
        if view_btn.count() == 0:
            view_btn = self.page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(2)

        with self.page.expect_popup() as page_info:
            self.js_click(view_btn)
        
        popup_page = page_info.value
        logger.info("Successfully opened document preview popup. Closing popup page.")
        self.page.wait_for_timeout(1000)
        popup_page.close()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

    def edit_and_save_first_record(self) -> None:
        """Clicks the Edit button of the first record, asserts the 'Log Details' heading, and clicks Save."""
        self._wait_for_loader()
        logger.info("Clicking the Edit button of the first record")
        
        # In the grid, the Edit button is next to View
        # Codegen used: page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(3)
        edit_btn = self.page.locator("#LogListGrid tbody tr").first.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(1)
        if edit_btn.count() == 0:
            edit_btn = self.page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(3)

        self.js_click(edit_btn)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Assert log details headings are visible
        expect(self.log_details_heading).to_be_visible(timeout=10000)
        expect(self.page.locator("#partial-form").first).to_be_visible(timeout=10000)

        logger.info("Clicking Save button inside Log Details")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        logger.info("Log details edited and saved successfully")
