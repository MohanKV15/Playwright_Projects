import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Page, Locator, expect
from IDOT_ODA_Customer_Portal.utils.config import Config

DEBUG_ARTIFACTS_DIR = Config.PROJECT_ROOT / "reports" / "debug_artifacts"
ZOOM_PERCENT = Config.ZOOM_PERCENT
DEFAULT_TIMEOUT = Config.TIMEOUT

logger = logging.getLogger(__name__)


class BasePage:
    """
    BasePage class implementing core Playwright action wrappers,
    screen zoom initialization, modal dialog handlers, Kendo UI utilities,
    and debug diagnostics.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self._apply_zoom_script()

    def _apply_zoom_script(self) -> None:
        """Applies zoom cleanly without body width distortion."""
        try:
            self.page.evaluate(
                f"""
                (() => {{
                    if (document.body) {{
                        document.body.style.zoom = '{ZOOM_PERCENT}%';
                    }}
                }})();
                """
            )
        except Exception:
            pass

    def _wait_for_loader(self, timeout: int = 15000) -> None:
        """Waits for any active Kendo loading masks or AJAX spinners to disappear."""
        loader_selectors = [
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

    def navigate(self, url: str, timeout_ms: int = 30000) -> None:
        """Navigates to URL with resilient fallback handling slow staging responses."""
        self.logger.info(f"Navigating to URL: {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        except Exception as e:
            self.logger.warning(f"Navigation to {url} timed out waiting for domcontentloaded: {e}. Retrying with commit status...")
            self.page.goto(url, wait_until="commit", timeout=timeout_ms)
        self._apply_zoom_script()
        self._wait_for_loader()

    def safe_click(self, locator_or_selector: Union[Locator, str], timeout_ms: int = 10000) -> bool:
        """Waits for element, scrolls into view, and clicks safely."""
        self._wait_for_loader()
        try:
            locator = locator_or_selector if isinstance(locator_or_selector, Locator) else self.page.locator(locator_or_selector)
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.scroll_into_view_if_needed()
            locator.click(timeout=timeout_ms)
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.warning(f"Click failed on {locator_or_selector}: {e}. Trying JS click.")
            return self.js_click(locator_or_selector)

    def safe_fill(self, locator_or_selector: Union[Locator, str], value: str, timeout_ms: int = 10000) -> bool:
        """Fills text into target locator safely."""
        self._wait_for_loader()
        try:
            locator = locator_or_selector if isinstance(locator_or_selector, Locator) else self.page.locator(locator_or_selector)
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.fill(value, timeout=timeout_ms)
            return True
        except Exception as e:
            self.logger.error(f"Fill failed for {locator_or_selector}: {e}")
            return False

    def js_click(self, locator_or_selector: Union[Locator, str]) -> bool:
        """Triggers click event directly via JavaScript evaluation."""
        try:
            locator = locator_or_selector if isinstance(locator_or_selector, Locator) else self.page.locator(locator_or_selector)
            locator.evaluate("el => el.click()")
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.error(f"JS click failed: {e}")
            return False

    def select_kendo_dropdown(self, dropdown_locator_or_selector: Union[Locator, str], item_text: str, timeout_ms: int = 10000) -> bool:
        """Opens a Kendo UI dropdown and selects the item matching item_text."""
        self._wait_for_loader()
        try:
            locator = dropdown_locator_or_selector if isinstance(dropdown_locator_or_selector, Locator) else self.page.locator(dropdown_locator_or_selector)
            locator.scroll_into_view_if_needed()
            locator.click(timeout=timeout_ms)
            self.page.wait_for_timeout(300)

            # Search in open popup list
            item_option = self.page.locator(".k-animation-container:visible li, .k-list-container:visible li").filter(
                has_text=re.compile(rf"^\s*{re.escape(item_text)}\s*$", re.I)
            ).first
            
            if item_option.count() == 0 or not item_option.is_visible():
                item_option = self.page.locator(".k-animation-container:visible li, .k-list-container:visible li").filter(
                    has_text=item_text
                ).first

            item_option.click(timeout=timeout_ms)
            self._wait_for_loader()
            self.logger.info(f"Selected '{item_text}' from Kendo dropdown.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to select '{item_text}' from Kendo dropdown: {e}")
            return False

    def set_kendo_datepicker(self, picker_locator_or_selector: Union[Locator, str], date_str: str) -> bool:
        """Sets date string in a Kendo datepicker input and triggers change event."""
        try:
            locator = picker_locator_or_selector if isinstance(picker_locator_or_selector, Locator) else self.page.locator(picker_locator_or_selector)
            locator.scroll_into_view_if_needed()
            locator.fill(date_str)
            locator.press("Tab")
            self._wait_for_loader()
            return True
        except Exception as e:
            self.logger.error(f"Failed to set date '{date_str}': {e}")
            return False

    def handle_kendo_alert(self, timeout_ms: int = 5000) -> bool:
        """Detects and clicks OK on Kendo alert/confirm dialogs if displayed."""
        try:
            active_dialog = self.page.locator(".k-window:visible, .k-dialog:visible, [role='dialog']:visible").first
            if active_dialog.is_visible(timeout=timeout_ms):
                ok_btn = active_dialog.locator("button:has-text('OK'), .k-button:has-text('OK'), button:has-text('Yes')").first
                if ok_btn.is_visible(timeout=2000):
                    ok_btn.click()
                    self._wait_for_loader()
                    return True
        except Exception:
            pass
        return False

    def capture_screenshot(self, scenario_name: str) -> None:
        """Saves a screenshot into debug_artifacts directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = DEBUG_ARTIFACTS_DIR / f"{timestamp}_{scenario_name}.png"
            self.page.screenshot(path=str(path))
            self.logger.info(f"Screenshot saved to: {path}")
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
