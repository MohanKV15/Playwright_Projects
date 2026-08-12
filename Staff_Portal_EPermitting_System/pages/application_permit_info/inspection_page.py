import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class InspectionPage(BasePage):
    """
    Page Object Model for Inspection tab & Inspection Review workflow in Staff Portal E-Permitting System.
    Provides automated methods to handle inspection navigation, form details, report generation,
    and adding/verifying inspection reviews.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.inspection_tab = page.get_by_role("link", name="Inspection").or_(
            page.locator("a:has-text('Inspection'), span:has-text('Inspection'), .k-tabstrip a:has-text('Inspection')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")

        # ── Form Inputs & Buttons ─────────────────────────────────────────────
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.locator(
            "button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save'], a:has-text('Save'), .btn:has-text('Save')"
        ).first

        # ── Inspection Review Locators ───────────────────────────────────────
        self.add_new_button = page.get_by_role("button", name=re.compile(r"Add New", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Add New", re.I))
        ).or_(
            page.locator("#btnAddNewReview, #btnAddNew, a:has-text('Add New'), button:has-text('Add New'), .btn:has-text('Add New')")
        ).first

        self.review_modal_title = page.locator("#div4319InspectionReviewStaffAdd_wnd_title").or_(
            page.locator(".k-window-title:has-text('Add/Edit Inspection Review')")
        ).first

        self.review_modal_dialog = page.get_by_role("dialog", name="Add/Edit Inspection Review").or_(
            page.locator("[role='dialog']:visible")
        ).first

        self.submit_review_button = page.locator("#btnReviewSubmit").or_(
            page.locator("button:has-text('Submit'), input[type='submit'][value='Submit']")
        ).first

    def select_all_kendo_dropdowns(self) -> None:
        """Selects 1st valid option for all Kendo dropdowns by delegating to KendoControls."""
        super().select_all_kendo_dropdowns()

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_inspection(self) -> None:
        """Navigates to the Inspection tab."""
        logger.info("Navigating to Inspection tab.")
        self._wait_for_loader()
        if self.inspection_tab.is_visible():
            self.js_click(self.inspection_tab)
        else:
            self.page.evaluate("$('a:contains(\"Inspection\"), span:contains(\"Inspection\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Inspection page initial layout by ensuring application header is visible."""
        logger.info("Verifying Inspection initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_inspection_details(self, comments: str = "") -> None:
        """Fills inspection form comments, selects dropdown options, sets current dates, and saves."""
        logger.info("Filling and saving Inspection form details.")
        self._wait_for_loader()
        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)

        # Select all required Kendo dropdown options and populate date fields
        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        # Save inspection details and assert no validation errors
        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()

    def generate_inspection_reports(self) -> None:
        """Triggers inspection report generation if available on page."""
        logger.info("Generating inspection reports if available.")
        self._wait_for_loader()
        gen_btn = self.page.locator(
            "button:has-text('Generate'), input[type='button'][value*='Generate'], input[type='submit'][value*='Generate']"
        ).first
        if gen_btn.is_visible():
            self.js_click(gen_btn)
            self._wait_for_loader()

    def verify_add_new_review_modal_opened(self) -> None:
        """Validates that the Add/Edit Inspection Review modal dialog has opened."""
        candidates = [
            self.page.locator("#div4319InspectionReviewStaffAdd_wnd_title"),
            self.review_modal_title,
            self.page.locator("#btnReviewSubmit"),
            self.review_modal_dialog,
            self.page.locator("[role='dialog']:visible"),
        ]

        for loc in candidates:
            try:
                if loc.count() > 0 and loc.is_visible():
                    return
            except Exception:
                continue

        raise AssertionError("Add New inspection review modal did not open after clicking the button.")

    def add_inspection_review(self, comments: str = "") -> None:
        """
        Executes workflow to add a new Inspection Review entry:
        1. Click 'Add New' button to open review modal dialog.
        2. Verify modal title and dialog container visibility.
        3. Fill form controls (dropdowns, dates, radios/checkboxes, comments).
        4. Submit the review form and verify grid updates.
        """
        logger.info("Adding new Inspection Review.")
        self._wait_for_loader()

        if self.add_new_button.count() > 0 and self.add_new_button.is_visible():
            self.js_click(self.add_new_button)
        else:
            self.page.evaluate("$('#btnAddNewReview, #btnAddNew, a:contains(\"Add New\"), button:contains(\"Add New\")').first().click()")

        self._wait_for_loader()
        self.page.wait_for_timeout(500)

        # Confirm modal is open and visible
        self.verify_add_new_review_modal_opened()

        # Select first valid option for all Kendo dropdowns in modal
        self.select_all_kendo_dropdowns()

        # Fill date fields with current date
        self.set_all_datefields_to_current()

        # Select radio buttons and checkboxes within modal
        self.page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('.k-window:visible input[type="radio"], [role="dialog"]:visible input[type="radio"], .form-check input[type="radio"]').first().prop("checked", true).trigger("change");
                jq('.k-window:visible input[type="checkbox"], [role="dialog"]:visible input[type="checkbox"], .form-check input[type="checkbox"]').prop("checked", true).trigger("change");
            }
        """)

        # Enter review comments if provided
        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)

        # Click Submit button to submit review
        submit_btn = self.page.locator("#btnReviewSubmit")
        if submit_btn.count() > 0 and submit_btn.is_visible():
            self.js_click(submit_btn)
        elif self.submit_review_button.is_visible():
            self.js_click(self.submit_review_button)

        self._wait_for_loader()
        self.assert_no_validation_errors()

        # Verify inspection review grid is visible and contains records
        self.verify_inspection_review_added()

    def verify_inspection_review_added(self) -> None:
        """
        Verifies that the Inspection Review record has been saved and is displayed in the grid table.
        Asserts grid visibility and presence of record rows.
        """
        logger.info("Verifying saved Inspection Review entry in grid.")
        self._wait_for_loader()

        grid_table = self.page.locator("#InspectionReviewMainTable, #div4319InspectionReviewStaff .k-grid table, #div4319InspectionReviewStaff .k-grid").first
        expect(grid_table).to_be_visible(timeout=15000)

        rows = self.page.locator("#InspectionReviewMainTable tbody tr, #div4319InspectionReviewStaff .k-grid tbody tr")
        expect(rows.first).to_be_visible(timeout=15000)
        logger.info(f"Verified Inspection Review grid records present (Found {rows.count()} rows).")

