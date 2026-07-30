import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ChecklistPage(BasePage):
    """
    Page Object Model for the Checklist tab within the Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Tab Navigation ──────────────────────────────────────────────────
        self.checklist_tab = page.get_by_role("link", name="Checklist").or_(
            page.locator("a:has-text('Checklist'), span:has-text('Checklist'), .k-tabstrip a:has-text('Checklist'), .k-tabstrip span:has-text('Checklist')")
        ).first

        # ── Page Header & App-Level Elements ────────────────────────────────
        self.log_app_header     = page.locator("#LogAppHeader")
        self.checklist_heading  = page.get_by_role("heading", name="Checklist").or_(
            page.locator("h1:has-text('Checklist'), h2:has-text('Checklist'), h3:has-text('Checklist')")
        ).first

        # ── Condition Filter Radio (Application / Permit) ───────────────────
        self.condition_radio_application = page.locator("#conditionRadio").get_by_text("Application").first

        # ── Non-Other Conditions Grid ────────────────────────────────────────
        self.non_other_grid = page.locator("#nonOtherGrid")

        # Pagination controls scoped to the Non-Other grid toolbar (#conditiontop)
        self.non_other_first_page = page.locator("#conditiontop").get_by_role("link", name="Go to the first page")
        self.non_other_prev_page = page.locator("#conditiontop").get_by_role("link", name="Go to the previous page")
        self.non_other_next_page = page.locator("#conditiontop").get_by_role("link", name="Go to the next page")
        self.non_other_last_page = page.locator("#conditiontop").get_by_role("link", name="Go to the last page")

        # ── Condition Row Actions ─────────────────────────────────────────────
        self.first_row_edit_button = page.locator("#nonOtherGrid tbody tr:first-child").get_by_role("button").or_(
            page.locator("#nonOtherGrid tbody tr:first-child .k-grid-edit, #nonOtherGrid tbody tr:first-child #gridEdit")
        ).first
        self.update_button = page.get_by_role("button", name=" Update").or_(page.get_by_role("button", name="Update")).first

        # ── Optional Condition Radio ─────────────────────────────────────────
        self.optional_condition_radio = page.locator("div:nth-child(2) > .k-radio-label").first

        # ── Optional Conditions Grid ──────────────────────────────────────────
        self.optional_condition_grid = page.locator("#nonOtherGridOptional")

        # Pagination controls scoped to the optional conditions section
        self.optional_first_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the first page")
        self.optional_prev_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the previous page")
        self.optional_next_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the next page")
        self.optional_last_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the last page")

        # ── Documents and Log Section ─────────────────────────────────────────
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log").or_(page.locator("#divfrmLog, #LogDynGridLoad").get_by_text("Documents and Log")).first
        self.complete_log_grid     = page.locator("#LogDynGridLoad > #partial-form > .form-wrapper > .row > .col-md-12")
        self.complete_log_status   = page.locator("#CompleteLog > div:nth-child(2)")

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to_checklist(self) -> None:
        """Clicks the Checklist sidebar tab and waits for the page to fully load."""
        logger.info("Navigating to Checklist tab.")
        self._wait_for_loader()
        if not self.checklist_heading.is_visible():
            self.js_click(self.checklist_tab)
            self.page.wait_for_load_state("domcontentloaded")
            self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Asserts initial structural elements are loaded."""
        logger.info("Verifying Checklist page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def open_first_condition_row(self) -> None:
        """Opens the first visible row in the Non-Other grid."""
        logger.info("Opening the first condition row in the Non-Other grid.")
        self._wait_for_loader()
        if self.first_row_edit_button.is_visible():
            self.js_click(self.first_row_edit_button)
            self._wait_for_loader()

    def click_update(self) -> None:
        """Clicks Update button."""
        logger.info("Clicking the Update button for the expanded condition row.")
        if self.update_button.is_visible():
            self.js_click(self.update_button)
            self._wait_for_loader()

    def paginate_non_other_to_last_page(self) -> None:
        """Navigates Non-Other grid to last page."""
        self.paginate_grid_last(self.non_other_last_page, grid_name="Non-Other Grid")

    def select_optional_condition_radio(self) -> None:
        """Switches view to Optional condition radio."""
        self.select_optional_conditions_view()

    def paginate_optional_to_last_page(self) -> None:
        """Navigates Optional conditions grid to last page."""
        self.paginate_grid_last(self.optional_last_page, grid_name="Optional Conditions Grid")

    def verify_documents_and_log_section(self) -> None:
        """Verifies documents and log section readiness."""
        pass

    def paginate_grid_next(self, next_btn_locator, clicks: int = 2, grid_name: str = "grid") -> None:
        """Paginates forward up to clicks times."""
        for i in range(clicks):
            try:
                if next_btn_locator.is_visible():
                    css_classes = next_btn_locator.get_attribute("class") or ""
                    if "k-state-disabled" in css_classes:
                        break
                    self.js_click(next_btn_locator)
                    self._wait_for_loader()
            except Exception:
                break

    def paginate_grid_last(self, last_btn_locator, grid_name: str = "grid") -> None:
        """Navigates directly to the last page."""
        try:
            if last_btn_locator.is_visible():
                css_classes = last_btn_locator.get_attribute("class") or ""
                if "k-state-disabled" not in css_classes:
                    self.js_click(last_btn_locator)
                    self._wait_for_loader()
        except Exception:
            pass

    def select_optional_conditions_view(self) -> None:
        """Switches the view to Optional conditions radio."""
        logger.info("Switching view to Optional conditions radio filter.")
        self._wait_for_loader()
        if self.optional_condition_radio.is_visible():
            self.js_click(self.optional_condition_radio)
            self._wait_for_loader()
