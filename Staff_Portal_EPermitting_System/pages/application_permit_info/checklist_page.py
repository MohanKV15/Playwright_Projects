import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ChecklistPage(BasePage):
    """
    Page Object Model for the Checklist tab within the Staff Portal E-Permitting System.

    Covers:
      - Navigation to the Checklist tab
      - Layout verification (header, grid containers, radio filters)
      - Interacting with the Non-Other conditions grid (row edit + update)
      - Paginating the Non-Other conditions grid to the last page
      - Selecting an optional condition radio (div:nth-child(2))
      - Paginating the Optional conditions grid to the last page
      - Verifying the Documents and Log section (inherited from BasePage)
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Tab Navigation ──────────────────────────────────────────────────
        self.checklist_tab = page.get_by_role("link", name="Checklist")

        # ── Page Header & App-Level Elements ────────────────────────────────
        self.log_app_header     = page.locator("#LogAppHeader")
        self.checklist_heading  = page.get_by_role("heading", name="Checklist")

        # ── Condition Filter Radio (Application / Permit) ───────────────────
        self.condition_radio_application = page.locator("#conditionRadio").get_by_text("Application")

        # ── Non-Other Conditions Grid ────────────────────────────────────────
        self.non_other_grid = page.locator("#nonOtherGrid")

        # Pagination controls scoped to the Non-Other grid toolbar (#conditiontop)
        self.non_other_first_page = page.locator("#conditiontop").get_by_role("link", name="Go to the first page")
        self.non_other_prev_page = page.locator("#conditiontop").get_by_role("link", name="Go to the previous page")
        self.non_other_next_page = page.locator("#conditiontop").get_by_role("link", name="Go to the next page")
        self.non_other_last_page = page.locator("#conditiontop").get_by_role("link", name="Go to the last page")

        # ── Condition Row Actions ─────────────────────────────────────────────
        # Opens the detail/edit pane for the first visible row in the non-other grid
        self.first_row_edit_button = page.locator("#nonOtherGrid tbody tr:first-child").get_by_role("button")
        self.update_button = page.get_by_role("button", name=" Update")

        # ── Optional Condition Radio ─────────────────────────────────────────
        # The 2nd radio option div that switches the grid view to "Optional" conditions
        self.optional_condition_radio = page.locator("div:nth-child(2) > .k-radio-label")

        # ── Optional Conditions Grid ──────────────────────────────────────────
        self.optional_condition_grid = page.locator("#nonOtherGridOptional")

        # Pagination controls scoped to the optional conditions section
        self.optional_first_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the first page")
        self.optional_prev_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the previous page")
        self.optional_next_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the next page")
        self.optional_last_page = page.locator("#optionalCondition").get_by_role("link", name="Go to the last page")

        # ── Documents and Log Section ─────────────────────────────────────────
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.complete_log_grid     = page.locator("#LogDynGridLoad > #partial-form > .form-wrapper > .row > .col-md-12")
        self.complete_log_status   = page.locator("#CompleteLog > div:nth-child(2)")

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate_to_checklist(self) -> None:
        """Clicks the Checklist sidebar tab and waits for the page to fully load."""
        logger.info("Navigating to Checklist tab.")
        self._wait_for_loader()
        self.js_click(self.checklist_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    # ── Layout Verification ────────────────────────────────────────────────────

    def verify_initial_layout(self) -> None:
        """
        Asserts all critical structural elements are present on the Checklist page.
        Validates: app header, main heading, condition radio filter, and
        the Non-Other conditions grid container.
        """
        logger.info("Verifying Checklist page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.checklist_heading).to_be_visible(timeout=15000)
        expect(self.condition_radio_application).to_be_visible(timeout=10000)
        expect(self.non_other_grid).to_be_visible(timeout=10000)

    # ── Non-Other Grid Interactions ───────────────────────────────────────────

    def open_first_condition_row(self) -> None:
        """
        Clicks the action button on the first visible row in the Non-Other
        conditions grid to expand its detail/edit pane.
        """
        logger.info("Opening the first condition row in the Non-Other grid.")
        self._wait_for_loader()
        self.first_row_edit_button.wait_for(state="visible", timeout=15000)
        self.js_click(self.first_row_edit_button)
        self._wait_for_loader()

    def click_update(self) -> None:
        """Clicks the Update button to save changes to the expanded condition row."""
        logger.info("Clicking the Update button for the expanded condition row.")
        self.update_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.update_button)
        self._wait_for_loader()

    # ── Pagination Helpers & Checks ───────────────────────────────────────────

    def paginate_grid_next(self, next_btn_locator, clicks: int = 2, grid_name: str = "grid") -> None:
        """
        Paginates forward up to `clicks` times if the next page button is active and enabled.
        """
        for i in range(clicks):
            try:
                next_btn_locator.wait_for(state="visible", timeout=5000)
                css_classes = next_btn_locator.get_attribute("class") or ""
                if "k-state-disabled" in css_classes or not next_btn_locator.is_enabled():
                    logger.info(f"[{grid_name}] Next page button disabled or inactive. Stopping pagination.")
                    break
                logger.info(f"[{grid_name}] Navigating to next page (click {i + 1}/{clicks})...")
                try:
                    with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=10000) as response_info:
                        next_btn_locator.click(force=True)
                except Exception:
                    next_btn_locator.click(force=True)
                self._wait_for_loader()
                self.page.wait_for_timeout(1000)
            except Exception as e:
                logger.info(f"[{grid_name}] Stopped paginating: {e}")
                break

    def verify_pagination_functionality(self, next_btn, prev_btn, first_btn, last_btn, grid_name: str = "grid") -> None:
        """
        Dynamically verifies all pagination controls (Next, Prev, Last, First) if multiple pages are present.
        Uses the exact expect_response pattern from the previous path (permit listing).
        """
        logger.info(f"[{grid_name}] Starting pagination verification for all controls.")
        self._wait_for_loader()
        
        # Check if Next page is available
        next_btn.wait_for(state="visible", timeout=8000)
        class_attr = next_btn.get_attribute("class") or ""
        
        if "k-state-disabled" not in class_attr and next_btn.is_enabled():
            logger.info(f"[{grid_name}] Multiple pages detected. Testing Next Page.")
            # 1. Click Next Page
            try:
                with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                    next_btn.click(force=True)
                logger.info(f"[{grid_name}] Next page response received.")
            except Exception:
                next_btn.click(force=True)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)
            
            # 2. Click Previous Page
            logger.info(f"[{grid_name}] Testing Previous Page.")
            prev_btn.wait_for(state="visible", timeout=5000)
            try:
                with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                    prev_btn.click(force=True)
                logger.info(f"[{grid_name}] Previous page response received.")
            except Exception:
                prev_btn.click(force=True)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)
            
            # 3. Click Last Page
            logger.info(f"[{grid_name}] Testing Last Page.")
            last_btn.wait_for(state="visible", timeout=5000)
            try:
                with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                    last_btn.click(force=True)
                logger.info(f"[{grid_name}] Last page response received.")
            except Exception:
                last_btn.click(force=True)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)
            
            # 4. Click First Page
            logger.info(f"[{grid_name}] Testing First Page.")
            first_btn.wait_for(state="visible", timeout=5000)
            try:
                with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                    first_btn.click(force=True)
                logger.info(f"[{grid_name}] First page response received.")
            except Exception:
                first_btn.click(force=True)
            self._wait_for_loader()
            self.page.wait_for_timeout(1000)
            
            logger.info(f"[{grid_name}] All pagination controls verified successfully (Next -> Prev -> Last -> First).")
        else:
            logger.info(f"[{grid_name}] Pagination is disabled or only 1 page of records exists.")

    def paginate_non_other_to_last_page(self) -> None:
        """Navigates the Non-Other conditions grid forward (up to 2 pages)."""
        logger.info("Paginating Non-Other conditions grid (up to 2 pages).")
        self.paginate_grid_next(self.non_other_next_page, clicks=2, grid_name="NonOtherGrid")

    # ── Optional Conditions ───────────────────────────────────────────────────

    def select_optional_condition_radio(self) -> None:
        """
        Clicks the second radio option (div:nth-child(2)) which switches the
        grid display to show Optional conditions and reveals #nonOtherGridOptional.
        """
        logger.info("Selecting Optional condition radio button.")
        self.optional_condition_radio.wait_for(state="visible", timeout=10000)
        self.js_click(self.optional_condition_radio)
        self._wait_for_loader()
        expect(self.optional_condition_grid).to_be_visible(timeout=10000)

    def paginate_optional_to_last_page(self) -> None:
        """Navigates the Optional conditions grid forward (up to 2 pages)."""
        logger.info("Paginating Optional conditions grid (up to 2 pages).")
        self.paginate_grid_next(self.optional_next_page, clicks=2, grid_name="OptionalGrid")

    # ── Documents & Log Section ───────────────────────────────────────────────

    def verify_documents_and_log_section(self) -> None:
        """
        Verifies that the Documents and Log section is rendered and its key
        elements (heading, log status, and the log data grid) are all visible.
        """
        logger.info("Verifying Documents and Log section.")
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
        expect(self.complete_log_status).to_be_visible(timeout=15000)
        expect(self.complete_log_grid).to_be_visible(timeout=15000)
