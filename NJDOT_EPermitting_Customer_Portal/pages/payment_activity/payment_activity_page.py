import re
from playwright.sync_api import Page
from utils.ui_actions import download_file


class PaymentActivityPage:

    def __init__(self, page: Page):
        self.page = page

        # ---------- LOCATORS ----------
        self.view_payment_btn = page.locator("#btnViewPayment")

        self.payment_header = page.locator("div").filter(
            has_text="Payment Activity Payment"
        ).nth(1)

        self.next_btn = page.get_by_role("link", name="Go to the next page")
        self.last_btn = page.get_by_role("link", name="Go to the last page")

        self.export_btn = page.get_by_role("button", name=re.compile("Export"))
        self.back_btn = page.get_by_role("button", name=re.compile("Back"))

        self.loader = page.locator(".k-loading-mask")

        # Page input (Page 1 of 200)
        self.page_input = page.get_by_role("spinbutton")

    # ---------- WAITS ----------
    def _wait_for_loader(self):
        try:
            self.loader.wait_for(state="hidden", timeout=10000)
        except:
            pass

    # ---------- NAVIGATION ----------
    def open_payment_activity(self):
        self.view_payment_btn.click()
        self.payment_header.click()
        self._wait_for_loader()

    # ---------- PAGINATION (BEST FIX) ----------
    def go_to_last_page(self):
        """
        Fast navigation to last page (no 200 clicks)
        """
        try:
            self.last_btn.wait_for(state="visible", timeout=5000)
            self.last_btn.click()
            self._wait_for_loader()
        except:
            # Fallback: use page input
            self._go_to_last_page_using_input()

    def _go_to_last_page_using_input(self):
        """
        Fallback using page number input
        """
        try:
            page_text = self.page.locator("text=of").inner_text()
            total_pages = int(page_text.split("of")[1].strip())

            self.page_input.fill(str(total_pages))
            self.page_input.press("Enter")

            self._wait_for_loader()
        except:
            # Final fallback (rare)
            while True:
                class_attr = self.next_btn.get_attribute("class") or ""
                if "k-state-disabled" in class_attr:
                    break

                self.next_btn.click()
                self._wait_for_loader()

    # ---------- EXPORT ----------
    def export_payment_data(self):
        return download_file(self.page, self.export_btn, module="payment")

    # ---------- BACK ----------
    def go_back(self):
        self.back_btn.click()