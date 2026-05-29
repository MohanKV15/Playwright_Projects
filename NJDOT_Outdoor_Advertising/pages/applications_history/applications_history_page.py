import re
import logging
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class ApplicationsHistoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Grid
        self.grid_container = page.locator(".k-grid").first
        self.no_records_msg = page.get_by_text("No records available.")
        
        # Navigation
        self.view_apps_btn = page.locator("#btnViewSubmittedApps")
        self.back_btn = page.get_by_role("button", name=" Back")
        
        # Search & Export
        self.search_input = page.locator("#searchcriteria")
        self.search_btn = page.get_by_role("button", name=" Search")
        self.export_btn = page.get_by_role("button", name=" Export")
        
        # Pagination
        self.next_btn = page.get_by_role("link", name="Go to the next page")

    # ---------- NAVIGATION ----------
    def open(self) -> None:
        """Opens the Applications History page from the sidebar."""
        logger.info("Opening Applications History panel...")
        
        # Click the link and wait for navigation
        self.view_apps_btn.click()
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_page_ready()
        
        # Verify a key header is visible to confirm navigation
        expect(self.page.get_by_role("heading", name="Applications History").first).to_be_visible(timeout=10000)

    def go_back(self) -> None:
        """Clicks the back button to return to the dashboard."""
        logger.info("Clicking 'Back' button...")
        self.back_btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ---------- SEARCH ----------
    def get_first_record_text(self) -> str:
        """Extracts the text from the first cell of the first row to use for dynamic searching."""
        logger.info("Extracting dynamic search value from the first record...")
        self._wait_for_page_ready()
        
        first_row = self.grid_container.locator("tbody tr").first
        first_row.wait_for(state="visible", timeout=15000)
        
        # Grab text from the first column (e.g., Application/Permit Number)
        text = first_row.locator("td").first.inner_text().strip()
        logger.info(f"Dynamic search value extracted: '{text}'")
        return text

    def perform_search(self, criteria: str) -> None:
        """Fills the search box and triggers a search."""
        logger.info(f"Searching Applications History for: '{criteria}'")
        self.search_input.click()
        self.search_input.fill(criteria)
        self.search_btn.click()
        self._wait_for_page_ready()
        
    def clear_search(self) -> None:
        """Clears the search box to view all records."""
        logger.info("Clearing search criteria...")
        self.search_input.click()
        self.search_input.fill("")
        self.search_btn.click()
        self._wait_for_page_ready()

    # ---------- PAGINATION & EXPORT ----------
    def validate_pagination(self) -> None:
        """Paginates through the Kendo grid until the end is reached."""
        logger.info("Paginating to the end of the Applications History grid...")
        page_num = 1
        while True:
            self._wait_for_loader()
            if not self.next_btn.is_visible():
                logger.info("No pagination available.")
                break
                
            if "k-state-disabled" in (self.next_btn.get_attribute("class") or ""):
                logger.info(f"Reached final page (Page {page_num})")
                break
            try:
                self.next_btn.click(timeout=5000)
            except Exception:
                self.page.wait_for_timeout(500)
                self.next_btn.click(force=True)
            page_num += 1
            self._wait_for_page_ready()

    def export_history(self) -> None:
        """Triggers the Export function, verifies the file downloads, and saves it locally."""
        logger.info("Exporting Applications History...")
        with self.page.expect_download() as download_info:
            self.export_btn.click()
        
        download = download_info.value
        
        # 1. Determine target directory
        from pathlib import Path
        download_dir = Path("downloads/applications_history")
        
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
        logger.info("Verifying grid records...")
        grid_rows = self.grid_container.locator("tbody tr")
        try:
            grid_rows.first.or_(self.no_records_msg).wait_for(state="visible", timeout=15000)
        except Exception as e:
            raise AssertionError(f"❌ Grid failed to load entirely. Neither records nor empty-state appeared. {e}")

        if self.no_records_msg.is_visible():
            logger.info("Grid is empty (No records available).")
            return False

        count = grid_rows.count()
        logger.info(f"Found {count} records on current page.")
        if count == 0:
            return False
            
        return True

    # ---------- WAITS ----------
    def _wait_for_page_ready(self) -> None:
        """Waits for the grid to appear and the AJAX loader to hide."""
        try:
            self.grid_container.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        self._wait_for_loader()
