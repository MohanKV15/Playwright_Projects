import re
from playwright.sync_api import Page, expect


class ActionItemsPage:

    def __init__(self, page: Page):
        self.page = page
        self.grid       = page.locator("#ActionItemGrid")
        self.rows       = page.locator("#ActionItemGrid tbody tr")
        self.loader     = page.locator(".k-loading-mask")
        self.action_items_btn = page.locator("#btnActionItems")
        self.next_btn   = page.get_by_role("link", name="Go to the next page")

    # ---------- NAVIGATION ----------
    def open(self):
        with self.page.expect_navigation(
            url=re.compile("ActionItems|CAActionItems", re.I),
            wait_until="load",
            timeout=20000
        ):
            self.action_items_btn.click()
        self._wait_for_page_ready()

    # ---------- RECORDS ----------
    def open_first_n_records(self, n: int = 2):
        self._wait_for_page_ready()
        count = self.rows.count()
        assert count > 0, "No records found in Action Items table"

        for i in range(min(n, count)):
            row = self.rows.nth(i)
            edit_btn = self._get_edit_button(row)
            expect(edit_btn).to_be_visible()
            edit_btn.scroll_into_view_if_needed()
            self._click_and_wait(edit_btn)
            self._validate_form_loaded()
            self.page.mouse.wheel(0, 4000)
            self.go_back()

    def _get_edit_button(self, row):
        btn = row.locator(
            "button.viewBtn, a.k-grid-edit, button[title='Edit'], a[title='Edit']"
        )
        if btn.count() == 0:
            btn = row.get_by_role("button")
        return btn.first

    def _click_and_wait(self, element):
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=10000):
                element.click()
        except Exception:
            element.click()
            self.page.wait_for_url(re.compile("Portal/Page/Index"), timeout=10000)
        self._wait_for_loader()

    def _validate_form_loaded(self):
        expect(self.page).to_have_url(re.compile("Portal/Page/Index", re.I))
        expect(self.page.locator("form")).to_be_visible(timeout=15000)

    def go_back(self):
        self.page.go_back()
        self._wait_for_page_ready()
        expect(self.page).to_have_url(re.compile("ActionItems", re.I))

    # ---------- PAGINATION ----------
    def validate_pagination(self):
        while True:
            self._wait_for_loader()
            if "k-state-disabled" in (self.next_btn.get_attribute("class") or ""):
                break
            try:
                self.next_btn.click(timeout=5000)
            except Exception:
                self.page.wait_for_timeout(500)
                self.next_btn.click(force=True)
            self._wait_for_page_ready()

    # ---------- WAITS ----------
    def _wait_for_page_ready(self):
        self.grid.wait_for(state="visible", timeout=15000)
        self._wait_for_loader()
        expect(self.rows.first).to_be_visible()

    def _wait_for_loader(self):
        try:
            self.loader.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(300)