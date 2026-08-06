import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class WaiverPage(BasePage):
    """
    Page Object Model for Waiver tab in Staff Portal E-Permitting System.
    Provides automated methods for navigating to Waiver tab, adding waiver details,
    editing waivers, and validating waiver records in the grid.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.waiver_tab = page.get_by_role("link", name="Waiver").or_(
            page.locator("a:has-text('Waiver'), span:has-text('Waiver'), .k-tabstrip a:has-text('Waiver')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.waiver_heading = page.get_by_role("heading", name="Waiver").or_(
            page.locator("h1:has-text('Waiver'), h2:has-text('Waiver'), h3:has-text('Waiver')")
        ).first

        self.waiver_grid_container = page.locator("#div4319WaiverAppStaffFull > div:nth-child(3)").or_(
            page.locator("#div4319WaiverAppStaffFull .k-grid, #div4319WaiverAppStaffFull table")
        ).first

        # ── Action Buttons & Form Controls ────────────────────────────────────
        self.add_new_button = page.get_by_role("button", name=" Add New").or_(
            page.get_by_role("button", name="Add New")
        ).or_(
            page.locator("#btnAddNewWaiver, .btn:has-text('Add New')")
        ).first

        self.waiver_details_heading = page.get_by_role("heading", name="Waiver Details").or_(
            page.locator("h1:has-text('Waiver Details'), h2:has-text('Waiver Details'), h3:has-text('Waiver Details')")
        ).first

        self.waiver_details_text_container = page.get_by_text(re.compile(r"Waiver Details\s+Save\s+Cancel", re.I)).or_(
            page.locator("form:has-text('Waiver Details'), .form-wrapper:has-text('Waiver Details')")
        ).first

        self.text_placeholder1_input = page.locator("#Text_PlaceHolder1")
        self.comment_placeholder1_input = page.locator("#Comment_PlaceHolder1")
        self.choose_file_button = page.get_by_role("button", name="Choose File").first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(
            page.locator("button:has-text('Save'), input[type='submit'][value='Save']")
        ).first

        self.edit_waiver_button = page.locator("#editWaiver").or_(
            page.locator(".k-grid-edit, button:has-text('Edit'), a:has-text('Edit')")
        ).first

        self.partial_form_container = page.locator("#partial-form").nth(1).or_(
            page.locator("#partial-form, .form-wrapper")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_waiver(self) -> None:
        """Navigates to the Waiver tab."""
        logger.info("Navigating to Waiver tab.")
        self._wait_for_loader()
        if self.waiver_tab.is_visible():
            self.js_click(self.waiver_tab)
        else:
            self.page.evaluate("$('a:contains(\"Waiver\"), span:contains(\"Waiver\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Waiver page initial layout by asserting header, heading, and grid container visibility."""
        logger.info("Verifying Waiver initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.waiver_heading).to_be_visible(timeout=15000)
        expect(self.waiver_grid_container).to_be_visible(timeout=15000)

    def click_add_new_waiver(self) -> None:
        """Clicks 'Add New' button and verifies that Waiver Details section appears."""
        logger.info("Clicking 'Add New' button for Waiver.")
        self._wait_for_loader()
        if self.add_new_button.is_visible():
            self.js_click(self.add_new_button)
            self._wait_for_loader()

        expect(self.waiver_details_heading).to_be_visible(timeout=20000)

    def fill_waiver_details(self, text_val: str = "test", comment_val: str = "test") -> None:
        """Fills text placeholder and comment placeholder input fields in Waiver form."""
        logger.info(f"Filling Waiver details (Text: {text_val}, Comment: {comment_val}).")
        self._wait_for_loader()

        if self.text_placeholder1_input.is_visible():
            self.text_placeholder1_input.click()
            self.text_placeholder1_input.fill(text_val)

        if self.choose_file_button.is_visible():
            logger.info("Choose File button visible.")

        if self.comment_placeholder1_input.is_visible():
            self.comment_placeholder1_input.click()
            self.comment_placeholder1_input.fill(comment_val)

        self.select_all_kendo_dropdowns()
        self.set_all_datefields_to_current()

        # Best-effort: fill other empty text inputs or textareas within the visible waiver modal/dialog
        try:
            self.page.evaluate("""
                (txt) => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return;
                    var container = jq('.k-window:visible, [role="dialog"]:visible, #partial-form:visible').first();
                    if (!container || !container.length) container = jq('form:visible').first();
                    if (!container || !container.length) return;
                    container.find('input[type="text"], textarea').each(function() {
                        var $el = jq(this);
                        var id = ($el.attr('id') || '').toLowerCase();
                        var name = ($el.attr('name') || '').toLowerCase();
                        if (id.includes('date') || name.includes('date') || id.includes('time') || name.includes('time') || $el.is(':disabled')) return;
                        if (!$el.val() || $el.val().toString().trim() === '') {
                            $el.val(txt).trigger('input').trigger('change').trigger('blur');
                        }
                    });
                }
            """, comment_val)
        except Exception:
            pass

    def save_waiver(self) -> None:
        """Clicks Save button and asserts grid container is visible without validation errors."""
        logger.info("Saving Waiver record.")
        self._wait_for_loader()
        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()

        expect(self.waiver_grid_container).to_be_visible(timeout=15000)

    def edit_waiver(self) -> None:
        """Clicks #editWaiver button, verifies partial-form container, and saves changes."""
        logger.info("Editing existing Waiver record.")
        self._wait_for_loader()
        if self.edit_waiver_button.is_visible():
            self.js_click(self.edit_waiver_button)
            self._wait_for_loader()

        expect(self.partial_form_container).to_be_visible(timeout=15000)

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()

    def execute_waiver_codegen_flow(self, text_val: str = "test", comment_val: str = "test") -> None:
        """Executes full end-to-end codegen workflow for Waiver tab."""
        self.navigate_to_waiver()
        self.verify_initial_layout()
        self.click_add_new_waiver()
        self.fill_waiver_details(text_val=text_val, comment_val=comment_val)
        self.save_waiver()
        self.edit_waiver()
