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
    KendoCheckbox,
    KendoButton,
    KendoGrid,
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
        self.kendo_checkbox = self.kendo_controls.checkbox
        self.kendo_button = self.kendo_controls.button
        self.kendo_grid = self.kendo_controls.grid
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

    def select_first_dropdown(self, dropdown_locator_or_selector: Union[Locator, str], timeout_ms: int = 5000) -> bool:
        """Selects the first valid option from a Kendo or native dropdown widget."""
        self._wait_for_loader()
        res = self.kendo_dropdown.select_first_option(dropdown_locator_or_selector, timeout_ms=timeout_ms)
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

    def check_kendo_checkbox(self, checkbox_locator_or_selector: Union[Locator, str], input_index: Optional[int] = None) -> bool:
        """Checks a Kendo UI checkbox widget safely."""
        return self.kendo_checkbox.check(checkbox_locator_or_selector, input_index=input_index)

    def handle_kendo_alert(self, timeout_ms: int = 5000) -> bool:
        """Detects and clicks OK on Kendo alert/confirm dialogs if displayed."""
        res = KendoControls.handle_kendo_alert(self.page, timeout_ms=timeout_ms)
        if res:
            self._wait_for_loader()
        return res

    def click_dialog_ok(self, timeout_ms: int = 15000) -> bool:
        """Clicks OK on active confirmation or alert modal dialog."""
        ok_btn = (
            self.page.get_by_role("button", name=re.compile(r"^OK$", re.I))
            .or_(self.page.locator(".k-dialog:visible button:has-text('OK')"))
            .or_(self.page.locator(".k-window:visible button:has-text('OK')"))
            .or_(self.page.locator("button:visible:has-text('OK')"))
            .first
        )
        ok_btn.wait_for(state="visible", timeout=timeout_ms)
        ok_btn.click()
        self._wait_for_loader()
        return True

    def dismiss_survey_modal(self, timeout_ms: int = 3000) -> bool:
        """Dismisses the optional survey prompt modal by clicking 'No' if present."""
        res = KendoControls.dismiss_survey_modal(self.page, timeout_ms=timeout_ms)
        if res:
            self._wait_for_loader()
        return res

    def click_kendo_button(self, button_locator_or_selector: Union[Locator, str], timeout_ms: int = 5000) -> bool:
        """Enables and clicks a Kendo button widget safely."""
        return self.kendo_button.click(button_locator_or_selector, timeout_ms=timeout_ms)

    def click_grid_row_button(
        self,
        grid_locator_or_selector: Union[Locator, str],
        row_index: int = 0,
        button_name_regex: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> bool:
        """Clicks the action button inside the specified Kendo grid row (defaults to 1st record)."""
        res = self.kendo_grid.click_row_button(
            grid_locator_or_selector,
            row_index=row_index,
            button_name_regex=button_name_regex,
            timeout_ms=timeout_ms,
        )
        if res:
            self._wait_for_loader()
        return res

    def get_grid_first_record_identifier(
        self,
        grid_locator_or_selector: Union[Locator, str],
        pattern: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> str:
        """Retrieves primary identifier from the 1st record row of a Kendo Grid."""
        return self.kendo_grid.get_first_record_identifier(
            grid_locator_or_selector,
            pattern=pattern,
            timeout_ms=timeout_ms,
        )

    def clean_downloads_folder(self) -> None:
        """Removes previous files in downloads directory so only the latest download remains."""
        downloads_dir = Config.DOWNLOADS_DIR
        downloads_dir.mkdir(parents=True, exist_ok=True)
        for item in downloads_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception as e:
                    self.logger.warning(f"Could not delete old download {item}: {e}")

    def download_export_file(
        self,
        export_button: Union[Locator, str],
        default_filename: str = "Export.xlsx",
        timeout_ms: int = 30000,
    ) -> Path:
        """
        Cleans previous downloads, triggers export click on export_button,
        waits for download, saves into downloads directory, and verifies it exists and is non-empty.
        """
        self.clean_downloads_folder()
        downloads_dir = Config.DOWNLOADS_DIR

        btn = export_button if isinstance(export_button, Locator) else self.page.locator(export_button)
        btn.scroll_into_view_if_needed()

        with self.page.expect_download(timeout=timeout_ms) as download_info:
            self.click_kendo_button(btn)

        download = download_info.value
        filename = download.suggested_filename or default_filename
        target_path = downloads_dir / filename
        download.save_as(str(target_path))

        self.logger.info(f"Latest export file saved to: {target_path}")
        assert target_path.exists(), f"Downloaded file was not found at: {target_path}"
        assert target_path.stat().st_size > 0, f"Downloaded export file at {target_path} is empty"

        self._wait_for_loader()
        return target_path

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

