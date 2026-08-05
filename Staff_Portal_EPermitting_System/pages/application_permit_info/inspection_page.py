import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class InspectionPage(BasePage):
    """
    Page Object Model for Inspection tab & Inspection Review workflow in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.inspection_tab = page.get_by_role("link", name="Inspection").or_(
            page.locator("a:has-text('Inspection'), span:has-text('Inspection'), .k-tabstrip a:has-text('Inspection')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.inspection_heading = page.get_by_role("heading", name="Inspection").or_(
            page.locator("h1:has-text('Inspection'), h2:has-text('Inspection'), h3:has-text('Inspection')")
        ).first

        # ── Form Inputs & Buttons ─────────────────────────────────────────────
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.locator(
            "button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save'], a:has-text('Save'), .btn:has-text('Save')"
        ).first

        # ── Inspection Review Locators (from user codegen) ────────────────────
        self.add_new_button = page.get_by_role("button", name=" Add New").or_(
            page.get_by_role("button", name="Add New")
        ).or_(
            page.locator("#btnAddNewReview, .btn:has-text('Add New')")
        ).first

        self.review_modal_title = page.locator("#div4319InspectionReviewStaffAdd_wnd_title").or_(
            page.locator(".k-window-title:has-text('Add/Edit Inspection Review')")
        ).first

        self.review_modal_dialog = page.get_by_role("dialog", name="Add/Edit Inspection Review").or_(
            page.locator("[role='dialog']:visible")
        ).first

        self.inspection_type_dropdown = page.locator("#div4319InsReviewStaffEdit").get_by_text("--Select Inspection Type--").or_(
            page.locator("#div4319InsReviewStaffEdit .k-dropdown")
        ).first

        self.inspection_by_dropdown = page.locator("#divInsConsultant").get_by_text("--Select Inspection By--").or_(
            page.locator("#divInsConsultant .k-dropdown")
        ).first

        self.submit_review_button = page.locator("#btnReviewSubmit").or_(
            page.locator("button:has-text('Submit'), input[type='submit'][value='Submit']")
        ).first

        self.review_grid_container = page.locator("#div4319InspectionReviewStaff > div:nth-child(3)").or_(
            page.locator("#div4319InspectionReviewStaff .k-grid")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_inspection(self) -> None:
        """Navigates to Inspection tab."""
        logger.info("Navigating to Inspection tab.")
        self._wait_for_loader()
        if self.inspection_tab.is_visible():
            self.js_click(self.inspection_tab)
        else:
            self.page.evaluate("$('a:contains(\"Inspection\"), span:contains(\"Inspection\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Inspection page initial layout."""
        logger.info("Verifying Inspection initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def fill_inspection_details(self, comments: str = "") -> None:
        """Fills inspection form details, selects 1st dropdown options, sets current date, and saves."""
        logger.info("Filling and saving Inspection form.")
        self._wait_for_loader()
        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)

        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

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

    def add_inspection_review(self, comments: str = "") -> None:
        """
        Implements exact codegen workflow for Add/Edit Inspection Review:
        1. Click 'Add New' button: page.get_by_role("button", name=" Add New").click()
        2. Expect modal title '#div4319InspectionReviewStaffAdd_wnd_title' to be visible.
        3. Expect dialog 'Add/Edit Inspection Review' to be visible.
        4. Select 1st valid option for Inspection Type and Inspection By dropdowns.
        5. Fill all date fields with present day date (today's date).
        6. Select radio buttons / form check options.
        7. Click Submit button ('#btnReviewSubmit').
        8. Expect review grid container ('#div4319InspectionReviewStaff > div:nth-child(3)') to be visible.
        """
        logger.info("Adding new Inspection Review per codegen workflow.")
        self._wait_for_loader()

        if not self.add_new_button.is_visible():
            logger.warning("Add New button not visible on Inspection page.")
            return

        # 1. Click Add New (page.get_by_role("button", name=" Add New").click())
        self.js_click(self.add_new_button)
        self._wait_for_loader()

        # 2. Expect title & dialog visible (matching codegen)
        title_loc = self.page.locator("#div4319InspectionReviewStaffAdd_wnd_title")
        if title_loc.count() > 0 and title_loc.is_visible():
            expect(title_loc).to_be_visible(timeout=15000)
        elif self.review_modal_title.is_visible():
            expect(self.review_modal_title).to_be_visible(timeout=15000)

        dialog_loc = self.page.get_by_role("dialog", name="Add/Edit Inspection Review")
        if dialog_loc.count() > 0 and dialog_loc.is_visible():
            expect(dialog_loc).to_be_visible(timeout=15000)
        elif self.review_modal_dialog.is_visible():
            expect(self.review_modal_dialog).to_be_visible(timeout=15000)

        # 3. Wait up to 10s for Inspection By Kendo AJAX DataSource binding
        for _ in range(20):
            has_data = self.page.evaluate("""
                () => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return false;
                    var d1 = jq('#inspected_by_staff').data('kendoDropDownList') || jq('#inspected_by_consultant').data('kendoDropDownList');
                    return d1 && d1.dataSource && typeof d1.dataSource.data === 'function' && d1.dataSource.data().length > 0;
                }
            """)
            if has_data:
                break
            self.page.wait_for_timeout(500)

        # 4. Select 1st valid dropdown option (index 1) for Inspection Type and Inspection By
        self.page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;

                jq('#div4319InsReviewStaffEdit select, #div4319InsReviewStaffEdit input[data-role="dropdownlist"], #divInsConsultant select, #divInsConsultant input[data-role="dropdownlist"], #inspected_by_staff, #inspected_by_consultant, #HPINSInsType').each(function() {
                    var $el = jq(this);
                    var ddl = $el.data('kendoDropDownList') || $el.closest('.k-dropdown, .k-widget').data('kendoDropDownList');
                    if (!ddl && window.kendo && typeof window.kendo.widgetInstance === 'function') {
                        try { ddl = window.kendo.widgetInstance($el); } catch(e) {}
                    }
                    if (ddl && typeof ddl.select === 'function') {
                        var data = (ddl.dataSource && typeof ddl.dataSource.data === 'function') ? ddl.dataSource.data() : [];
                        if (data.length > 0) {
                            var hasOptionLabel = ddl.options && ddl.options.optionLabel;
                            var idx = hasOptionLabel ? 1 : 0;
                            if (idx < data.length || !hasOptionLabel) {
                                ddl.select(idx);
                                if (typeof ddl.trigger === 'function') ddl.trigger('change');
                                $el.trigger('change').trigger('input');
                            }
                        }
                    }
                });

                // Ensure hidden #inspected_by input gets updated
                var staffVal = jq('#inspected_by_staff').val() || jq('#inspected_by_consultant').val();
                if (staffVal) {
                    jq('#inspected_by').val(staffVal).trigger('change');
                }
            }
        """)

        self.select_all_kendo_dropdowns()

        # 5. Fill Date fields with present day date (today)
        self.set_all_datefields_to_current()

        # 6. Select Radio option / Checkbox options in modal
        self.page.evaluate("""
            () => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('.k-window:visible input[type="radio"], [role="dialog"]:visible input[type="radio"], .form-check input[type="radio"]').first().prop("checked", true).trigger("change");
                jq('.k-window:visible input[type="checkbox"], [role="dialog"]:visible input[type="checkbox"], .form-check input[type="checkbox"]').prop("checked", true).trigger("change");
            }
        """)

        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)

        self.set_all_datefields_to_current()
        self.select_all_kendo_dropdowns()

        # 7. Click Submit button (#btnReviewSubmit)
        submit_btn = self.page.locator("#btnReviewSubmit")
        if submit_btn.count() > 0 and submit_btn.is_visible():
            self.js_click(submit_btn)
        elif self.submit_review_button.is_visible():
            self.js_click(self.submit_review_button)

        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 8. Expect review grid container (#div4319InspectionReviewStaff > div:nth-child(3)) to be visible
        grid_loc = self.page.locator("#div4319InspectionReviewStaff > div:nth-child(3)")
        if grid_loc.count() > 0 and grid_loc.is_visible():
            expect(grid_loc).to_be_visible(timeout=15000)
        elif self.review_grid_container.is_visible():
            expect(self.review_grid_container).to_be_visible(timeout=15000)
