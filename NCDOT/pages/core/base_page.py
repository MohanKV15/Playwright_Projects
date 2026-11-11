import logging
from typing import Optional, Union
from playwright.sync_api import Page, Locator, expect
from utils.config import Config
from pages.core.kendo_controls import (
    KendoControls,
    KendoDropdown,
    KendoDatePicker,
    KendoNumericTextBox,
    KendoCheckbox,
    KendoDialog,
)

logger = logging.getLogger(__name__)


class BasePage:
    """
    BasePage class implementing core Playwright action wrappers,
    screen zoom initialization, modal dialog handlers, Kendo UI utilities,
    and resilient error handling.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        self.kendo_controls = KendoControls(page)
        self.kendo_dropdown = self.kendo_controls.dropdown
        self.kendo_datepicker = self.kendo_controls.datepicker
        self.kendo_numeric = self.kendo_controls.numeric
        self.kendo_checkbox = self.kendo_controls.checkbox
        self.kendo_dialog = self.kendo_controls.dialog
        self._inject_zoom_init_script()
        self._apply_zoom_script()

    def _inject_zoom_init_script(self) -> None:
        """Injects persistent init script so any new document automatically renders at configured zoom."""
        try:
            self.page.add_init_script(
                f"""
                (() => {{
                    const apply = () => {{
                        if (document.body) {{
                            document.body.style.zoom = '{Config.ZOOM_PERCENT}%';
                        }} else {{
                            setTimeout(apply, 10);
                        }}
                    }};
                    if (document.readyState === 'loading') {{
                        document.addEventListener('DOMContentLoaded', apply, {{ once: true }});
                    }} else {{
                        apply();
                    }}
                    window.addEventListener('load', apply);
                }})();
                """
            )
        except Exception:
            pass

    def _apply_zoom_script(self) -> None:
        """Applies zoom cleanly to body without custom margin/width distortion."""
        try:
            self.page.evaluate(
                f"""
                (() => {{
                    if (document.body) {{
                        document.body.style.zoom = '{Config.ZOOM_PERCENT}%';
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

        # Apply screen zoom to 67% on navigated page
        self._apply_zoom_script()

    def js_click(self, locator: Union[Locator, str]) -> None:
        """Performs a direct JavaScript dispatch click to bypass pointer interception."""
        loc = locator if isinstance(locator, Locator) else self.page.locator(locator)
        loc.first.evaluate("el => el.click()")

    def dismiss_kendo_dialogs(self) -> None:
        """Delegates dismissal of Kendo alerts and modal popups."""
        self.kendo_dialog.dismiss_alerts()

    def select_kendo_dropdown(self, target: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """Selects an option in a Kendo dropdown."""
        self._wait_for_loader()
        res = self.kendo_dropdown.select(target, option_text, timeout_ms=timeout_ms)
        self._wait_for_loader()
        return res

    def set_kendo_numeric(self, selector_or_id: str, value: float) -> bool:
        """Sets a numeric value into a KendoNumericTextBox."""
        return self.kendo_numeric.set_value(selector_or_id, value)

    def pick_kendo_date(self, trigger: Union[Locator, str], day_text: Optional[str] = None) -> bool:
        """Picks a date from a Kendo DatePicker popup calendar."""
        return self.kendo_datepicker.pick_date(trigger_locator=trigger, day_text=day_text)

