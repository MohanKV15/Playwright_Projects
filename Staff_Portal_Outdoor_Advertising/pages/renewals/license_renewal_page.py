import re
import logging
import datetime
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class LicenseRenewalPage(BasePage):
    """Page Object Model for the License Renewal section under Renewals module."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Menu Links
        self.renewals_menu_link = page.get_by_role("link", name="Renewals ")
        self.license_renewal_link = page.get_by_role("link", name="License Renewal")

        # Headings & Containers
        self.license_renewal_heading = page.get_by_role("heading", name="License Renewal", exact=True)
        self.partial_form_first = page.locator("#partial-form").first
        self.log_heading = page.get_by_role("heading", name="Log", exact=True)
        self.partial_form_second = page.locator("#partial-form").nth(1)
        self.log_content_div = page.locator(".k-grid-content")

        # Action Buttons
        self.generate_pre_renewal_btn = page.get_by_role("button", name=" Generate Pre-Renewal")
        self.generate_renewal_btn = page.get_by_role("button", name=" Generate Renewal")
        self.generate_late_notices_btn = page.get_by_role("button", name=" Generate Late Notices")
        self.status_update_license_not_btn = page.get_by_role("button", name=" Status Update - License Not")
        self.status_update_license_cancelled_btn = page.get_by_role("button", name=" Status Update - License Cancelled")

        # Dialogs / Popups
        self.kendo_ok_button = page.get_by_role("button", name="OK")
        self.proceed_button = page.get_by_role("button", name=" Proceed")

        # Modal Headings
        self.generate_pre_renewal_heading = page.get_by_role("heading", name="Generate License Pre-Renewal")
        self.generate_renewal_heading = page.get_by_role("heading", name="Generate License Renewal")
        self.generate_late_notice_heading = page.get_by_role("heading", name="Generate License Late Notice")
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

    def navigate_to_license_renewal(self) -> None:
        """Navigates to Renewals -> License Renewal and asserts initial page elements are visible."""
        logger.info("Navigating to License Renewal page")
        self._expand_navigation_menu()

        # If sub-menu link is not visible, toggle the parent Renewals menu link
        if not self.license_renewal_link.is_visible():
            logger.info("License Renewal link not visible; clicking Renewals menu header to expand.")
            self.renewals_menu_link.click()
            self.page.wait_for_timeout(1000)

        self.license_renewal_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

        # Assert initial view elements
        expect(self.license_renewal_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.generate_pre_renewal_btn).to_be_visible(timeout=10000)
        expect(self.log_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_second).to_be_visible(timeout=10000)
        expect(self.log_content_div).to_be_visible(timeout=10000)

    def generate_pre_renewal(self) -> None:
        """Triggers the 'Generate Pre-Renewal' flow and handles confirmation alerts."""
        self._wait_for_loader()
        logger.info("Clicking Generate Pre-Renewal button")
        self.generate_pre_renewal_btn.click()
        self.page.wait_for_timeout(1000)

        expect(self.generate_pre_renewal_heading).to_be_visible(timeout=10000)
        expect(self.page.locator("div:nth-child(2) > div:nth-child(2)").first).to_be_visible(timeout=10000)
        expect(self.page.locator(".row > div:nth-child(3)").first).to_be_visible(timeout=10000)

        logger.info("Clicking Proceed button on Pre-Renewal modal")
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

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
        """Triggers the 'Generate Renewal' flow and handles confirmation alerts."""
        self._wait_for_loader()
        logger.info("Clicking Generate Renewal button")
        self.generate_renewal_btn.click()
        self.page.wait_for_timeout(1000)

        expect(self.generate_renewal_heading).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Customer email notice (SUBJECT) NOTICE REGARDING NJDOT PERMIT RENEWALS")).to_be_visible(timeout=10000)
        expect(self.page.locator("#LicenseRenewalGenerate > div:nth-child(2)")).to_be_visible(timeout=10000)

        logger.info("Clicking Proceed button on Renewal modal")
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

        logger.info("Handling Renewal confirmation alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            active_dialog.wait_for(state="visible", timeout=8000)
            if active_dialog.get_by_text("Are you sure you want to").is_visible(timeout=3000):
                self.kendo_ok_button.click()
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Renewal confirmation dialog did not appear: {e}")

    def generate_late_notices(self) -> None:
        """Triggers the 'Generate Late Notices' flow and handles confirmation alerts."""
        self._wait_for_loader()
        logger.info("Clicking Generate Late Notices button")
        self.generate_late_notices_btn.click()
        self.page.wait_for_timeout(1000)

        expect(self.generate_late_notice_heading).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Customer email notice (SUBJECT) NOTICE REGARDING NJDOT PERMIT RENEWALS")).to_be_visible(timeout=10000)
        expect(self.page.locator("#LicenseRenewalGenerate > div:nth-child(2)")).to_be_visible(timeout=10000)

        logger.info("Clicking Proceed button on Late Notices modal")
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

        logger.info("Handling Late Notices confirmation alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            active_dialog.wait_for(state="visible", timeout=8000)
            if active_dialog.get_by_text("Are you sure you want to").is_visible(timeout=3000):
                self.kendo_ok_button.click()
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Late Notices confirmation dialog did not appear: {e}")

    def status_update_license_not(self) -> None:
        """Triggers the 'Status Update - License Not' flow and dismisses the success alert."""
        self._wait_for_loader()
        logger.info("Clicking Status Update - License Not button")
        self.status_update_license_not_btn.click()

        logger.info("Asserting License Status Updated alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        expect(active_dialog).to_be_visible(timeout=15000)
        expect(active_dialog.get_by_text("License Status Updated")).to_be_visible(timeout=10000)
        self.kendo_ok_button.click()
        self._wait_for_loader()

    def status_update_license_cancelled(self) -> None:
        """Triggers the 'Status Update - License Cancelled' flow and dismisses the success alert."""
        self._wait_for_loader()
        logger.info("Clicking Status Update - License Cancelled button")
        self.status_update_license_cancelled_btn.click()

        logger.info("Asserting License Status Updated alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        expect(active_dialog).to_be_visible(timeout=15000)
        expect(active_dialog.get_by_text("License Status Updated")).to_be_visible(timeout=10000)
        self.kendo_ok_button.click()
        self._wait_for_loader()

    def select_date_range_three_months_ago(self) -> None:
        """Opens From Date picker, navigates 3 months back, selects day 19 (fallback to 15), and selects day 19 on To Date picker."""
        self._wait_for_loader()
        target_day = "19"

        logger.info("Opening From Date picker")
        self.page.get_by_role("button", name="select").first.click()
        self.page.wait_for_timeout(500)

        logger.info("Navigating 3 months back")
        # In codegen: dblclick on Previous, then click on Previous (total 3 clicks)
        self.page.get_by_role("button", name="Previous").dblclick()
        self.page.wait_for_timeout(300)
        self.page.get_by_role("button", name="Previous").click()
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting day {target_day} for From Date")
        calendar_locator = self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible")
        day_link = calendar_locator.get_by_role("link", name=target_day, exact=True).first
        try:
            if day_link.is_visible(timeout=2000):
                self.js_click(day_link)
            else:
                logger.warning(f"Day {target_day} not found 3 months ago, falling back to day 15")
                self.js_click(calendar_locator.get_by_role("link", name="15", exact=True).first)
        except Exception:
            logger.warning(f"Failed to click day {target_day}, falling back to day 15")
            self.js_click(calendar_locator.get_by_role("link", name="15", exact=True).first)
        self.page.wait_for_timeout(500)

        logger.info("Opening To Date picker")
        self.page.get_by_role("button", name="select").nth(1).click()
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting day {target_day} for To Date")
        self.js_click(calendar_locator.get_by_role("link", name=target_day, exact=True).first)
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
        """Reads and returns the name/title of the first record in the log grid."""
        self._wait_for_loader()
        logger.info("Locating the first row of LogListGrid or .k-grid-content")
        grid_row_selector = "#LogListGrid tbody tr, .k-grid-content tbody tr, [role='grid'] tbody tr"
        self.page.wait_for_selector(grid_row_selector, timeout=15000)
        first_row = self.page.locator(grid_row_selector).first
        
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
        logger.info("Clicking the View document button of the first record")
        
        grid_row_selector = "#LogListGrid tbody tr, .k-grid-content tbody tr, [role='grid'] tbody tr"
        view_btn = self.page.locator(grid_row_selector).first.get_by_role("button").filter(has_text=re.compile(r"^$")).first
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
        
        grid_row_selector = "#LogListGrid tbody tr, .k-grid-content tbody tr, [role='grid'] tbody tr"
        edit_btn = self.page.locator(grid_row_selector).first.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(1)
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
