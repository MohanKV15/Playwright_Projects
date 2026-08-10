import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitListingPage(BasePage):
    """
    Page Object Model for Permit Listing in Staff Portal E-Permitting System.
    Provides robust search, pagination, record selection, and backend 500 error bypass capabilities.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Sidebar Navigation Locators ────────────────────────────────────────
        self.app_permit_info_menu = page.get_by_role("link", name="Application/Permit Info ")
        self.permit_listing_link = page.get_by_role("link", name="Permit Listing")

        # ── Add New Permit Locators ────────────────────────────────────────────
        self.add_new_permit_button = page.get_by_role("button", name=" Add New Permit").or_(
            page.locator("#btnAddNewPermit, button:has-text('Add New Permit')")
        ).first
        self.app_type_dropdown = page.get_by_label("Select Application Type").get_by_text("--Select Application Type--")
        self.modal_header = page.get_by_text("Select Application Type", exact=True)

        # ── Filter & Search Locators ───────────────────────────────────────────
        self.company_input = page.get_by_role("textbox", name="Applicant/Permittee").first
        self.refresh_button = page.get_by_role("button", name=re.compile(r"Refresh", re.I))

        # ── Grid Locators ──────────────────────────────────────────────────────
        self.next_page_button = page.get_by_role("link", name=re.compile(r"Go to the next page", re.I))
        self.first_record_edit_button = page.locator("#gridEdit, a.k-grid-edit").first

    def navigate_to_permit_listing(self, dashboard_url: str = "https://u-njhtsp.bemcorp.net/Home/Dashboard?MenuName=Dashboard") -> None:
        """Navigates to Dashboard and selects Permit Listing from sidebar menu."""
        logger.info("Navigating to Permit Listing.")
        for attempt in range(3):
            try:
                self.app_permit_info_menu.wait_for(state="attached", timeout=20000)
                for _ in range(5):
                    self.app_permit_info_menu.evaluate("el => el.click()")
                    try:
                        self.permit_listing_link.wait_for(state="visible", timeout=3000)
                        break
                    except Exception:
                        self.page.wait_for_timeout(1500)

                self.permit_listing_link.evaluate("el => el.click()")
                self.page.wait_for_load_state("domcontentloaded")
                self._wait_for_loader()
                return
            except Exception as e:
                if attempt == 2:
                    raise e
                logger.warning(f"Sidebar navigation retry {attempt + 1}/3... Error: {e}")
                self.page.goto(dashboard_url, timeout=45000, wait_until="domcontentloaded")
                self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Verifies search form input is visible and interactive."""
        self.verify_search_form_ready()

    def verify_and_close_add_new_modal(self) -> None:
        """Opens Add New Permit modal, verifies layout, and closes it."""
        self.open_add_new_permit_modal()
        close_btn = self.page.locator(".k-window:visible a.k-window-action, .k-window:visible .k-i-close, .k-window:visible button.close, [role='dialog']:visible button:has-text('Close')").first
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click()
        else:
            self.page.keyboard.press("Escape")
        self._wait_for_loader()

    def verify_search_form_ready(self) -> None:
        """Verifies search form input is visible and interactive."""
        self._wait_for_loader()
        expect(self.company_input).to_be_visible(timeout=15000)

    def search_by_company(self, company_name: str) -> None:
        """Fills out company search filter and clicks Refresh button."""
        self._wait_for_loader()
        self.company_input.wait_for(state="visible", timeout=15000)
        self.company_input.fill(company_name)

        try:
            with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000):
                self.refresh_button.click()
        except Exception:
            self.refresh_button.click()

        self._wait_for_loader()

    def navigate_to_next_page_and_edit_first_record(self) -> dict:
        """Paginates grid to next page if enabled and edits 1st record."""
        self._wait_for_loader()
        if self.next_page_button.is_visible():
            k_class = self.next_page_button.get_attribute("class") or ""
            if "k-state-disabled" not in k_class:
                self.js_click(self.next_page_button)
                self._wait_for_loader()

        target_btn = self.first_record_edit_button
        row_locator = target_btn.locator("xpath=ancestor::tr")
        app_no = "Unknown"
        if row_locator.count() > 0:
            cols = [c.strip() for c in row_locator.inner_text().split("\t") if c.strip()]
            if len(cols) > 0 and cols[0]:
                app_no = cols[0]

        self.js_click(target_btn)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()
        return {"status": "success", "app_no": app_no}

    def open_add_new_permit_modal(self) -> None:
        """Clicks Add New Permit button and waits for modal header with retry mechanism."""
        self._wait_for_loader()
        self.add_new_permit_button.wait_for(state="visible", timeout=15000)
        for attempt in range(3):
            try:
                self.js_click(self.add_new_permit_button)
                self.modal_header.wait_for(state="visible", timeout=5000)
                return
            except Exception:
                self.page.wait_for_timeout(1000)

        expect(self.modal_header).to_be_visible(timeout=15000)

    def select_application_type(self, type_name: str) -> None:
        """Selects application type from modal dropdown."""
        self._wait_for_loader()
        self.js_click(self.app_type_dropdown)
        option = self.page.get_by_role("option", name=type_name).first
        option.wait_for(state="visible", timeout=10000)
        self.js_click(option)
        self._wait_for_loader()

    def is_server_error_page(self) -> bool:
        """Checks if current page displays a server 500 NullPointer error page."""
        try:
            self.page.wait_for_timeout(1000)
            text = self.page.inner_text("body")
            if "Object reference not set" in text or "Please Contact Administrator" in text or "Server Error" in text or "Message :" in text:
                logger.warning("Detected server 500 error page ('Object reference not set to an instance of an object').")
                return True
        except Exception:
            pass
        return False

    def search_and_edit_permit(self, company_name: str = "HCL", record_index: int = None, max_retries: int = 5) -> dict:
        """
        Navigates to permit listing, searches by company name, and edits a valid matching record.
        If a record opens a 500 error page ('Object reference not set'), automatically tries the next record.
        """
        if record_index is None:
            import os
            worker_str = os.getenv("PYTEST_XDIST_WORKER", "gw0")
            try:
                record_index = int(worker_str.replace("gw", ""))
            except Exception:
                record_index = 0

        for attempt in range(max_retries):
            try:
                self.navigate_to_permit_listing()
                self.search_by_company(company_name)

                edit_buttons = self.page.locator("#gridEdit, a.k-grid-edit")
                count = edit_buttons.count()

                if count == 0:
                    logger.warning(f"No records found for company '{company_name}'.")
                    return {"status": "no_records", "app_no": None}

                target_idx = (record_index + attempt) % count
                btn = edit_buttons.nth(target_idx)
                row_locator = btn.locator("xpath=ancestor::tr")
                app_no = "Unknown"
                if row_locator.count() > 0:
                    cols = [c.strip() for c in row_locator.inner_text().split("\t") if c.strip()]
                    if len(cols) > 0 and cols[0]:
                        app_no = cols[0]

                logger.info(f"Attempting to edit record {attempt + 1}: App No '{app_no}'")
                self.js_click(btn)
                self.page.wait_for_load_state("domcontentloaded")
                self._wait_for_loader()

                if self.is_server_error_page():
                    logger.warning(f"Record '{app_no}' triggered server 500 error page. Retrying with next record...")
                    continue

                return {"status": "success", "app_no": app_no}

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

        raise RuntimeError(f"Could not open a valid permit record after {max_retries} attempts.")
