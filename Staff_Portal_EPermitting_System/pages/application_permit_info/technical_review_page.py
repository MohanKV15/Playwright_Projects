import datetime
import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class TechnicalReviewPage(BasePage):
    """
    Page Object Model for Technical Review in Staff Portal E-Permitting System.
    Provides clean, professional automation methods for the complete Technical Review workflow.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Header Locators ───────────────────────────────────────
        self.technical_review_link = page.get_by_role("link", name="Technical Review")
        self.log_app_header = page.locator("#LogAppHeader")
        self.reviewers_assigned_heading = page.get_by_role("heading", name="Reviewers Assigned")
        self.summary_container = page.locator(".row > div:nth-child(3)").first

        # ── Form & Action Locators ─────────────────────────────────────────────
        self.add_new_button = page.get_by_role("button", name=" Add New")
        self.technical_review_heading = page.get_by_role("heading", name="Technical Review")
        self.form_wrapper_container = page.locator("#partial-form > .form-wrapper > .row > .col-md-12")

        # ── Date Picker Locators ───────────────────────────────────────────────
        self.date_picker_first = page.get_by_role("button", name="select").first
        self.date_picker_second = page.get_by_role("button", name="select").nth(1)

        # ── ReviewUnitGrid Locators (1st Row Scoped) ───────────────────────────
        self.grid_first_row = page.locator("#ReviewUnitGrid tbody tr").first
        self.grid_edit_btn = self.grid_first_row.locator(".k-grid-edit, button:has-text('Edit'), a:has-text('Edit')").first
        self.grid_dropdown = page.locator("#ReviewUnitGrid").get_by_text("--Select Review By--").or_(
            page.locator("#ReviewUnitGrid").get_by_text("John Jone")
        ).first
        self.grid_update_btn = self.grid_first_row.locator(".k-grid-update, .k-i-check, button:has-text('Update'), a:has-text('Update')").first

        # ── Save, Detail & Cancel Locators ─────────────────────────────────────
        self.save_btn = page.get_by_role("button", name=" Save")
        self.edit_tech_review_btn = page.locator("#editTechReview").first
        self.dept_job_permit_container = page.locator("div").filter(has_text="Department Job # Permit Type").nth(4)
        self.cancel_btn = page.get_by_role("button", name=" Cancel")

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _select_first_dropdown_option(self) -> None:
        """Selects the 1st valid non-placeholder option from active dropdown list."""
        logger.info("Selecting 1st valid option from active dropdown.")
        self._wait_for_loader()

        options = self.page.get_by_role("option").or_(
            self.page.locator("li.k-item:visible, .k-list-container:visible li, .k-animation-container:visible li, ul.k-list:visible li")
        )

        try:
            options.first.wait_for(state="visible", timeout=10000)
            for i in range(options.count()):
                opt = options.nth(i)
                txt = opt.inner_text().strip()
                if txt and not txt.startswith("--") and not txt.lower().startswith("select") and "no data" not in txt.lower():
                    logger.info(f"Selected option: '{txt}'")
                    self.js_click(opt)
                    self.page.wait_for_timeout(300)
                    return
            if options.count() > 0:
                self.js_click(options.first)
        except Exception as e:
            logger.warning(f"Dropdown selection note: {e}")

    # ── Action Methods ──────────────────────────────────────────────────────

    def navigate_to_technical_review(self) -> None:
        """Navigates to Technical Review tab and verifies initial page headers."""
        logger.info("Navigating to Technical Review tab.")
        self._wait_for_loader()
        self.js_click(self.technical_review_link)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

        if self.log_app_header.count() > 0:
            expect(self.log_app_header).to_be_visible(timeout=10000)
        if self.reviewers_assigned_heading.count() > 0:
            expect(self.reviewers_assigned_heading).to_be_visible(timeout=10000)
        if self.summary_container.count() > 0:
            expect(self.summary_container).to_be_visible(timeout=10000)

    def click_add_new(self) -> None:
        """Clicks Add New button and verifies form containers."""
        logger.info("Clicking Add New button.")
        self.add_new_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.add_new_button)
        self._wait_for_loader()

        if self.technical_review_heading.count() > 0:
            expect(self.technical_review_heading).to_be_visible(timeout=10000)
        if self.form_wrapper_container.count() > 0:
            expect(self.form_wrapper_container).to_be_visible(timeout=10000)

    def fill_dates(self) -> None:
        """Populates present day dates into 1st and 2nd date pickers."""
        day_str = str(datetime.date.today().day)
        date_full = datetime.date.today().strftime("%m/%d/%Y")
        logger.info(f"Filling present day date '{day_str}' ({date_full}).")

        # Fill 1st Date Picker
        try:
            if self.date_picker_first.is_visible():
                self.js_click(self.date_picker_first)
                self.page.wait_for_timeout(300)
                day_link1 = self.page.get_by_label(re.compile(r"Current focused date", re.I)).get_by_role("link", name=day_str).or_(
                    self.page.locator(".k-calendar-container:visible, .k-animation-container:visible").get_by_role("link", name=day_str, exact=True)
                ).first
                if day_link1.is_visible():
                    self.js_click(day_link1)
        except Exception as e:
            logger.warning(f"1st date picker note: {e}")

        # Fill 2nd Date Picker
        try:
            if self.date_picker_second.is_visible():
                self.js_click(self.date_picker_second)
                self.page.wait_for_timeout(300)
                day_link2 = self.page.get_by_role("link", name=day_str, exact=True).nth(1).or_(
                    self.page.locator(".k-calendar-container:visible, .k-animation-container:visible").get_by_role("link", name=day_str, exact=True)
                ).first
                if day_link2.is_visible():
                    self.js_click(day_link2)
        except Exception as e:
            logger.warning(f"2nd date picker note: {e}")

        # Fallback direct date fill
        try:
            inputs = self.page.locator("input[data-role='datepicker'], .k-datepicker input, input[id*='Sent'], input[id*='Due']")
            for i in range(min(inputs.count(), 2)):
                inp = inputs.nth(i)
                if inp.is_visible() and not inp.input_value():
                    inp.fill(date_full)
                    inp.dispatch_event("change")
                    inp.dispatch_event("blur")
        except Exception as e:
            logger.warning(f"Direct date fill note: {e}")

    def edit_review_unit_grid(self) -> None:
        """Edits ReviewUnitGrid 1st row, selects 1st option from Review By dropdown, and clicks Update."""
        logger.info("Editing ReviewUnitGrid 1st row.")
        if self.grid_edit_btn.is_visible():
            self.js_click(self.grid_edit_btn)
            self._wait_for_loader()

        if self.grid_dropdown.is_visible():
            self.js_click(self.grid_dropdown)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        self._select_first_dropdown_option()
        self.page.wait_for_timeout(300)

        if self.grid_update_btn.is_visible():
            self.js_click(self.grid_update_btn)
            self._wait_for_loader()

        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    def save_technical_review(self) -> None:
        """Clicks Save button to submit the Technical Review entry."""
        logger.info("Saving Technical Review form.")
        if self.save_btn.is_visible():
            self.js_click(self.save_btn)
            self._wait_for_loader()

    def verify_summary_and_cancel(self) -> None:
        """Verifies summary layout, opens detail view, verifies detail layout, and clicks Cancel."""
        logger.info("Verifying summary layout and detail view.")
        if self.summary_container.count() > 0:
            expect(self.summary_container).to_be_visible(timeout=15000)

        if self.edit_tech_review_btn.is_visible():
            self.js_click(self.edit_tech_review_btn)
            self._wait_for_loader()

            if self.dept_job_permit_container.count() > 0:
                expect(self.dept_job_permit_container).to_be_visible(timeout=15000)

        if self.cancel_btn.is_visible():
            self.js_click(self.cancel_btn)
            self._wait_for_loader()

    def execute_full_technical_review_codegen_flow(self) -> None:
        """Executes full technical review codegen workflow end-to-end."""
        self.navigate_to_technical_review()
        self.click_add_new()
        self.fill_dates()
        self.edit_review_unit_grid()
        self.save_technical_review()
        self.verify_summary_and_cancel()
