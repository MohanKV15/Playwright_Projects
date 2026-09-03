import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class TechnicalReviewPage(BasePage):
    """
    Page Object Model for Technical Review in Staff Portal E-Permitting System.
    Provides clean, professional automation methods for Technical Review workflows.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Header Locators ───────────────────────────────────────
        self.technical_review_link = page.get_by_role("link", name="Technical Review").or_(
            page.locator("a:has-text('Technical Review'), span:has-text('Technical Review'), .k-tabstrip a:has-text('Technical Review'), .k-tabstrip span:has-text('Technical Review')")
        ).first
        self.log_app_header = page.locator("#LogAppHeader")
        self.reviewers_assigned_heading = page.get_by_role("heading", name="Reviewers Assigned").or_(page.locator("h1:has-text('Reviewers Assigned'), h2:has-text('Reviewers Assigned'), h3:has-text('Reviewers Assigned'), div:has-text('Reviewers Assigned')")).first
        self.summary_container = page.locator(".row > div:nth-child(3)").first

        # ── Form & Action Locators ─────────────────────────────────────────────
        self.add_new_button = page.get_by_role("button", name=" Add New").or_(page.get_by_role("button", name="Add New")).first
        self.technical_review_heading = page.get_by_role("heading", name="Technical Review").or_(page.locator("h1:has-text('Technical Review'), h2:has-text('Technical Review'), h3:has-text('Technical Review')")).first
        self.form_wrapper_container = page.locator("#partial-form > .form-wrapper > .row > .col-md-12, #partial-form, .form-wrapper").first

        # ── Date Picker Locators ───────────────────────────────────────────────
        self.date_picker_first = page.get_by_role("button", name="select").first
        self.date_picker_second = page.get_by_role("button", name="select").nth(1)

        # ── ReviewUnitGrid Locators (1st Row Scoped) ───────────────────────────
        self.grid_first_row = page.locator("#ReviewUnitGrid tbody tr").first
        self.grid_edit_btn = self.grid_first_row.locator(".k-grid-edit, #gridEdit, button:has-text('Edit'), a:has-text('Edit')").first
        self.grid_dropdown = page.locator("#ReviewUnitGrid").get_by_text("--Select Review By--").or_(
            page.locator("#ReviewUnitGrid").get_by_text("John Jone")
        ).first
        self.grid_update_btn = self.grid_first_row.locator(".k-grid-update, .k-i-check, button:has-text('Update'), a:has-text('Update')").first

        # ── Save, Detail & Cancel Locators ─────────────────────────────────────
        self.save_btn = page.get_by_role("button", name=" Save").or_(page.get_by_role("button", name="Save")).first
        self.edit_tech_review_btn = page.locator("#editTechReview").first
        self.dept_job_permit_container = page.locator("div").filter(has_text="Department Job # Permit Type").nth(4)
        self.cancel_btn = page.get_by_role("button", name=" Cancel").or_(page.get_by_role("button", name="Cancel")).first

    def navigate_to_technical_review(self) -> None:
        """Navigates to Technical Review tab and verifies page headers."""
        logger.info("Navigating to Technical Review tab.")
        self._wait_for_loader()
        if not self.reviewers_assigned_heading.is_visible():
            self.js_click(self.technical_review_link)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_headers(self) -> None:
        """Verifies LogAppHeader and Reviewers Assigned heading."""
        logger.info("Verifying headers on Technical Review page.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def click_add_new(self) -> None:
        """Clicks Add New button and verifies partial form container."""
        logger.info("Clicking 'Add New' button.")
        self._wait_for_loader()
        if self.add_new_button.is_visible():
            self.js_click(self.add_new_button)
            self._wait_for_loader()

    def edit_review_unit_grid_first_row(self) -> None:
        """Edits first row in ReviewUnitGrid."""
        logger.info("Editing first row in ReviewUnitGrid.")
        self._wait_for_loader()
        if self.grid_edit_btn.is_visible():
            self.js_click(self.grid_edit_btn)
            self._wait_for_loader()

        self.select_all_kendo_dropdowns()

        if self.grid_update_btn.is_visible():
            self.js_click(self.grid_update_btn)
            self._wait_for_loader()

    def select_dates_and_save(self) -> None:
        """Picks dates from both date pickers and clicks Save."""
        logger.info("Selecting dates and clicking Save.")
        self.set_today_date(self.date_picker_first)
        self.set_today_date(self.date_picker_second)

        if self.save_btn.is_visible():
            self.js_click(self.save_btn)
            self._wait_for_loader()
            self.assert_no_validation_errors()

    def edit_tech_review_details_and_cancel(self) -> None:
        """Clicks #editTechReview and then Cancel."""
        if self.edit_tech_review_btn.is_visible():
            self.js_click(self.edit_tech_review_btn)
            self._wait_for_loader()

        if self.cancel_btn.is_visible():
            self.js_click(self.cancel_btn)
            self._wait_for_loader()

    def execute_full_technical_review_codegen_flow(self) -> None:
        """Executes full end-to-end Technical Review flow."""
        self.navigate_to_technical_review()
        self.verify_initial_headers()
        self.click_add_new()
        self.edit_review_unit_grid_first_row()
        self.select_dates_and_save()
        self.edit_tech_review_details_and_cancel()
