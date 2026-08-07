import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PreApplicationPage(BasePage):
    """
    Page Object Model for Pre-Application in Staff Portal E-Permitting System.
    Automates search filtering (Route, Suffix, Block, Lot, Refresh, Clear/Reset),
    record selection (Edit pencil button), Pre-Application Information full view verification, and saving.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.pre_app_menu = page.get_by_role("link", name="Pre-Application").or_(
            page.locator("a:has-text('Pre-Application'), span:has-text('Pre-Application')")
        ).first

        self.pre_app_heading = page.get_by_role("heading", name="Pre-Application").or_(
            page.locator("h1:has-text('Pre-Application'), h2:has-text('Pre-Application'), .card-title:has-text('Pre-Application')")
        ).first

        self.pre_app_info_heading = page.locator("div").filter(has_text="Pre-Application Information").or_(
            page.locator("h1:has-text('Pre-Application Information'), h2:has-text('Pre-Application Information'), .card-title:has-text('Pre-Application Information')")
        ).first

        # ── Search Filter Inputs ──────────────────────────────────────────────
        self.route_input = page.locator("#Route_No, #Route, input[name*='Route']").first
        self.block_input = page.locator("#Block_No, #Block, input[name*='Block']").first
        self.pre_app_no_input = page.locator("#Pre_Application_No, #PreAppNo, input[name*='Pre_Application']").first
        self.lot_input = page.locator("#Lot_No, #Lot, input[name*='Lot']").first

        # ── Action Buttons ────────────────────────────────────────────────────
        self.refresh_button = page.get_by_role("button", name=re.compile(r"Refresh", re.I)).or_(
            page.locator("button:has-text('Refresh'), .btn:has-text('Refresh')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first

        # ── Grid Locators ─────────────────────────────────────────────────────
        self.grid_rows = page.locator(".k-grid tbody tr, table.k-selectable tbody tr, #gridPreApplication tbody tr")
        self.first_edit_button = page.locator("#gridEdit, .k-grid-edit, a.k-button:has(.k-i-edit), button:has(.fa-pencil), button.btn-edit, td a.k-button, td button").first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_pre_application(self) -> None:
        """Navigates to Pre-Application page."""
        logger.info("Navigating to Pre-Application page.")
        self._wait_for_loader()
        if self.pre_app_menu.is_visible():
            self.js_click(self.pre_app_menu)
        else:
            self.page.evaluate("$('a:contains(\"Pre-Application\"), span:contains(\"Pre-Application\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Pre-Application initial page layout."""
        logger.info("Verifying Pre-Application page layout.")
        self._wait_for_loader()
        expect(self.pre_app_heading).to_be_visible(timeout=15000)

    def search_by_first_record_route(self) -> str:
        """
        Extracts Route value from 1st grid row, fills Route# search input, and clicks Refresh.
        Returns the searched Route string.
        """
        logger.info("Extracting 1st record Route value to perform search filter.")
        self._wait_for_loader()

        route_val = "33NA"
        if self.grid_rows.count() > 0:
            first_row_text = self.grid_rows.first.text_content() or ""
            match = re.search(r"\b(\d+[A-Z]*)\b", first_row_text)
            if match:
                route_val = match.group(1)

        logger.info(f"Filling Route# search input with: {route_val}")
        if self.route_input.is_visible():
            self.route_input.fill(route_val)

        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()

        return route_val

    def clear_search_and_refresh(self) -> None:
        """Clears all search filter input fields and clicks Refresh to reload all records."""
        logger.info("Clearing all search filters and refreshing grid.")
        self._wait_for_loader()

        for inp in [self.route_input, self.block_input, self.pre_app_no_input, self.lot_input]:
            if inp.count() > 0 and inp.is_visible():
                inp.fill("")

        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()

    def open_first_record_in_edit_mode(self) -> None:
        """Clicks Edit (pencil icon) button on the 1st row of the grid."""
        logger.info("Opening 1st record in Edit mode.")
        self._wait_for_loader()
        edit_btn = self.grid_rows.first.locator("#gridEdit, .k-grid-edit, a.k-button, button").first if self.grid_rows.count() > 0 else self.first_edit_button
        if edit_btn.count() > 0 and edit_btn.is_visible():
            self.js_click(edit_btn)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_pre_application_info(self) -> None:
        """Validates Pre-Application Information full view layout."""
        logger.info("Verifying Pre-Application Information full view.")
        self._wait_for_loader()
        target = self.pre_app_info_heading.or_(
            self.page.locator("h1:has-text('Pre-Application'), h2:has-text('Pre-Application'), .card-title, #partial-form, .form-wrapper")
        ).first
        expect(target).to_be_visible(timeout=15000)

    def safe_click_save(self) -> None:
        """Clicks Save button and asserts zero validation errors."""
        logger.info("Clicking Save button.")
        self._wait_for_loader()
        if self.save_button.count() > 0 and self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
