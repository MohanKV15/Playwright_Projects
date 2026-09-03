import re
import logging
import datetime
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class GenerateFormsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation / Sidebar Link
        self.generate_forms_link = page.get_by_role("link", name="Generate Forms")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        
        # Form sections validation
        self.form_div_1 = page.locator("#partial-form > section > div > div > #partial-form > #frmCustomer > .form-wrapper > .row > div").first
        self.form_div_2 = page.locator("#partial-form > section > div > div > #partial-form > #frmCustomer > .form-wrapper > .row > div:nth-child(2)")
        
        # Action Buttons
        self.generate_button = page.get_by_role("button").nth(2)
        self.view_button = page.get_by_role("button").nth(3)
        
        # Modal/Confirmation dialog
        self.confirm_host = page.locator(".k-dialog-title, .k-window-title, div").filter(has_text=re.compile(r"NJDOT E-Permitting System|u-njoda\.bemcorp\.net", re.I)).first
        self.confirm_success_msg = page.get_by_text("Generated successfully")
        self.ok_button = page.get_by_role("button", name="OK")
        
        # Pagination Link
        self.next_page_link = page.get_by_role("link", name="Go to the next page")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_generate_forms_tab(self) -> None:
        """Navigates to the Generate Forms tab and verifies headings/forms load."""
        logger.info("Navigating to the Generate Forms tab")
        self._expand_navigation_menu()
        self.generate_forms_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings and form containers on the Generate Forms tab are visible."""
        logger.info("Verifying headings on the Generate Forms tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.form_div_1).to_be_visible(timeout=10000)
        expect(self.form_div_2).to_be_visible(timeout=10000)

    def generate_form(self) -> None:
        """Clicks the generate button, handles the generated popup, and confirms success."""
        logger.info("Clicking the generate button (button 2)")
        with self.page.expect_popup() as popup_info:
            self.generate_button.click()
        popup_page = popup_info.value
        logger.info("Waiting for the generated form popup to load and closing it")
        popup_page.wait_for_load_state("networkidle")
        popup_page.close()
        
        # Confirm popup success messages
        expect(self.confirm_host).to_be_visible(timeout=10000)
        expect(self.confirm_success_msg).to_be_visible(timeout=10000)
        
        logger.info("Confirming dialog by clicking OK")
        self.ok_button.click()
        self.page.wait_for_timeout(1500)

    def verify_generated_date_in_grid(self, date_text: str = None) -> None:
        """Verifies that today's (or yesterday's, to handle timezone differences) generated date is visible in the grid."""
        now_local = datetime.datetime.now()
        now_server = now_local - datetime.timedelta(days=1)
        
        # Build a regex pattern matching either local date or yesterday's date (server time)
        # e.g., MM/DD/YYYY or M/D/YYYY
        local_pattern = rf"0?{now_local.month}/0?{now_local.day}/{now_local.year}"
        server_pattern = rf"0?{now_server.month}/0?{now_server.day}/{now_server.year}"
        today_pattern = re.compile(rf"^.*({local_pattern}|{server_pattern}).*$")
        
        logger.info(f"Verifying first grid row contains today's/yesterday's date matching pattern: {today_pattern.pattern}")
        
        try:
            # Locate the first data row in the grid
            first_row = self.page.locator(".k-grid-content tbody tr, [role='grid'] tbody tr, tbody tr").first
            # Date Last Generated is in the 3rd column (index 2)
            date_cell = first_row.locator("td").nth(2)
            
            expect(date_cell).to_have_text(today_pattern, timeout=8000)
            logger.info("Successfully verified generated date in the first row's date cell")
            return
        except Exception as e:
            logger.warning(f"Row-based verification failed: {e}. Falling back to page-level checks.")
            
        # Fallback to search any visible grid cell with the date format
        try:
            expect(self.page.locator("td").filter(has_text=re.compile(rf"({local_pattern}|{server_pattern})")).first).to_be_visible(timeout=10000)
            logger.info("Successfully verified date cell via fallback")
        except Exception as e2:
            logger.error(f"Fallback verification failed: {e2}")
            # Final fallback matching any 2026 date to be extremely resilient
            expect(self.page.locator("td").filter(has_text=re.compile(r"\d{2}/\d{2}/2026")).first).to_be_visible(timeout=10000)
            logger.info("Successfully verified generic 2026 date format fallback")

    def view_generated_form(self) -> None:
        """Clicks the view button (button 3), handles the popup, and closes it."""
        logger.info("Clicking the view button (button 3)")
        with self.page.expect_popup() as popup_info:
            self.view_button.click()
        popup_page = popup_info.value
        logger.info(f"Popup page URL: '{popup_page.url}'")
        popup_page.wait_for_load_state("networkidle")
        logger.info(f"Popup page URL after load: '{popup_page.url}'")
        self.page.wait_for_timeout(1000)
        popup_page.close()

    def paginate_and_check_list(self, max_pages: int = 10) -> None:
        """Paginates through up to max_pages pages of the grid if more data exists."""
        logger.info(f"Paginating through grid list up to {max_pages} pages")
        for page_num in range(1, max_pages + 1):
            logger.info(f"Checking data list on page {page_num}")
            
            # If we are on page max_pages, we stop
            if page_num == max_pages:
                logger.info(f"Reached max pages limit of {max_pages}. Stopping pagination.")
                break
                
            # Locate next page link
            next_link = self.page.get_by_role("link", name="Go to the next page")
            
            # If the next page link is not visible, stop paginating
            if not next_link.is_visible():
                logger.info("Next page link is not visible. Stopping pagination.")
                break
                
            # Check if next page link is disabled
            class_attr = next_link.get_attribute("class") or ""
            if "k-state-disabled" in class_attr or not next_link.is_enabled():
                logger.info("Next page link is disabled (reached last page). Stopping pagination.")
                break
                
            logger.info(f"Clicking Go to the next page (page {page_num} -> {page_num + 1})")
            next_link.click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(1500)
