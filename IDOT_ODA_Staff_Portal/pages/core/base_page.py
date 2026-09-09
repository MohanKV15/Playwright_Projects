import logging
import re
from typing import Optional, Union
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class BasePage:
    """
    Core BasePage implementing universal Playwright action wrappers,
    safe click/fill handlers, and robust loader synchronization.

    Adheres strictly to the Page Object Model (POM):
    - Free of test harness scripts (zoom initialization and failure reporting belong in conftest).
    - Free of domain/widget-specific controls (Kendo widgets are isolated in dedicated components).
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

        # Centralized Global Loaders
        self.global_loader = page.locator("#loader, #loading, .loading")
        self.kendo_loader = page.locator(
            ".k-loading-mask, .k-loading-image, .k-loading-color, .k-i-loading"
        )

    def _wait_for_loader(self, timeout: int = 15000) -> None:
        """
        Waits for active Kendo loading masks or AJAX spinners to disappear
        and automatically dismisses any system error modals blocking the page.
        """
        # Auto-dismiss any 'Error occured. Contact Administrator' popup blocking the page
        try:
            error_modal = self.page.locator(".k-window:visible, .k-dialog:visible, .modal:visible").filter(
                has_text=re.compile(r"Error occured|Contact Administrator|An error occurred", re.I)
            )
            if error_modal.count() > 0 and error_modal.first.is_visible(timeout=500):
                ok_btn = error_modal.first.locator("button:has-text('OK'), .k-button:has-text('OK')").first
                if ok_btn.is_visible(timeout=500):
                    self.logger.warning("Auto-dismissing error modal dialog by clicking OK.")
                    ok_btn.click(force=True)
                    self.page.wait_for_timeout(300)
        except Exception:
            pass

        loader_selectors = [
            "#loader:visible",
            ".k-loading-mask:visible",
            ".k-loading-image:visible",
            ".k-loading-color:visible",
            ".k-i-loading:visible",
            "#loading:visible",
            ".loading:visible",
        ]
        combined_selector = ", ".join(loader_selectors)
        try:
            loader = self.page.locator(combined_selector)
            if loader.count() > 0:
                loader.first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

        try:
            visible_dialogs = self.page.locator(".k-window:visible, .k-dialog:visible")
            if visible_dialogs.count() == 0:
                self.page.locator(".k-overlay").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

    def _wait_for_page_ready(self) -> None:
        """Universal utility to pause execution until AJAX and UI rendering completes."""
        self._wait_for_loader()

    # ---------- CORE NAVIGATION & SYNCHRONIZATION ----------
    def navigate(self, url: str, timeout_ms: int = 30000) -> None:
        """Navigates to URL with resilient fallback handling."""
        self.logger.info(f"Navigating to URL: {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        except Exception as e:
            self.logger.warning(
                f"Navigation to {url} timed out waiting for domcontentloaded: {e}. Retrying with commit..."
            )
            self.page.goto(url, wait_until="commit", timeout=timeout_ms)
        self._wait_for_loader()

    def wait_for_url(self, url_pattern: str, timeout_ms: int = 30000) -> None:
        """Waits for page URL to match pattern and synchronizes loaders."""
        self.logger.info(f"Waiting for URL pattern: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout_ms)
        self._wait_for_loader()

    # ---------- CORE UI ACTION WRAPPERS ----------
    def safe_click(self, locator_or_selector: Union[Locator, str], timeout_ms: int = 10000) -> bool:
        """Waits for element, scrolls into view (with sticky header offset), and clicks safely."""
        self._wait_for_loader()
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.scroll_into_view_if_needed()
            # Scroll up slightly to avoid occlusion under sticky top headers
            try:
                self.page.evaluate("window.scrollBy(0, -100)")
            except Exception:
                pass
            locator.click(timeout=timeout_ms)
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.warning(f"Click failed on {locator_or_selector}: {e}. Trying JS click.")
            return self.js_click(locator_or_selector)

    def safe_fill(
        self, locator_or_selector: Union[Locator, str], value: str, timeout_ms: int = 10000
    ) -> bool:
        """Fills text into target locator safely."""
        self._wait_for_loader()
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.fill(value, timeout=timeout_ms)
            return True
        except Exception as e:
            self.logger.error(f"Fill failed for {locator_or_selector}: {e}")
            return False

    def js_click(self, locator_or_selector: Union[Locator, str]) -> bool:
        """Triggers click event directly via JavaScript evaluation to bypass overlays."""
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            locator.evaluate("el => el.click()")
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.error(f"JS click failed: {e}")
            return False

    def dispatch_bubble_click(self, locator_or_selector: Union[Locator, str]) -> bool:
        """Dispatches a native JS click event that bubbles up the DOM for complex buttons."""
        self._wait_for_loader()
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            locator.wait_for(state="visible", timeout=5000)
            locator.scroll_into_view_if_needed()
            locator.evaluate(
                "el => el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }))"
            )
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.error(f"Dispatch bubble click failed: {e}")
            return False

    def scroll_to_locator(self, locator_or_selector: Union[Locator, str]) -> None:
        """Scrolls an element into view smoothly."""
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            locator.scroll_into_view_if_needed()
        except Exception:
            pass

    def get_element_text(self, locator_or_selector: Union[Locator, str]) -> str:
        """Returns inner text for the target element."""
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            return locator.inner_text()
        except Exception:
            return ""

    def click_element(self, selector: str) -> None:
        """Standard selector click with selector wait."""
        self.page.wait_for_selector(selector)
        self.page.click(selector)

    def fill_input(self, selector: str, text: str) -> None:
        """Standard selector text fill with selector wait."""
        self.page.wait_for_selector(selector)
        self.page.fill(selector, text)

    def wait_for_element(self, selector: str, timeout: int = 30000) -> None:
        """Standard wait for selector."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def is_visible(self, locator_or_selector: Union[Locator, str], timeout_ms: int = 3000) -> bool:
        """Safely checks if an element is visible within timeout without throwing exception."""
        try:
            locator = (
                locator_or_selector
                if isinstance(locator_or_selector, Locator)
                else self.page.locator(locator_or_selector)
            )
            return locator.is_visible(timeout=timeout_ms)
        except Exception:
            return False
