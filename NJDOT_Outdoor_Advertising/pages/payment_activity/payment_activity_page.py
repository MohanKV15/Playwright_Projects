import re
import logging
from pathlib import Path
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage
from pages.core.kendo_utils import KendoUtils

logger = logging.getLogger(__name__)

class PaymentActivityPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Grid
        self.grid_container = page.locator(".k-grid").first
        self.no_records_msg = page.get_by_text("No records available.")
        
        # Navigation
        self.view_payment_btn = page.locator("#btnViewPayment")
        self.back_btn = page.get_by_role("button", name=" Back")
        
        # Filters
        self.time_period_dropdown = page.locator("#frmPaymentActivity .k-dropdown, #frmPaymentActivity .k-input").first
        
        # Actions & Pagination
        self.export_btn = page.get_by_role("button", name=re.compile("Export", re.I))
        self.next_btn = page.get_by_role("link", name="Go to the next page")
        self.last_btn = page.get_by_role("link", name="Go to the last page")
        self.page_input = page.get_by_role("spinbutton")

    # ---------- NAVIGATION ----------
    def open(self) -> None:
        """Opens the Payment Activity page from the sidebar."""
        logger.info("Opening Payment Activity panel...")
        
        self.view_payment_btn.click()
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_page_ready()
        
        # Verify a key header is visible to confirm navigation
        expect(self.page.get_by_role("heading", name=re.compile("Payment", re.I)).first).to_be_visible(timeout=10000)

    def go_back(self) -> None:
        """Clicks the back button to return to the dashboard."""
        logger.info("Clicking 'Back' button...")
        self.back_btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ---------- FILTER ----------
    def select_time_period(self, period_name: str) -> None:
        """Selects a specific time period from the Kendo dropdown (e.g. 'Last 6 months', '2025')."""
        logger.info(f"Selecting time period: '{period_name}'")
        self._wait_for_page_ready()
        KendoUtils.select_dropdown_option(self.page, self.time_period_dropdown, period_name)
        self._wait_for_page_ready()

    def test_first_three_time_periods(self, max_records: int = 3) -> None:
        """Selects the first N time periods from the dropdown one by one."""
        logger.info(f"Testing first {max_records} time periods in the dropdown...")
        self._wait_for_page_ready()
        
        for i in range(max_records):
            # Open dropdown
            try:
                self.time_period_dropdown.click(timeout=5000)
            except Exception:
                self.time_period_dropdown.click(force=True)
                
            # Get options list
            options = self.page.locator("li[role='option']")
            try:
                options.first.wait_for(state="visible", timeout=10000)
            except Exception:
                logger.warning("Dropdown options did not appear!")
                break
            
            # Stop if there are fewer options than we want to test
            count = options.count()
            if i >= count:
                break
                
            option_text = options.nth(i).inner_text()
            logger.info(f"Selecting time period [{i+1}/{min(max_records, count)}]: '{option_text}'")
            options.nth(i).click()
            
            self._wait_for_page_ready()


    # ---------- PAGINATION (BEST FIX) ----------
    def go_to_last_page(self) -> None:
        """Fast navigation to the last page using KendoUtils."""
        KendoUtils.fast_paginate_to_last_page(self.page, self.next_btn, self.last_btn, self.page_input, self._wait_for_loader)

    def export_activity(self) -> None:
        """Triggers the Export function, verifies the file downloads, and saves it locally."""
        logger.info("Exporting Payment Activity...")
        with self.page.expect_download() as download_info:
            try:
                self.export_btn.click(timeout=5000)
            except Exception:
                # Fallback to a broader button search if explicit export role isn't found
                self.page.locator("button, a").filter(has_text=re.compile("Export", re.I)).first.click(force=True)
        
        download = download_info.value
        
        # 1. Determine target directory
        download_dir = Path("downloads/payment_activity")
        
        # 2. Create the directory if it doesn't exist
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Clear old files to ensure only the latest one remains
        for existing_file in download_dir.iterdir():
            if existing_file.is_file():
                existing_file.unlink()
                
        # 4. Save the new file
        target_path = download_dir / download.suggested_filename
        download.save_as(target_path)
        
        logger.info(f"Successfully downloaded and saved file to: {target_path.absolute()}")

    def verify_records_present(self) -> bool:
        """Dynamically waits for either actual grid rows to render OR the empty-state message."""
        return KendoUtils.verify_grid_records(self.grid_container, self.no_records_msg)

    # ---------- WAITS ----------
    def _wait_for_page_ready(self) -> None:
        """Waits for the grid to appear and the AJAX loader to hide."""
        try:
            self.grid_container.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        self._wait_for_loader()
