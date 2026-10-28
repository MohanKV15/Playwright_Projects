import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Page, Locator, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.kendo_controls import (
    KendoControls,
    KendoDropdown,
    KendoDatePicker,
    KendoNumericTextBox,
    KendoMaskedTextBox,
)

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
        self.kendo_controls = KendoControls(page)
        self.kendo_dropdown = self.kendo_controls.dropdown
        self.kendo_datepicker = self.kendo_controls.datepicker
        self.kendo_numeric = self.kendo_controls.numeric
        self.kendo_masked = self.kendo_controls.masked
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
            "#loader.k-loading-image",
            ".k-loading-mask",
            ".k-loading-image",
            ".k-loading-color",
            ".k-i-loading",
            "#loading",
            ".loading",
        ]
        combined_selector = ", ".join(loader_selectors)
        try:
            loader = self.page.locator(combined_selector)
            if loader.count() > 0:
                loader.first.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

    def navigate(self, url: str, timeout_ms: int = 45000) -> None:
        """Navigates to URL with resilient fallback handling slow staging responses."""
        self.logger.info(f"Navigating to URL: {url}")
        response = None
        try:
            response = self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        except Exception as e:
            self.logger.warning(f"Navigation to {url} timed out waiting for domcontentloaded: {e}. Retrying with commit status...")
            response = self.page.goto(url, wait_until="commit", timeout=timeout_ms)

        # Detect server outage / bad gateway immediately to avoid 30s locator timeouts
        status = response.status if response else None
        if status and status >= 500:
            error_msg = f"Target Environment Unavailable: '{url}' returned HTTP {status} ({response.status_text}). Backend server is down or unreachable."
            self.logger.critical(error_msg)
            raise RuntimeError(error_msg)

        page_title = (self.page.title() or "").lower()
        if "502 bad gateway" in page_title or "service unavailable" in page_title:
            error_msg = f"Target Environment Error: '{url}' displayed '{self.page.title()}'. Check if backend server is down or VPN is disconnected."
            self.logger.critical(error_msg)
            raise RuntimeError(error_msg)

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
        res = self.kendo_dropdown.select(dropdown_locator_or_selector, item_text, timeout_ms=timeout_ms)
        self._wait_for_loader()
        return res

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
        res = KendoControls.handle_kendo_alert(self.page, timeout_ms=timeout_ms)
        if res:
            self._wait_for_loader()
        return res

    def scroll_to_section(self, section_locator: Union[Locator, str]) -> None:
        """
        Scrolls smoothly to a major section heading or element to provide a steady,
        natural visual progression down the page.
        """
        try:
            locator = section_locator if isinstance(section_locator, Locator) else self.page.locator(section_locator)
            locator.evaluate("el => el.scrollIntoView({ behavior: 'smooth', block: 'start' })")
        except Exception:
            pass

    def capture_screenshot(self, scenario_name: str) -> None:
        """Saves a screenshot into debug_artifacts directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = DEBUG_ARTIFACTS_DIR / f"{timestamp}_{scenario_name}.png"
            self.page.screenshot(path=str(path))
            self.logger.info(f"Screenshot saved to: {path}")
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")

