import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LetterOfNoInterestPage(BasePage):
    """
    Page Object Model for Letter of No Interest in Staff Portal E-Permitting System.
    Automates navigation, 'Linked with Permit' checkbox toggling, dynamic searching
    (Route#, Block, Lot), opening 1st record in Edit mode, layout assertions, and saving.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation Locators ───────────────────────────────────────────────
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

        # ── Search & Filter Locators ──────────────────────────────────────────
        self.linked_with_permit_checkbox = page.get_by_text("Linked with Permit").or_(
            page.locator("label:has-text('Linked with Permit'), input[type='checkbox']")
        ).first

        self.refresh_button = page.get_by_role("button", name=re.compile(r"Refresh", re.I)).or_(
            page.locator("button:has-text('Refresh'), .btn:has-text('Refresh')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first

        # ── Grid Locators ─────────────────────────────────────────────────────
        self.grid_rows = page.locator(".k-grid tbody tr, table.k-selectable tbody tr, #gridLONI tbody tr")
        self.first_edit_button = page.locator("#gridEdit, .k-grid-edit, a.k-button:has(.k-i-edit), button:has(.fa-pencil), button.btn-edit, td a.k-button, td button").first

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
        """Toggles 'Linked with Permit' checkbox on and off with Refresh clicks per codegen steps."""
        logger.info("Testing 'Linked with Permit' checkbox toggle with Refresh.")
        self._wait_for_loader()

        if self.linked_with_permit_checkbox.is_visible():
            self.js_click(self.linked_with_permit_checkbox)
            if self.refresh_button.is_visible():
                self.js_click(self.refresh_button)
                self._wait_for_loader()
                self.page.wait_for_timeout(1000)

            self.js_click(self.linked_with_permit_checkbox)
            if self.refresh_button.is_visible():
                self.js_click(self.refresh_button)
                self._wait_for_loader()
                self.page.wait_for_timeout(1000)

    def search_by_first_record_route_block_lot(self) -> dict:
        """
        Dynamically extracts Route#, Block, and Lot from 1st row,
        fills search filter fields all at once, and clicks Refresh.
        """
        logger.info("Extracting Route#, Block, and Lot from 1st row dynamically.")
        self._wait_for_loader()

        route_val = ""
        block_val = ""
        lot_val = ""

        if self.grid_rows.count() > 0:
            row_cells = self.grid_rows.first.locator("td")

            # Route # is in 1st cell (e.g., "22" or "4")
            if row_cells.count() > 0:
                route_val = (row_cells.nth(0).text_content() or "").strip()

            # Block/Lot is in 3rd cell (e.g., "5.11/2.04" or "99.01/20")
            if row_cells.count() > 2:
                block_lot_text = (row_cells.nth(2).text_content() or "").strip()
                if "/" in block_lot_text:
                    parts = block_lot_text.split("/")
                    block_val = parts[0].strip()
                    lot_val = parts[1].split("&")[0].split(",")[0].strip()
                elif block_lot_text:
                    block_val = block_lot_text

        # Fallbacks if grid was empty
        if not route_val:
            route_val = "22"
        if not block_val:
            block_val = "5.11"
        if not lot_val:
            lot_val = "2.04"

        logger.info(f"Filling search inputs — Route#: '{route_val}', Block: '{block_val}', Lot: '{lot_val}'")

        # 1. Fill Route #
        route_inp = self.page.get_by_role("textbox", name=re.compile(r"Route", re.I)).or_(
            self.page.locator("#Route_No, #Route, input[name*='Route'], .form-wrapper input[type='text']")
        ).first
        if route_inp.count() > 0 and route_inp.is_visible():
            route_inp.click()
            route_inp.fill(route_val)
            route_inp.press("Tab")

        # 2. Fill Block
        block_inp = self.page.locator("#Block_No, #Block, input[name*='Block'], input[id*='Block']").first
        if block_inp.count() > 0 and block_inp.is_visible():
            block_inp.click()
            block_inp.fill(block_val)
            block_inp.press("Tab")

        # 3. Fill Lot
        lot_inp = self.page.locator("#Lot_No, #Lot, input[name*='Lot'], input[id*='Lot']").first
        if lot_inp.count() > 0 and lot_inp.is_visible():
            lot_inp.click()
            lot_inp.fill(lot_val)
            lot_inp.press("Tab")

        self.page.wait_for_timeout(500)

        # 4. Click Refresh button
        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()
            self.page.wait_for_timeout(2000)

        return {"route": route_val, "block": block_val, "lot": lot_val}

    def clear_search_and_refresh(self) -> None:
        """Clears search filter inputs and clicks Refresh to reload full grid."""
        logger.info("Clearing search filters and refreshing grid.")
        self._wait_for_loader()

        route_inp = self.page.get_by_role("textbox", name=re.compile(r"Route", re.I)).or_(
            self.page.locator("#Route_No, #Route, input[name*='Route'], .form-wrapper input[type='text']")
        ).first
        if route_inp.count() > 0 and route_inp.is_visible():
            route_inp.click()
            route_inp.fill("")
            route_inp.press("Tab")

        for inp in self.page.locator("input[name*='Block'], input[name*='Lot']").all():
            try:
                if inp.is_visible():
                    inp.fill("")
            except Exception:
                pass

        if self.refresh_button.is_visible():
            self.js_click(self.refresh_button)
            self._wait_for_loader()
            self.page.wait_for_timeout(1500)

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
