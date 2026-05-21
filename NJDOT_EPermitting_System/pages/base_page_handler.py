from NJDOT_EPermitting_System.config import PROJECT_ROOT
import logging
import time
from typing import Optional, Callable, Any
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect


class PageLoadError(Exception):
   pass


class ElementNotFoundError(Exception):
   pass


class BasePageHandler:
   """Base class with robust handling (clean + stable)."""

   DEBUG_ARTIFACTS_DIR = PROJECT_ROOT / "reports" / "debug_artifacts"

   def __init__(self, page: Page, script_name: str = "test"):
       self.page = page
       self.script_name = script_name
       self.logger = logging.getLogger(__name__)
       self.DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

   # -----------------------------
   # Debug Artifacts
   # -----------------------------
   def _capture_debug_artifacts(self, scenario: str):
       try:
           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           path = self.DEBUG_ARTIFACTS_DIR / f"{timestamp}_{scenario}.png"
           self.page.screenshot(path=str(path))
           self.logger.info(f"Screenshot saved: {path}")
       except Exception as e:
           self.logger.error(f"Screenshot failed: {e}")

   # -----------------------------
   # Retry Logic (KEEP - important)
   # -----------------------------
   def _retry_with_backoff(self, action: Callable, max_retries=3, timeout_ms=5000):
       wait = 1
       for attempt in range(max_retries):
           try:
               return action(timeout_ms)
           except Exception as e:
               if attempt == max_retries - 1:
                   raise e
               self.page.wait_for_timeout(wait * 1000)
               wait *= 1.5

   # -----------------------------
   # Page Load
   # -----------------------------
   def assert_page_loaded(self, url_pattern: str = None, timeout_ms: int = 30000):
       self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
       if url_pattern:
           expect(self.page).to_have_url(url_pattern)

   # -----------------------------
   # Element Helpers (KEEP)
   # -----------------------------
   def element_exists(self, selector: str) -> bool:
       return self.page.locator(selector).count() > 0

   def safe_click(self, selector: str, timeout_ms: int = 10000) -> bool:
       try:
           def action(timeout):
               locator = self.page.locator(selector)
               if not locator.count():
                   raise ElementNotFoundError(selector)
               locator.click(timeout=timeout)

           self._retry_with_backoff(action, timeout_ms=timeout_ms)
           return True
       except Exception as e:
           self.logger.error(f"Click failed: {selector} -> {e}")
           return False

   def safe_fill(self, selector: str, value: str, timeout_ms: int = 10000) -> bool:
       try:
           def action(timeout):
               locator = self.page.locator(selector)
               if not locator.count():
                   raise ElementNotFoundError(selector)
               locator.fill(value, timeout=timeout)

           self._retry_with_backoff(action, timeout_ms=timeout_ms)
           return True
       except Exception as e:
           self.logger.error(f"Fill failed: {selector} -> {e}")
           return False

   def wait_for_element(self, selector: str, timeout_ms: int = 30000) -> bool:
       try:
           self.page.wait_for_selector(selector, timeout=timeout_ms)
           return True
       except Exception:
           self._capture_debug_artifacts(f"not_found_{selector}")
           return False

   # -----------------------------
   # Error Detection (KEEP)
   # -----------------------------
   def detect_error_page(self) -> Optional[str]:
       content = self.page.content().lower()

       if "payment failed" in content:
           return "payment_failure"
       # Keep this check precise to avoid false positives (the word "session"
       # can appear on unrelated pages/cookies).
       if (
           "session expired" in content
           or "session has expired" in content
           or "your session has expired" in content
           or "session timed out" in content
           or "session timeout" in content
       ):
           return "session_expired"
       if "server error" in content:
           return "server_error"

       return None

   # -----------------------------
   # Scroll Helper (KEEP)
   # -----------------------------
   def _scroll_and_click(self, locator, timeout_ms: int = 10000):
       locator.scroll_into_view_if_needed()
       locator.click(timeout=timeout_ms)



 