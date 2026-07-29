import logging
import datetime
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitDetailsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Navigation / Tabs
        self.permit_details_tab = page.get_by_role("link", name="Permit Details")
        
        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.permit_details_heading = page.get_by_role("heading", name="Permit Details")
        self.documents_log_heading = page.locator("#divfrmLog, #LogDynGridLoad, h1, h2, h3, h4, h5, h6").get_by_text("Documents and Log").first
        
        # Form Selectors
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save")
        
    def scroll_to_element(self, locator: Locator) -> None:
        """Scrolls an element into view smoothly using BasePage scroll utility."""
        logger.info(f"Scrolling element into view: {locator}")
        try:
            locator.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Scroll into view note: {e}")

    def scroll_to_documents_log(self) -> None:
        """Scrolls the viewport smoothly down to the Documents and Log section."""
        logger.info("Scrolling viewport down to Documents and Log section.")
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Scroll to Documents and Log section note: {e}")

    def navigate_to_permit_details(self) -> None:
        """Transitions to the Permit Details tab."""
        logger.info("Navigating to Permit Details tab.")
        self._wait_for_loader()
        self.scroll_to_element(self.permit_details_tab)
        self.js_click(self.permit_details_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout and headers on the Permit Details page."""
        logger.info("Verifying Permit Details page initial layout.")
        expect(self.permit_details_heading).to_be_visible(timeout=15000)

    def set_all_permit_dates(self) -> None:
        """Sets all date inputs in the permit form to the current date."""
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        logger.info(f"Setting all permit date fields to '{current_date_str}'")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"], input[id*="Date"], input[name*="Date"], .k-datepicker input').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                        $(this).trigger("change");
                    }}
                }});
            }}
        """)
        self.page.wait_for_timeout(500)

    def _select_valid_dropdown_option(self, preferred_text: str = "") -> None:
        """Selects preferred option by text or the first non-placeholder option in a visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible", timeout=5000)
        list_box = self.page.locator("[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible").last
        options = list_box.locator("li, [role='option'], .k-item")
        
        # 1. Try preferred text if provided
        if preferred_text:
            matching = options.filter(has_text=re.compile(rf"{re.escape(preferred_text)}", re.I)).first
            if matching.count() > 0 and matching.is_visible():
                self.js_click(matching)
                self.page.wait_for_timeout(500)
                self._wait_for_loader()
                return

        # 2. Filter out placeholders starting with '--' or 'Select'
        count = options.count()
        for i in range(count):
            txt = options.nth(i).inner_text().strip()
            if txt and not txt.startswith("--") and not txt.lower().startswith("select"):
                logger.info(f"Selecting valid dropdown option '{txt}' at index {i}")
                self.js_click(options.nth(i))
                self.page.wait_for_timeout(500)
                self._wait_for_loader()
                return
                
        # 3. Fallback: index 1 if count > 1 else index 0
        if count > 1:
            self.js_click(options.nth(1))
        else:
            self.js_click(options.first)
            
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    def fill_permit_details(self, comments: str = "test permit details", **kwargs) -> None:
        """Fills out the Permit Details form by selecting valid options in each dropdown, setting dates, and saving."""
        logger.info("Filling out Permit Details form.")
        self._wait_for_loader()
        
        # Select Dropdowns inside #frmPermit
        dropdowns = self.page.locator("#frmPermit span.k-widget.k-dropdown:visible, #frmPermit span[role='listbox']:visible, span.k-widget.k-dropdown:visible")
        count = dropdowns.count()
        logger.info(f"Found {count} dropdowns inside Permit Details form.")
        
        for i in range(count):
            self.js_click(dropdowns.nth(i))
            self._select_valid_dropdown_option("No")
            
        # Set all DateFields to current date via JS injection
        self.set_all_permit_dates()
        
        # Fill Comments text
        if self.comments_input.is_visible():
            self.scroll_to_element(self.comments_input)
            self.js_click(self.comments_input)
            self.comments_input.fill(comments)
            
        # Click Save
        logger.info("Saving Permit Details.")
        self.scroll_to_element(self.save_button)
        try:
            self.save_button.click(timeout=3000)
        except Exception:
            self.dispatch_bubble_click(self.save_button)
        self._wait_for_loader()
        
        # Handle potential Kendo popup alert
        try:
            self.ok_button.wait_for(state="visible", timeout=3000)
            self.js_click(self.ok_button)
            self._wait_for_loader()
        except Exception:
            pass
            
        # Scroll down to Documents and Log section and verify
        self.scroll_to_documents_log()
        expect(self.attach_document_button.or_(self.add_communication_button).first).to_be_visible(timeout=15000)
        logger.info("Permit Details added, saved, and Documents & Log section verified successfully.")

    def attach_document(self, file_path: str, subject: str = "test", description: str = "test") -> None:
        """Scrolls viewport down to Documents and Log section before attaching a document."""
        self.scroll_to_documents_log()
        super().attach_document(file_path, subject, description)

    def add_communication(self, subject: str = "testingd", description: str = "one") -> None:
        """Scrolls viewport down to Documents and Log section before adding a communication entry."""
        self.scroll_to_documents_log()
        super().add_communication(subject, description)

    def create_package_and_verify(self) -> None:
        """Scrolls viewport down to Documents and Log section before creating a package."""
        self.scroll_to_documents_log()
        super().create_package_and_verify()
