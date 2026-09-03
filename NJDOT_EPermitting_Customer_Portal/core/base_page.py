from NJDOT_EPermitting_Customer_Portal.config import PROJECT_ROOT
import logging
import time
from typing import Optional, Callable, Any
import os
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect
from faker import Faker

from NJDOT_EPermitting_Customer_Portal.core.kendo_mixin import KendoMixin


class PageLoadError(Exception):
   pass


class ElementNotFoundError(Exception):
   pass


class BasePage(KendoMixin):
   """Core base class with robust handling (clean + stable)."""

   DEBUG_ARTIFACTS_DIR = PROJECT_ROOT / "reports" / "debug_artifacts"
   BASE_HOST = (os.getenv("BASE_URL") or os.getenv("PYTEST_BASE_URL") or "https://u-njhtcp.bemcorp.net").rstrip("/")
   DASHBOARD_URL = f"{BASE_HOST}/Portal/Page/Index/4321CustomerPortalDashboardFull"
   _file_pdf = PROJECT_ROOT / "testdata" / "attachments" / "file.pdf"
   SUPPORTING_DOCUMENT_PATH = Path(
      os.getenv("NJHT_SUPPORTING_DOCUMENT_PATH")
      or (_file_pdf if _file_pdf.exists() else PROJECT_ROOT / "testdata" / "dummy.pdf")
   )

   def __init__(self, page: Page, script_name: str = "test"):
       self.page = page
       self.fake = Faker()
       self.script_name = script_name
       self.logger = logging.getLogger(__name__)
       self.DEBUG_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

   # -----------------------------
   # Debug Artifacts
   # -----------------------------
   def _capture_debug_artifacts(self, scenario: str):
       try:
           if not self.page.is_closed():
               timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
               path = self.DEBUG_ARTIFACTS_DIR / f"{timestamp}_{scenario}.png"
               self.page.screenshot(path=str(path))
               self.logger.info(f"Screenshot saved: {path}")
       except Exception as e:
           self.logger.error(f"Screenshot failed: {e}")

   # -----------------------------
   # Retry Logic
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
   # Element Helpers
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
   # Error Detection
   # -----------------------------
   def detect_error_page(self) -> Optional[str]:
       try:
           if self.page.is_closed():
               return "session_expired"
       except Exception:
           return "session_expired"

       try:
           content = self.page.content().lower()
       except Exception:
           return "session_expired"

       if "payment failed" in content:
           return "payment_failure"
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
   # Kendo UI / Wait Helpers
   # -----------------------------
   def _wait_for_click_blockers_to_clear(self, timeout_ms: int = 5000):
       """Wait for common modal/overlay blockers to stop intercepting clicks."""
       blocker_selectors = [
           ".k-overlay:visible",
           ".k-loading-mask:visible",
           "#loader.k-loading-image",
       ]
       try:
           end_time = self.page.evaluate("Date.now()") + timeout_ms
           while self.page.evaluate("Date.now()") < end_time:
               blockers_active = False
               for selector in blocker_selectors:
                   if self.page.locator(selector).count() > 0:
                       blockers_active = True
                       break
               if not blockers_active:
                   return
               self.page.wait_for_timeout(100)
       except Exception:
           pass

   def _scroll_and_click(self, locator, timeout_ms: int = 15000, retry: int = 2):
       """Ensure element is in view before clicking to reduce flaky interactions."""
       locator.wait_for(state="visible", timeout=timeout_ms)
       last_error = None
       for _ in range(max(1, retry)):
           try:
               self._wait_for_click_blockers_to_clear(timeout_ms=min(timeout_ms, 5000))
               locator.scroll_into_view_if_needed()
               locator.click(timeout=timeout_ms)
               return
           except Exception as ex:
               last_error = ex
               try:
                   self.page.wait_for_timeout(250)
               except Exception:
                   pass

       try:
           self._wait_for_click_blockers_to_clear(timeout_ms=min(timeout_ms, 3000))
           locator.scroll_into_view_if_needed()
           locator.click(timeout=timeout_ms, force=True)
           return
       except Exception as ex:
           last_error = ex
       raise last_error

   # ==================================================
   # DOM/JS Fallback
   # ==================================================
   def _dom_click_fallback(self, selector: str) -> Any:
       return self.page.evaluate(
           """
           (selector) => {
             const el = document.querySelector(selector);
             if (!el) return false;
             el.scrollIntoView({ block: 'center', inline: 'center' });
             el.click();
             return true;
           }
           """,
           selector,
       )

   def _js_fill_fallback(self, selector: str, value: str) -> Any:
       return self.page.evaluate(
           """
           ({ selector, value }) => {
             const el = document.querySelector(selector);
             if (!el) return false;
             el.focus();
             el.value = String(value);
             el.dispatchEvent(new Event('input', { bubbles: true }));
             el.dispatchEvent(new Event('change', { bubbles: true }));
             el.dispatchEvent(new Event('blur', { bubbles: true }));
             return true;
           }
           """,
           {"selector": selector, "value": value},
       )

   def safe_click_with_fallback(self, selector: str, timeout_ms: int = 10000) -> bool:
       def action(timeout):
           locator = self.page.locator(selector)
           if not locator.count():
               raise ElementNotFoundError(selector)
           locator.click(timeout=timeout)

       try:
           self._retry_with_backoff(action, timeout_ms=timeout_ms)
           return True
       except Exception:
           self._capture_debug_artifacts(f"click_failed_before_fallback_{selector}")
           ok = self._dom_click_fallback(selector)
           if not ok:
               raise
           return True

   def safe_fill_with_fallback(self, selector: str, value: str, timeout_ms: int = 10000) -> bool:
       def action(timeout):
           locator = self.page.locator(selector)
           if not locator.count():
               raise ElementNotFoundError(selector)
           locator.fill(value, timeout=timeout)

       try:
           self._retry_with_backoff(action, timeout_ms=timeout_ms)
           return True
       except Exception:
           self._capture_debug_artifacts(f"fill_failed_before_fallback_{selector}")
           ok = self._js_fill_fallback(selector, value)
           if not ok:
               raise
           return True

   # ==================================================
   # Kendo UI & Forms Support
   # ==================================================
   def _first_visible_candidate(self, candidates, timeout_ms: int = 5000):
      for candidate in candidates:
         try:
            candidate.wait_for(state="visible", timeout=timeout_ms)
            return candidate
         except Exception:
            continue
      return None

   def _click_first_interactable_candidate(self, candidates, timeout_ms: int = 5000):
      for candidate in candidates:
         try:
            self._scroll_and_click(candidate, timeout_ms=timeout_ms)
            return True
         except Exception:
            continue
      return False

   def _find_first_visible_locator(self, locator_factories, timeout_ms: int = 5000):
      for factory in locator_factories:
         try:
            locator = factory()
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
         except Exception:
            continue
      return None

   def _collect_visible_validation_messages(self):
      messages = []
      try:
         visible_errors = self.page.locator(
            ".field-validation-error:visible, .validation-summary-errors li:visible, .k-invalid-msg:visible"
         )
         count = visible_errors.count()
         for i in range(count):
            text = visible_errors.nth(i).inner_text().strip()
            if text:
               messages.append(text)
      except Exception:
         pass
      return sorted(set(messages))

   def _collect_invalid_required_fields(self):
      labels = []
      try:
         invalid_controls = self.page.locator("input[aria-invalid='true'], select[aria-invalid='true'], textarea[aria-invalid='true']")
         count = invalid_controls.count()
         for i in range(min(count, 30)):
            control = invalid_controls.nth(i)
            label = (control.get_attribute("aria-label") or control.get_attribute("name") or control.get_attribute("id") or "").strip()
            if label:
               labels.append(label)
      except Exception:
         pass
      return sorted(set(labels))

   def _get_visible_dialog_text(self):
      selectors = [
         ".k-dialog-wrapper:visible .k-dialog-content:visible",
         ".k-dialog-wrapper:visible .k-dialog-titleless:visible",
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

   def _click_visible_dialog_action(self):
      try:
         ok_button = self.page.get_by_role("button", name="OK")
         if ok_button.count() > 0 and ok_button.first.is_visible():
            self._scroll_and_click(ok_button.first, timeout_ms=5000)
            return True
      except Exception:
         pass
      
      selectors = [
         ".k-dialog-wrapper:visible button:has-text('Continue')",
         ".k-dialog-wrapper:visible .k-primary:has-text('Continue')",
         ".k-dialog-wrapper:visible button:has-text('OK')",
         ".k-dialog-wrapper:visible .k-primary:has-text('OK')",
         ".k-dialog-wrapper:visible button:has-text('Ok')",
         ".k-dialog-wrapper:visible button:has-text('Yes')",
         ".k-dialog-wrapper:visible .k-primary:has-text('Yes')",
         ".k-window:visible button:has-text('Continue')",
         ".k-window:visible .k-primary:has-text('Continue')",
         ".k-window:visible button:has-text('OK')",
         ".k-window:visible .k-primary:has-text('OK')",
         ".k-window:visible button:has-text('Ok')",
         ".k-window:visible .k-primary",
         ".k-dialog-wrapper:visible .k-primary",
      ]
      for selector in selectors:
         button = self.page.locator(selector).first
         try:
            if button.count() == 0:
               continue
            self._scroll_and_click(button, timeout_ms=5000)
            return True
         except Exception:
            continue
      return False

   def _retry_continue_click_via_dom(self):
      try:
         return bool(
            self.page.evaluate(
               """
               () => {
                   const btn = document.getElementById('btnSubmit');
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
               """
            )
         )
      except Exception:
         return False

   def _switch_to_latest_page_if_closed(self) -> bool:
      if not self.page.is_closed():
         return False
      try:
         open_pages = [p for p in self.page.context.pages if not p.is_closed()]
         if not open_pages:
            return False
         self.page = open_pages[-1]
         self.logger.warning("Active page was closed; switched to latest open page: %s", self.page.url)
         return True
      except Exception:
         return False

   def _ensure_payment_page_context(self, timeout_ms: int = 15000):
      payment_url_pattern = re.compile(r"Payment", re.I)

      if not self.page.is_closed() and payment_url_pattern.search(self.page.url):
         return

      for p in reversed(self.page.context.pages):
         if not p.is_closed() and payment_url_pattern.search(p.url):
            self.page = p
            return

      expect(self.page).to_have_url(payment_url_pattern, timeout=timeout_ms)
