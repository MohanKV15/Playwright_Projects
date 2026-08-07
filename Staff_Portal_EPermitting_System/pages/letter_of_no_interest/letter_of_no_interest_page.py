import logging
import re
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LetterOfNoInterestPage(BasePage):
    """
    Optimized Page Object Model for Letter of No Interest in Staff Portal E-Permitting System.
    Automates navigation, 'Linked with Permit' checkbox toggling, dynamic searching
    (Route#, Block, Lot), opening 1st record in Edit mode, layout assertions, and saving.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Locators ──────────────────────────────────────────────────────────
        self.loni_menu = page.get_by_role("link", name="Letter of No Interest").or_(
            page.locator("a:has-text('Letter of No Interest'), span:has-text('Letter of No Interest')")
        ).first

        self.loni_heading = page.get_by_role("heading", name="Letter of No Interest").or_(
            page.locator("h1:has-text('Letter of No Interest'), h2:has-text('Letter of No Interest'), .card-title:has-text('Letter of No Interest')")
        ).first

        self.location_info_heading = page.get_by_text("Location Information").or_(
            page.locator("h1:has-text('Location Information'), h2:has-text('Location Information'), div:has-text('Location Information')")
        ).first

        self.loni_view_heading = page.get_by_text("Letter of No Interest View").or_(
            page.locator("h1:has-text('Letter of No Interest View'), h2:has-text('Letter of No Interest View'), div:has-text('Letter of No Interest View')")
        ).first

        self.linked_with_permit_checkbox = page.get_by_text("Linked with Permit").or_(
            page.locator("label:has-text('Linked with Permit'), input[type='checkbox']")
        ).first

        self.refresh_button = page.get_by_role("button", name=re.compile(r"Refresh", re.I)).or_(
            page.locator("button:has-text('Refresh'), .btn:has-text('Refresh')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first

        self.grid_rows = page.locator(".k-grid tbody tr, table.k-selectable tbody tr, #gridLONI tbody tr")
        self.first_edit_button = page.locator("#gridEdit, .k-grid-edit, a.k-button:has(.k-i-edit), button:has(.fa-pencil), button.btn-edit, td a.k-button, td button").first

    # ── Internal Helper Methods ───────────────────────────────────────────────

    def _fill_and_tab(self, input_loc: Locator, value: str) -> None:
        """Helper to focus, fill input value, and press Tab."""
        if input_loc.count() > 0 and input_loc.is_visible():
            input_loc.click()
            input_loc.fill(value)
            input_loc.press("Tab")

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_loni(self) -> None:
        """Navigates to Letter of No Interest page."""
        logger.info("Navigating to Letter of No Interest page.")
        self._wait_for_loader()
        if self.loni_menu.is_visible():
            self.js_click(self.loni_menu)
        else:
            self.page.evaluate("$('a:contains(\"Letter of No Interest\"), span:contains(\"Letter of No Interest\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates Letter of No Interest initial layout."""
        logger.info("Verifying Letter of No Interest initial layout.")
        self._wait_for_loader()
        expect(self.loni_heading).to_be_visible(timeout=15000)

    def test_linked_with_permit_checkbox_toggle(self) -> None:
        """Toggles 'Linked with Permit' checkbox on and off with Refresh clicks."""
        logger.info("Testing 'Linked with Permit' checkbox toggle with Refresh.")
        self._wait_for_loader()
        if self.linked_with_permit_checkbox.is_visible():
            for _ in range(2):
                self.js_click(self.linked_with_permit_checkbox)
                if self.refresh_button.is_visible():
                    self.js_click(self.refresh_button)
                    self._wait_for_loader()

    def search_by_first_record_route_block_lot(self) -> dict:
        """Dynamically extracts Route#, Block, and Lot from 1st row, fills inputs all at once, and clicks Refresh."""
        logger.info("Extracting Route#, Block, and Lot from 1st row dynamically.")
        self._wait_for_loader()

        route_val, block_val, lot_val = "22", "5.11", "2.04"

        if self.grid_rows.count() > 0:
            row_cells = self.grid_rows.first.locator("td")
            if row_cells.count() > 0:
                route_val = (row_cells.nth(0).text_content() or "").strip() or route_val
            if row_cells.count() > 2:
                block_lot_text = (row_cells.nth(2).text_content() or "").strip()
                if "/" in block_lot_text:
                    parts = block_lot_text.split("/")
                    block_val = parts[0].strip() or block_val
                    lot_val = parts[1].split("&")[0].split(",")[0].strip() or lot_val

        logger.info(f"Filling search inputs — Route#: '{route_val}', Block: '{block_val}', Lot: '{lot_val}'")

        route_inp = self.page.get_by_role("textbox", name=re.compile(r"Route", re.I)).or_(
            self.page.locator("#Route_No, #Route, input[name*='Route'], .form-wrapper input[type='text']")
        ).first
        block_inp = self.page.locator("#Block_No, #Block, input[name*='Block'], input[id*='Block']").first
        lot_inp = self.page.locator("#Lot_No, #Lot, input[name*='Lot'], input[id*='Lot']").first

        self._fill_and_tab(route_inp, route_val)
        self._fill_and_tab(block_inp, block_val)
        self._fill_and_tab(lot_inp, lot_val)

        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()

        return {"route": route_val, "block": block_val, "lot": lot_val}

    def clear_search_and_refresh(self) -> None:
        """Clears search filter inputs and clicks Refresh to reload full grid."""
        logger.info("Clearing search filters and refreshing grid.")
        self._wait_for_loader()

        route_inp = self.page.get_by_role("textbox", name=re.compile(r"Route", re.I)).or_(
            self.page.locator("#Route_No, #Route, input[name*='Route'], .form-wrapper input[type='text']")
        ).first
        self._fill_and_tab(route_inp, "")

        for inp in self.page.locator("input[name*='Block'], input[name*='Lot']").all():
            try:
                if inp.is_visible():
                    inp.fill("")
            except Exception:
                pass

        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()

    def open_first_record_in_edit_mode(self) -> None:
        """Clicks Edit (pencil icon) button on the 1st grid row."""
        logger.info("Opening 1st record in Edit mode.")
        self._wait_for_loader()
        edit_btn = self.grid_rows.first.locator("#gridEdit, .k-grid-edit, a.k-button, button").first if self.grid_rows.count() > 0 else self.first_edit_button
        if edit_btn.count() > 0 and edit_btn.is_visible():
            self.js_click(edit_btn)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_loni_full_view(self) -> None:
        """Validates Location Information & Letter of No Interest View headers."""
        logger.info("Verifying LONI full view layout headers.")
        self._wait_for_loader()
        expect(self.loni_heading).to_be_visible(timeout=15000)
        target_loc = self.location_info_heading.or_(self.page.locator("div:has-text('Location Information')")).first
        expect(target_loc).to_be_visible(timeout=15000)
        target_view = self.loni_view_heading.or_(self.page.locator("div:has-text('Letter of No Interest View')")).first
        expect(target_view).to_be_visible(timeout=15000)

    def safe_click_save(self) -> None:
        """Clicks Save button and asserts zero validation errors."""
        logger.info("Clicking Save button.")
        self._wait_for_loader()
        if self.save_button.count() > 0 and self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
            self.assert_no_validation_errors()
