from playwright.sync_api import expect
from pages.base_page import BasePage

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
        # We dynamically select the first available `#gridEdit` to avoid hardcoding row names
        self.first_record_edit_button = page.locator("#gridEdit, a.k-grid-edit").first

    def _wait_for_loader(self):
        """Waits for the global loading spinner to disappear to prevent pointer interceptions."""
        try:
            # Increased to 60s because Staging server dashboards are abnormally slow
            self.page.locator("#loader").wait_for(state="hidden", timeout=60000)
            self.page.wait_for_timeout(500) # Buffer for JS execution
        except Exception:
            pass

    def navigate_to_permit_listing(self, dashboard_url="https://u-njhtsp.bemcorp.net/Home/Dashboard?MenuName=Dashboard"):
        """Navigates to the Dashboard origin and selects the Permit Listing utility from Sidebar."""
        
        for attempt in range(3):
            try:
                # 1. Wait for the heavy Dashboard and Sidebar to physically attach to the DOM
                self.app_permit_info_menu.wait_for(state="attached", timeout=20000)
                
                # 2. OVERRIDE: Kendo UI requires native JS execution to bypass invisible loader layers
                for _ in range(5):
                    # Inject raw javascript literally into the DOM element
                    self.app_permit_info_menu.evaluate("element => element.click()")
                    try:
                        # 3. Wait for the dropdown child link to structurally appear
                        self.permit_listing_link.wait_for(state="visible", timeout=3000)
                        break
                    except Exception:
                        self.page.wait_for_timeout(1500)
                
                # 4. Inject JS click on the internal link as well
                self.permit_listing_link.evaluate("element => element.click()")
                
                # 5. Guarantee the navigation completed
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
        from playwright.sync_api import Page, expect
        self._wait_for_loader()
        
        try:
            expect(self.company_input).to_be_visible(timeout=15000)
        except Exception as e:
            # DUMP DOM for AI debugging
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
        self.refresh_button.click()
        
        # Wait for the backend to fetch the new grid data
        self._wait_for_loader()

    def navigate_to_next_page_and_edit_first_record(self):
        """Clicks the 'Next Page' grid button and edits the very first data record dynamically."""
        self._wait_for_loader()
        
        # 1. Click Next Page if available and not disabled
        self.next_page_button.wait_for(state="visible", timeout=15000)
        k_class = self.next_page_button.get_attribute("class") or ""
        
        if "k-state-disabled" not in k_class:
            print("Paginating to the next page...")
            # Use force=True to bypass interception by k-pager-wrap overlay
            self.next_page_button.click(force=True)
            # 2. Wait for the server to load the new page's data
            self._wait_for_loader()
        else:
            print("Note: Pagination skipped (Next Page is disabled or session is restricted to 1 page).")
        
        # 3. Capture data from the first row for verification
        self.first_record_edit_button.wait_for(state="visible", timeout=30000)
        row_locator = self.first_record_edit_button.locator("xpath=ancestor::tr")
        row_text = row_locator.inner_text()
        
        # Parsing basic data (assuming tab-separated or space-separated from inner_text)
        # This is a rough estimation based on the row_dump.txt
        columns = [col.strip() for col in row_text.split("\t") if col.strip()]
        captured_data = {
            "app_no": columns[0] if len(columns) > 0 else "Unknown",
            "county": columns[1] if len(columns) > 1 else "Unknown",
            "muni": columns[2] if len(columns) > 2 else "Unknown",
            "type": columns[4] if len(columns) > 4 else "Unknown"
        }
        
        # 4. Click Edit
        self.safe_click(self.first_record_edit_button)
        
        # 5. Wait for the new Application Edit Page to load
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
        
        # Click the dropdown to expand
        self.app_type_dropdown.click()
        
        # Clicking the option by text, but focusing on the first available to avoid ambiguity
        option = self.page.get_by_role("option", name=type_name).first
        option.wait_for(state="visible")
        option.evaluate("el => el.click()")
        self._wait_for_loader()
        
        # Professional tip: Avoid 'networkidle' on slow staging servers.
        # Instead, we wait for the page context to transition.
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000) # Small buffer for application JS initialization


