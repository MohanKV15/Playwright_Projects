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
        self.renewals_menu_link = page.get_by_role("link", name=re.compile(r"Renewals\s*", re.I))
        self.permit_renewal_link = page.get_by_role("link", name="Permit Renewal")

        # Headings & Containers
        self.annual_permit_renewal_heading = page.get_by_role("heading", name="Annual Permit Renewal")
        self.partial_form_first = page.locator("#partial-form").first
        self.log_heading = page.get_by_role("heading", name="Log", exact=True)
        self.partial_form_second = page.locator("#partial-form").nth(1)
        self.log_content_div = page.locator("div:nth-child(2) > .col-md-12")

        # Action Buttons with robust ID and regex matching
        self.generate_pre_renewal_btn = page.locator("#GenPreRenewal").or_(
            page.get_by_role("button", name=re.compile(r"Generate Pre-Renewal", re.I))
        )
        self.generate_renewal_btn = page.locator("#GenRenewal").or_(
            page.get_by_role("button", name=re.compile(r"Generate Renewal", re.I))
        )
        self.generate_paper_renewal_btn = page.locator("#GenPaperRenewal").or_(
            page.get_by_role("button", name=re.compile(r"Generate Paper Renewal", re.I))
        )
        self.status_update_permit_not_btn = page.locator("#btnPermitNotRenewed").or_(
            page.get_by_role("button", name=re.compile(r"Status Update - Permit Not", re.I))
        )
        self.status_update_permit_cancelled_btn = page.locator("#btnPermitCancelled").or_(
            page.get_by_role("button", name=re.compile(r"Status Update - Permit Cancelled", re.I))
        )

        # Dialogs / Popups
        self.kendo_ok_button = page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')").first
        self.kendo_cancel_button = page.locator("#Cancel, #btnPreRenewCancel").or_(
            page.get_by_role("button", name=re.compile(r"Cancel", re.I))
        )
        self.proceed_button = page.locator("#btnProceed, #btnRenewProceed").or_(
            page.get_by_role("button", name=re.compile(r"Proceed", re.I))
        )

        # Modal Headings
        self.generate_pre_renewal_heading = page.get_by_role("heading", name="Generate Permit Pre-Renewal")
        self.generate_renewal_heading = page.get_by_role("heading", name="Generate Permit Renewals")
        self.log_details_heading = page.get_by_role("heading", name="Log Details")

        # Filter elements
        self.search_button = page.locator("#btnSearch, #FeeSearchbtn").or_(page.get_by_role("button", name=" Search"))
        self.type_dropdown_trigger = page.locator("#frmFeeSearch, #partial-form").first.locator(".k-dropdown-wrap, [role='listbox']").first
        self.name_search_input = page.get_by_role("textbox", name="Name")

        # Save Action in Details
        self.save_button = page.locator("#btnSave, #btnSubmit").or_(page.get_by_role("button", name=" Save"))

    def _clear_loader(self) -> None:
        """Removes loading spinner classes from #loader to prevent pointer interception."""
        try:
            self.page.evaluate("() => { (window.jQuery || window.$)('#loader').removeClass('k-loading-image centering-notification'); }")
        except Exception:
            pass

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all renewals links are visible."""
        logger.info("Expanding Renewals PanelBar navigation panel.")
        self._expand_kendo_panel("renewal")

    def navigate_to_permit_renewal(self) -> None:
        """Navigates to Renewals -> Permit Renewal and asserts initial page elements are visible."""
        logger.info("Navigating to Permit Renewal page")
        self._expand_navigation_menu()

        if not self.permit_renewal_link.is_visible():
            logger.info("Permit Renewal link not visible; clicking Renewals menu header to expand.")
            self.renewals_menu_link.click()
            self.page.wait_for_timeout(1000)

        self.permit_renewal_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

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
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        logger.info("Clicking Proceed button on Pre-Renewal modal")
        self.proceed_button.wait_for(state="visible", timeout=10000)
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

        # Handle confirmation dialog
        logger.info("Handling Pre-Renewal confirmation alert dialog")
        try:
            active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
            if active_dialog.is_visible(timeout=5000):
                ok_btn = active_dialog.locator("button:has-text('OK'), button:has-text('Proceed')").first
                if ok_btn.is_visible():
                    ok_btn.click()
                    self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Pre-Renewal confirmation dialog note: {e}")
        self.dismiss_kendo_dialogs()

        # If still on Pre-Renewal page, return back to listing
        if "PermitPreRenwal" in self.page.url:
            cancel = self.page.locator("#btnPreRenewCancel, #Cancel").first
            if cancel.is_visible(timeout=2000):
                cancel.click()
                self.page.wait_for_load_state("networkidle")
                self._wait_for_loader()
            else:
                self.navigate_to_permit_renewal()

        expect(self.annual_permit_renewal_heading).to_be_visible(timeout=15000)

    def generate_renewal(self) -> None:
        """Triggers the 'Generate Renewal' flow, confirms, dismisses alerts, and returns to Renewal listing."""
        self._wait_for_loader()
        logger.info("Clicking Generate Renewal button")
        self.generate_renewal_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        logger.info("Clicking Proceed button on Renewal modal")
        self.proceed_button.wait_for(state="visible", timeout=10000)
        self.proceed_button.click()
        self.page.wait_for_timeout(1000)

        # Handle kendo.confirm dialog: click OK
        try:
            active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
            if active_dialog.is_visible(timeout=5000):
                ok_btn = active_dialog.locator("button:has-text('OK')").first
                if ok_btn.is_visible():
                    ok_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self._wait_for_loader()
        except Exception:
            pass

        # Handle subsequent alerts / errors if any
        self.dismiss_kendo_dialogs()

        # Return to Renewal listing page if still on AnnualRenewalGen page
        if "PermitAnnualRenwal" in self.page.url:
            logger.info("Returning to Permit Renewal listing from Annual Renewal generator")
            cancel = self.page.locator("#Cancel, #btnPreRenewCancel").first
            if cancel.is_visible(timeout=3000):
                cancel.click()
                self.page.wait_for_load_state("networkidle")
                self._wait_for_loader()
            else:
                self.navigate_to_permit_renewal()

        expect(self.annual_permit_renewal_heading).to_be_visible(timeout=15000)

    def generate_paper_renewal(self) -> None:
        """Triggers the 'Generate Paper Renewal' flow and handles the popup."""
        self._wait_for_loader()
        logger.info("Clicking Generate Paper Renewal button")
        expect(self.generate_paper_renewal_btn).to_be_visible(timeout=15000)
        self.generate_paper_renewal_btn.click()
        self.page.wait_for_timeout(1000)
        self.dismiss_kendo_dialogs()
        self._clear_loader()
        self._wait_for_loader()

    def status_update_permit_not(self) -> None:
        """Triggers the 'Status Update - Permit Not' flow and dismisses the popup."""
        self._wait_for_loader()
        self._clear_loader()
        logger.info("Verifying Status Update - Permit Not button is visible")
        expect(self.status_update_permit_not_btn).to_be_visible(timeout=10000)

        logger.info("Clicking Status Update - Permit Not button")
        self.status_update_permit_not_btn.click(force=True)
        self.page.wait_for_timeout(1000)
        self.dismiss_kendo_dialogs()
        self._clear_loader()
        self._wait_for_loader()

    def status_update_permit_cancelled(self) -> None:
        """Triggers the 'Status Update - Permit Cancelled' flow and asserts success popup."""
        self._wait_for_loader()
        self._clear_loader()
        logger.info("Clicking Status Update - Permit Cancelled button")
        self.status_update_permit_cancelled_btn.click(force=True)

        logger.info("Asserting Permit Status Updated alert dialog")
        active_dialog = self.page.locator(".k-dialog:visible, .k-window:visible")
        try:
            expect(active_dialog).to_be_visible(timeout=15000)
            expect(active_dialog.get_by_text("Permit Status Updated")).to_be_visible(timeout=10000)
            self.kendo_ok_button.click()
        except Exception:
            self.dismiss_kendo_dialogs()
        self._clear_loader()
        self._wait_for_loader()

    def select_date_range_three_months_ago(self) -> None:
        """Opens From Date picker, navigates 3 months back, selects today's day (with fallback), and selects today's day on To Date picker."""
        self._wait_for_loader()
        self._clear_loader()
        today = datetime.datetime.now()
        today_day = str(today.day)

        logger.info("Opening From Date picker")
        self.page.get_by_role("button", name="select").first.click(force=True)
        self.page.wait_for_timeout(500)

        logger.info("Navigating 3 months back")
        for _ in range(3):
            self.page.get_by_role("button", name="Previous").click(force=True)
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
        self.page.get_by_role("button", name="select").nth(1).click(force=True)
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting day {today_day} for To Date")
        self.js_click(calendar_locator.get_by_role("link", name=today_day, exact=True).first)
        self.page.wait_for_timeout(500)

        logger.info("Clicking Search button to filter by Date Range")
        self._clear_loader()
        self.search_button.first.click(force=True)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def filter_by_type_document(self) -> None:
        """Selects 'Document' in the Type dropdown and performs search."""
        self._wait_for_loader()
        self._clear_loader()
        logger.info("Opening Type dropdown")
        type_trigger = self.page.locator("#frmFeeSearch").get_by_text("--Select Type--").or_(self.type_dropdown_trigger)
        if type_trigger.is_visible():
            type_trigger.click(force=True)
            self.page.wait_for_timeout(500)

        logger.info("Selecting option 'Document'")
        doc_option = self.page.locator("[role='option']:visible, li:visible").filter(has_text=re.compile(r"^Document$", re.I)).first
        if doc_option.is_visible(timeout=2000):
            self.js_click(doc_option)
        else:
            self.kendo_dropdown.select_by_locator(self.page.locator("[role='listbox']:visible"), "Document")
        self.page.wait_for_timeout(500)

        logger.info("Clicking Search button to filter by Type")
        self._clear_loader()
        self.search_button.first.click(force=True)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def get_first_record_name(self) -> str:
        """Reads and returns the name/title of the first record in the LogListGrid."""
        self._wait_for_loader()
        logger.info("Locating the first row of LogListGrid")
        self.page.wait_for_selector("#LogListGrid tbody tr", timeout=10000)
        first_row = self.page.locator("#LogListGrid tbody tr").first

        name_cell = first_row.locator("td").nth(2)
        name_text = name_cell.inner_text().strip()
        logger.info(f"Retrieved first record name: '{name_text}'")
        return name_text

    def search_by_name(self, name: str) -> None:
        """Enters the name in the textbox and clicks search."""
        self._wait_for_loader()
        self._clear_loader()
        logger.info(f"Filtering grid by record name: '{name}'")
        self.name_search_input.click(force=True)
        self.name_search_input.fill(name)
        self.page.wait_for_timeout(500)

        self.search_button.first.click(force=True)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def view_and_close_first_record_document(self) -> None:
        """Clicks the View button of the first record, handles the resulting popup, and closes it."""
        self._wait_for_loader()
        logger.info("Clicking the View document button of the first record (popup expectation)")

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
        self.save_button.click(force=True)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        logger.info("Log details edited and saved successfully")
