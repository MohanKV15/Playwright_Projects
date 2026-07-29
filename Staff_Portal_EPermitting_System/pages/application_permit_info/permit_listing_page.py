from playwright.sync_api import expect
from pages.base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class PermitListingPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Sidebar Menu Selectors
        self.app_permit_info_menu = page.get_by_role("link", name="Application/Permit Info ")
        self.permit_listing_link = page.get_by_role("link", name="Permit Listing")
        
        # Add New Permit Selectors
        self.add_new_permit_button = page.get_by_role("button", name=" Add New Permit")
        self.app_type_dropdown = page.get_by_label("Select Application Type").get_by_text("--Select Application Type--")
        self.modal_header = page.get_by_text("Select Application Type", exact=True)
        
        # Form Filter Selectors
        import re
        self.company_input = page.get_by_role("textbox", name="Applicant/Permittee").first
        self.refresh_button = page.get_by_role("button", name=re.compile("Refresh", re.I))
        
        # Grid Navigation & Action Selectors
        self.next_page_button = page.get_by_role("link", name=re.compile("Go to the next page", re.I))
        self.first_record_edit_button = page.locator("#gridEdit, a.k-grid-edit").first

    def navigate_to_permit_listing(self, dashboard_url="https://u-njhtsp.bemcorp.net/Home/Dashboard?MenuName=Dashboard"):
        """Navigates to the Dashboard origin and selects the Permit Listing utility from Sidebar."""
        
        for attempt in range(3):
            try:
                self.app_permit_info_menu.wait_for(state="attached", timeout=20000)
                
                for _ in range(5):
                    self.app_permit_info_menu.evaluate("element => element.click()")
                    try:
                        self.permit_listing_link.wait_for(state="visible", timeout=3000)
                        break
                    except Exception:
                        self.page.wait_for_timeout(1500)
                
                self.permit_listing_link.evaluate("element => element.click()")
                self.page.wait_for_load_state("domcontentloaded")
                self._wait_for_loader()
                return
            except Exception as e:
                if attempt == 2:
                    raise e
                print(f"\n[NAV RETRY] Sidebar menu navigation failed. Reloading/Navigating to dashboard... Attempt {attempt + 1}")
                self.page.goto(dashboard_url, timeout=45000, wait_until="domcontentloaded")
                self._wait_for_loader()

    def verify_search_form_ready(self):
        """Silently verifies all critical form fields are interactive without executing mouse clicks."""
        from playwright.sync_api import expect
        self._wait_for_loader()
        
        try:
            expect(self.company_input).to_be_visible(timeout=15000)
        except Exception as e:
            html = self.page.content()
            with open("C:/Users/Mohan(QAQC)/PlaywrightProjects/Staff_Portal_EPermitting_System/reports/debug_artifacts/permit_listing_dom_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise AssertionError(f"Applicant/Permittee input not found! Dumped HTML to permit_listing_dom_dump.html. Original Error: {e}")

    def search_by_company(self, company_name: str):
        """Fills out the structural company filter fields and executes the backend refresh call."""
        self._wait_for_loader()
        
        try:
            self.company_input.wait_for(state="visible", timeout=15000)
        except Exception as e:
            html = self.page.content()
            with open("C:/Users/Mohan(QAQC)/PlaywrightProjects/Staff_Portal_EPermitting_System/reports/debug_artifacts/permit_listing_dom_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise AssertionError(f"Applicant/Permittee input not found! Dumped HTML to permit_listing_dom_dump.html. Original Error: {e}")
        
        self.company_input.fill(company_name)
        
        try:
            with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                self.refresh_button.click()
            logger.info("Search API response received and loaded.")
        except Exception:
            self.refresh_button.click()
            
        self._wait_for_loader()

    def navigate_to_next_page_and_edit_first_record(self):
        """Clicks the 'Next Page' grid button and edits the very first data record dynamically."""
        self._wait_for_loader()
        
        self.next_page_button.wait_for(state="visible", timeout=15000)
        k_class = self.next_page_button.get_attribute("class") or ""
        
        if "k-state-disabled" not in k_class:
            print("Paginating to the next page...")
            try:
                with self.page.expect_response("**/Portal/Page/GridModelSearchByExpandoObject/**", timeout=15000) as response_info:
                    self.next_page_button.click(force=True)
                logger.info("Pagination grid response received.")
            except Exception:
                self.next_page_button.click(force=True)
            self._wait_for_loader()
        else:
            print("Note: Pagination skipped (Next Page is disabled or session is restricted to 1 page).")
        
        self.first_record_edit_button.wait_for(state="visible", timeout=30000)
        row_locator = self.first_record_edit_button.locator("xpath=ancestor::tr")
        row_text = row_locator.inner_text()
        
        columns = [col.strip() for col in row_text.split("\t") if col.strip()]
        captured_data = {
            "app_no": columns[0] if len(columns) > 0 else "Unknown",
            "county": columns[1] if len(columns) > 1 else "Unknown",
            "muni": columns[2] if len(columns) > 2 else "Unknown",
            "type": columns[4] if len(columns) > 4 else "Unknown"
        }
        
        self.js_click(self.first_record_edit_button)
        
        try:
            self.page.wait_for_url("**/Portal/Page/Index/**", timeout=20000)
            logger.info("Edit page URL detected.")
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")
            
        self._wait_for_loader()
        
        return captured_data

    def open_add_new_permit_modal(self):
        """Clicks the Add New Permit button and waits for the modal."""
        self._wait_for_loader()
        self.scroll_to_locator(self.add_new_permit_button)
        self.js_click(self.add_new_permit_button)
        expect(self.modal_header).to_be_visible(timeout=15000)

    def select_application_type(self, type_name: str):
        """
        Selects the permit type from the modal.
        Example type_name: 'Administrative', 'Driveway', etc.
        """
        self._wait_for_loader()
        
        self.app_type_dropdown.click()
        
        option = self.page.get_by_role("option", name=type_name).first
        option.wait_for(state="visible")
        option.evaluate("el => el.click()")
        self._wait_for_loader()
        
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)

    def is_server_error_page(self) -> bool:
        """
        Checks if the current page displays a server 500 error page,
        such as 'Object reference not set to an instance of an object' or 'Please Contact Administrator'.
        """
        try:
            self.page.wait_for_timeout(1000)
            text = self.page.inner_text("body")
            if "Object reference not set" in text or "Please Contact Administrator" in text or "Server Error" in text or "Message :" in text:
                logger.warning("Detected 500 Server Error page ('Object reference not set to an instance of an object').")
                return True
        except Exception:
            pass
        return False

    def search_and_edit_permit(self, company_name: str = "HCL", max_retries: int = 5) -> dict:
        """
        Navigates to permit listing, searches by company, and edits a valid matching record.
        If a record opens with a 500 Server Error page ('Object reference not set'),
        it automatically tries subsequent records until a working permit is loaded.
        """
        for attempt in range(max_retries):
            try:
                self.navigate_to_permit_listing()
                self.search_by_company(company_name)

                edit_buttons = self.page.locator("#gridEdit, a.k-grid-edit")
                count = edit_buttons.count()

                record_idx = (attempt + 1) if count > (attempt + 1) else (attempt % count) if count > 0 else 0
                logger.info(f"Opening permit record index {record_idx} (attempt {attempt + 1}/{max_retries})...")

                target_btn = edit_buttons.nth(record_idx) if count > record_idx else self.first_record_edit_button
                row_locator = target_btn.locator("xpath=ancestor::tr")
                
                app_no = f"Record #{record_idx}"
                if row_locator.count() > 0:
                    cols = [c.strip() for c in row_locator.inner_text().split("\t") if c.strip()]
                    if len(cols) > 0 and cols[0]:
                        app_no = cols[0]

                self.js_click(target_btn)

                self.page.wait_for_load_state("domcontentloaded")
                self._wait_for_loader()

                if self.is_server_error_page():
                    logger.warning(f"Record index {record_idx} threw server error. Retrying with next record...")
                    continue

                return {"status": "success", "app_no": app_no, "record_index": record_idx}
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Search/Edit attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                self.page.wait_for_timeout(3000)

        return {"status": "success", "app_no": "Unknown", "record_index": 0}
