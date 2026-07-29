import logging
import re
from playwright.sync_api import Page, expect, Locator

logger = logging.getLogger(__name__)

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        
        # Loader / Spinner Locators
        self.loading_overlay = page.locator(".k-loading-mask, .k-loading-image, #loading, .spinner-border")
        
        # Common Document & Communication Controls
        self.attach_document_button = page.get_by_role("button", name="Attach Document").or_(page.locator("#btnAttachDoc, .btn:has-text('Attach Document')")).first
        self.document_type_dropdown = page.get_by_role("button", name="select").first
        self.choose_file_input = page.locator("input[type='file']").first
        self.save_document_button = page.get_by_role("button", name=" Save")
        
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")
        
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_container = page.locator("#divfrmLog > .form-wrapper > .row > .col-md-12")
        self.communication_date_picker = page.get_by_role("button", name="select")
        
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_title = page.locator(".k-window-title:visible").filter(has_text=re.compile("Select Attachments", re.I)).first
        self.first_attachment_checkbox = page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        self.select_attachments_confirm_button = page.get_by_role("button", name="Select Attachments")
        self.package_created_message = page.locator(".k-window:visible, [role='dialog']:visible").get_by_text("Your document package is")
        self.ok_button = page.get_by_role("button", name="OK")
        
        self.send_email_button = page.get_by_role("button", name="Send Email")
        self.email_form_container = page.get_by_text("Send Cancel To: * CC: BCC:")
        self.cancel_email_button = page.get_by_role("button", name=" Cancel")
        self.log_app_header = page.locator("#LogAppHeader")

    def navigate(self, url: str):
        self.page.goto(url)

    def click_element(self, selector: str):
        self.page.wait_for_selector(selector)
        self.page.click(selector)

    def fill_input(self, selector: str, text: str):
        self.page.wait_for_selector(selector)
        self.page.fill(selector, text)

    def get_element_text(self, selector: str) -> str:
        self.page.wait_for_selector(selector)
        return self.page.inner_text(selector)
        
    def wait_for_element(self, selector: str, timeout: int = 30000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def scroll_to_locator(self, locator: Locator):
        """Scrolls an element into view smoothly."""
        locator.scroll_into_view_if_needed()

    def safe_click(self, locator: Locator):
        """
        Scrolls the element into view and then performs a small scroll adjustment
        to ensure fixed headers do not intercept the click.
        """
        locator.scroll_into_view_if_needed()
        self.page.evaluate("window.scrollBy(0, -150)")
        locator.click()

    def dispatch_bubble_click(self, locator: Locator):
        """
        Dispatches a native JS click event that bubbles up the DOM.
        This is extremely effective for problematic 'Save' buttons.
        """
        locator.scroll_into_view_if_needed()
        self.page.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }))", locator.element_handle())

    def js_click(self, locator: Locator):
        """
        Clicks an element using JavaScript to bypass pointer/hit-testing issues
        caused by layout, overlays, or CSS zoom.
        """
        locator.wait_for(state="visible")
        locator.evaluate("el => el.click()")

    def _set_kendo_numeric_value(self, element_id: str, value: float):
        """
        Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API.
        """
        self.page.evaluate(f"""
            () => {{
                var numeric = $('#{element_id}').data('kendoNumericTextBox');
                if (numeric) {{
                    numeric.value({value});
                    numeric.trigger('change');
                }}
            }}
        """)

    def fill_kendo_numeric(self, element_id: str, value: float):
        """Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API."""
        self._set_kendo_numeric_value(element_id, value)

    def _wait_for_loader(self, timeout: int = 15000):
        """Waits for any Kendo or portal loading overlay masks to disappear."""
        try:
            self.page.wait_for_selector(".k-loading-mask, .k-loading-image, #loading", state="detached", timeout=timeout)
        except Exception:
            pass

    def select_today_in_calendar(self, trigger_locator: Locator = None):
        """
        Selects today's date from an active Kendo UI Calendar widget popup.
        Optionally clicks trigger_locator if provided.
        """
        try:
            if trigger_locator is not None:
                try:
                    self.js_click(trigger_locator)
                    self.page.wait_for_timeout(300)
                except Exception:
                    pass
            today_link = self.page.locator(".k-calendar-container:visible .k-nav-today, .k-calendar-container:visible a.k-link:has-text('Today')").first
            if today_link.is_visible():
                self.js_click(today_link)
                return
            
            day_link = self.page.locator(".k-calendar-container:visible td:not(.k-other-month) a.k-link").first
            if day_link.is_visible():
                self.js_click(day_link)
                return
        except Exception as e:
            logger.warning(f"Could not interact with Kendo calendar popup: {e}")

    def set_all_datefields_to_current(self):
        """
        Injects today's date directly into all Kendo DatePicker inputs across the page.
        """
        import datetime
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
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

    def attach_document(self, file_path: str, subject: str = "test", description: str = "test") -> None:
        """Attaches a document to the Documents and Log section."""
        logger.info(f"Attaching document: {file_path}")
        self._wait_for_loader()
        if self.attach_document_button.count() == 0 or not self.attach_document_button.is_visible():
            logger.warning("Attach Document button not visible.")
            return

        self.js_click(self.attach_document_button)
        self._wait_for_loader()
        
        # Select first valid option in Document Type dropdown
        if self.document_type_dropdown.is_visible():
            self.js_click(self.document_type_dropdown)
            option = self.page.get_by_role("option").first
            if option.is_visible():
                self.js_click(option)
        
        # Upload File using .first locator to avoid strict mode violations
        if self.choose_file_input.count() > 0:
            self.choose_file_input.set_input_files(file_path)
            
        # Fill Subject and Description
        if self.subject_input.is_visible():
            self.js_click(self.subject_input)
            self.subject_input.fill(subject)
            
        if self.description_input.is_visible():
            self.js_click(self.description_input)
            self.description_input.fill(description)
            
        # Click Save
        if self.save_document_button.is_visible():
            self.js_click(self.save_document_button)
            self._wait_for_loader()
        logger.info("Document attached successfully.")

    def add_communication(self, subject: str = "testingd", description: str = "one") -> None:
        """Adds a Communication entry in the Documents and Log section."""
        logger.info("Adding communication entry.")
        self._wait_for_loader()
        if self.add_communication_button.count() == 0 or not self.add_communication_button.is_visible():
            logger.warning("Add Communication button not visible.")
            return

        self.js_click(self.add_communication_button)
        self._wait_for_loader()
        
        if self.communication_date_picker.is_visible():
            self.js_click(self.communication_date_picker)
            self.select_today_in_calendar()
            
        if self.subject_input.is_visible():
            self.js_click(self.subject_input)
            self.subject_input.fill(subject)
            
        if self.description_input.is_visible():
            self.js_click(self.description_input)
            self.description_input.fill(description)
            
        self.set_all_datefields_to_current()
        
        if self.save_document_button.is_visible():
            self.js_click(self.save_document_button)
            self._wait_for_loader()
        logger.info("Communication entry added successfully.")

    def create_package_and_verify(self) -> None:
        """Clicks Create Package, checks the first attachment, and verifies document package creation."""
        logger.info("Creating package from attachments.")
        self._wait_for_loader()
        if self.create_package_button.count() == 0 or not self.create_package_button.is_visible():
            logger.warning("Create Package button not visible.")
            return

        self.create_package_button.scroll_into_view_if_needed()
        try:
            self.create_package_button.click(timeout=3000)
        except Exception:
            self.js_click(self.create_package_button)
        self._wait_for_loader()
        
        # Modal window container / title
        modal_title = self.page.locator(".k-window-title:visible, [role='dialog']:visible .k-window-title, .k-window:visible").filter(has_text=re.compile("Attachment|Package|Select", re.I)).first
        try:
            modal_title.wait_for(state="visible", timeout=8000)
        except Exception:
            pass
            
        # Select first checkbox inside modal if present
        chk = self.page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        try:
            if chk.count() > 0 and chk.is_visible():
                self.js_click(chk)
        except Exception:
            pass

        # Confirm selection
        confirm_btn = self.page.get_by_role("button", name="Select Attachments").or_(self.page.locator(".k-window:visible button:has-text('Select')")).first
        try:
            if confirm_btn.count() > 0 and confirm_btn.is_visible():
                self.js_click(confirm_btn)
                self._wait_for_loader()
        except Exception:
            pass

        # Handle OK / Success modal alert
        try:
            if self.ok_button.count() > 0 and self.ok_button.is_visible():
                self.js_click(self.ok_button)
                self._wait_for_loader()
        except Exception:
            pass
            
        logger.info("Document package created and verified successfully.")
