import re
from playwright.sync_api import Page, expect
from utils.ui_actions import download_file


class PermitHistoryPage:

    def __init__(self, page: Page):
        self.page = page

        # --- Dashboard ---
        self.view_apps_btn = page.locator("#btnViewSubmittedApps")

        # --- Page ---
        self.history_header = page.locator("h4", has_text="Application/Permit History")

        # --- Search ---
        self.search_input = page.locator("#Action_Item_Search_Text")
        self.search_btn = page.get_by_role("button", name=re.compile("Search"))

        # --- Grid ---
        self.grid = page.locator("#CustActionItemsList")
        self.grid_rows = page.locator("#CustActionItemsList tbody tr")
        self.no_records_msg = page.get_by_text("No records available.")

        # --- Pagination ---
        self.next_btn = page.get_by_role("link", name="Go to the next page")

        # --- Export ---
        self.export_btn = page.get_by_role("button", name=re.compile("Export"))

        # --- Loaders ---
        self.loader = page.locator(".k-loading-mask")
        self.global_loader = page.locator("#loader")

        # --- Filter ---
        self.filter_dropdown = page.locator("#filterViewDiv").locator(".k-input")

    # ---------- WAITS ----------
    def _wait_for_loader(self):
        try:
            self.global_loader.wait_for(state="hidden", timeout=15000)
        except:
            pass

        try:
            self.loader.wait_for(state="hidden", timeout=10000)
        except:
            pass

        self.page.wait_for_timeout(300)

    def _wait_for_page_ready(self):
        self._wait_for_loader()

    # ---------- NAVIGATION ----------
    def open_permit_history(self):
        self.page.wait_for_load_state("load", timeout=30000)

        self.view_apps_btn.wait_for(state="visible", timeout=10000)
        self.view_apps_btn.scroll_into_view_if_needed()

        with self.page.expect_navigation(
            url="**/HTCP4321AppHistory**",
            wait_until="load",
            timeout=30000
        ):
            self.view_apps_btn.click(no_wait_after=True)

        self._wait_for_page_ready()

    # ---------- VERIFY ----------
    def verify_history_visible(self):
        expect(self.history_header).to_be_visible(timeout=15000)

    # ---------- FILTER + SEARCH ----------
    def apply_filter_and_search(self, filter_value: str = "months", keyword: str = "highway"):
        self._wait_for_page_ready()
        self.filter_dropdown.wait_for(state="visible", timeout=10000)
        try:
            self.filter_dropdown.click(timeout=5000)
        except:
            self.filter_dropdown.click(force=True)

        option = self.page.locator("li[role='option']").filter(has_text=filter_value)
        option.wait_for(state="visible", timeout=10000)
        option.click()

        self.search_input.fill(keyword)
        self.search_btn.click()

        self._wait_for_page_ready()
        self.grid.wait_for(state="visible", timeout=15000)

    # ---------- GRID VALIDATION ----------
    def verify_records_present(self) -> bool:
        # Dynamically wait for either actual grid rows to render OR the empty-state message to appear
        try:
            self.grid_rows.first.or_(self.no_records_msg).wait_for(state="visible", timeout=15000)
        except Exception as e:
            raise AssertionError(f"❌ Grid failed to load entirely. Neither records nor empty-state appeared. {e}")

        if self.no_records_msg.is_visible():
            return False

        count = self.grid_rows.count()
        if count == 0:
            return False
            
        return True

    # ---------- PAGINATION ----------
    def validate_pagination(self):
        while True:
            self._wait_for_loader()

            class_attr = self.next_btn.get_attribute("class") or ""
            if "k-state-disabled" in class_attr:
                break

            try:
                self.next_btn.click(timeout=5000)
            except:
                self.page.wait_for_timeout(500)
                self.next_btn.click(force=True)

            self._wait_for_page_ready()

    # ---------- EXPORT ----------
    def export_file(self):
        return download_file(self.page, self.export_btn, module="permit")