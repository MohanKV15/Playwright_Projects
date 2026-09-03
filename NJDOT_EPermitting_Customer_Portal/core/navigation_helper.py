import re

from playwright.sync_api import expect


class NavigationHelper:
    """Navigation and recovery helpers for redirects/popups/tabs."""

    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger

    def switch_to_latest_page_if_closed(self) -> bool:
        if not self.page.is_closed():
            return False
        open_pages = [p for p in self.page.context.pages if not p.is_closed()]
        if not open_pages:
            return False
        self.page = open_pages[-1]
        if self.logger:
            self.logger.warning("Switched to latest open page: %s", self.page.url)
        return True

    def ensure_payment_page_context(self, timeout_ms: int = 15000):
        payment_url_pattern = re.compile(r"Payment", re.I)
        if not self.page.is_closed() and payment_url_pattern.search(self.page.url):
            return self.page

        for candidate in reversed(self.page.context.pages):
            if not candidate.is_closed() and payment_url_pattern.search(candidate.url):
                self.page = candidate
                return self.page

        expect(self.page).to_have_url(payment_url_pattern, timeout=timeout_ms)
        return self.page

    def retry_click_via_dom(self, button_id: str = "btnSubmit") -> bool:
        try:
            return bool(
                self.page.evaluate(
                    """
                    (id) => {
                        const btn = document.getElementById(id);
                        if (!btn) return false;
                        btn.removeAttribute('disabled');
                        btn.setAttribute('aria-disabled', 'false');
                        btn.focus();
                        btn.dispatchEvent(new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                        }));
                        return true;
                    }
                    """,
                    button_id,
                )
            )
        except Exception:
            return False

    def get_visible_dialog_text(self) -> str:
        selectors = [
            ".k-dialog-wrapper:visible .k-dialog-content:visible",
            ".k-window:visible .k-window-content:visible",
            ".k-dialog:visible .k-dialog-content:visible",
        ]
        for selector in selectors:
            locator = self.page.locator(selector).last
            try:
                if locator.count() == 0:
                    continue
                text = locator.inner_text().strip()
                if text:
                    return text
            except Exception:
                continue
        return ""

    def click_visible_dialog_action(self) -> bool:
        # Prefer explicit role-based matches first (most stable across Kendo variants).
        role_candidates = [
            self.page.get_by_role("button", name=re.compile(r"Continue", re.I)),
            self.page.get_by_role("button", name=re.compile(r"OK|Ok", re.I)),
            self.page.get_by_role("button", name=re.compile(r"Yes", re.I)),
            self.page.get_by_role("button", name=re.compile(r"Payment|Pay", re.I)),
            self.page.get_by_role("link", name=re.compile(r"Continue", re.I)),
            self.page.get_by_role("link", name=re.compile(r"Payment|Pay", re.I)),
        ]
        for candidate in role_candidates:
            try:
                if candidate.count() == 0:
                    continue
                btn = candidate.first
                btn.scroll_into_view_if_needed()
                btn.click(timeout=5000)
                return True
            except Exception:
                continue

        selectors = [
            ".k-dialog-wrapper:visible button:has-text('Continue')",
            ".k-dialog-wrapper:visible .k-primary:has-text('Continue')",
            ".k-dialog-wrapper:visible button:has-text('Payment')",
            ".k-dialog-wrapper:visible a:has-text('Payment')",
            ".k-dialog-wrapper:visible .k-primary:has-text('Payment')",
            ".k-dialog-wrapper:visible button:has-text('OK')",
            ".k-dialog-wrapper:visible .k-primary:has-text('OK')",
            ".k-dialog-wrapper:visible button:has-text('Yes')",
            ".k-dialog-wrapper:visible .k-primary:has-text('Yes')",
            ".k-window:visible button:has-text('Continue')",
            ".k-window:visible .k-primary:has-text('Continue')",
            ".k-window:visible button:has-text('Payment')",
            ".k-window:visible a:has-text('Payment')",
            ".k-window:visible .k-primary:has-text('Payment')",
            ".k-window:visible button:has-text('OK')",
            ".k-window:visible .k-primary:has-text('OK')",
            ".k-window:visible .k-primary",
            ".k-dialog-wrapper:visible .k-primary",
        ]
        for selector in selectors:
            button = self.page.locator(selector).first
            try:
                if button.count() == 0:
                    continue
                button.scroll_into_view_if_needed()
                button.click(timeout=5000)
                return True
            except Exception:
                continue
        return False
