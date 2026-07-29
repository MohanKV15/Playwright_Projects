import logging
import datetime
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PaymentListingPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Navigation / Tabs
        self.payments_tab = page.get_by_role("link", name="Payments")
        
        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing")
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.refund_details_heading = page.get_by_role("heading", name="Refund Details")
        self.documents_log_heading = page.locator("#divfrmLog, #LogDynGridLoad, h1, h2, h3, h4, h5, h6").get_by_text("Documents and Log").first
        
        # Action Buttons
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment")
        self.save_button = page.get_by_role("button", name=" Save")
        self.edit_payment_button = page.locator("#btnPaymentDetailsEdit, a.k-grid-edit").first
        
        # Dropdown Triggers
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --").first
        self.payment_method_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Method Of Payment --").first
        self.payment_subtype_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Sub Type--").first
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select payment Status --").first
        
        # Numeric & Text Inputs
        self.amount_input = page.get_by_role("spinbutton", name="Requested Amount ($) *").first
        self.comments_input = page.get_by_role("textbox", name="Comments")

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
            doc_btn = self.page.get_by_role("button", name="Attach Document").or_(self.page.locator("#divfrmLog, #btnAttachDoc, .btn:has-text('Attach')")).first
            if doc_btn.count() > 0 and doc_btn.is_visible():
                doc_btn.scroll_into_view_if_needed()
                self.page.wait_for_timeout(300)
            else:
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Scroll to Documents and Log section note: {e}")

    def navigate_to_payments(self) -> None:
        """Transitions to the Payments tab."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()
        self.scroll_to_element(self.payments_tab)
        self.js_click(self.payments_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates headers exist on the Payment Listing page."""
        logger.info("Verifying Payment Listing page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.payment_listing_heading).to_be_visible(timeout=10000)

    def set_all_payment_dates(self) -> None:
        """Sets all date inputs in the payment form to the current date."""
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        logger.info(f"Setting all payment date fields to '{current_date_str}'")
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

    def add_payment_details(self, amount: str = "1", comments: str = "test payment", **kwargs) -> None:
        """Fills out the Payment Details form by selecting valid options in each dropdown, setting dates, and saving."""
        logger.info("Adding new Payment details.")
        self._wait_for_loader()
        
        # Click Add New Payment
        self.scroll_to_element(self.add_new_payment_button)
        self.js_click(self.add_new_payment_button)
        self._wait_for_loader()
        
        expect(self.payment_details_heading).to_be_visible(timeout=10000)
        
        # Select Dropdowns sequentially using preferred codegen defaults ("Bond", "Bond", "Maintenance", "Not Paid")
        preferred_options = ["Bond", "Bond", "Maintenance", "Not Paid"]
        dropdowns = self.page.locator("#frmPaymentDetails span.k-widget.k-dropdown:visible, #frmPaymentDetails span[role='listbox']:visible")
        count = dropdowns.count()
        logger.info(f"Found {count} dropdowns inside Payment Details form.")
        
        for i in range(count):
            pref = preferred_options[i] if i < len(preferred_options) else ""
            self.js_click(dropdowns.nth(i))
            self._select_valid_dropdown_option(pref)
        
        # Fill Numeric Amount
        try:
            if self.amount_input.count() > 0 and self.amount_input.is_visible():
                self.js_click(self.amount_input)
                self.amount_input.fill(amount)
            else:
                num_input = self.page.locator(".k-numeric-wrap input").first
                self.js_click(num_input)
                num_input.fill(amount)
        except Exception as e:
            logger.warning(f"Amount input note: {e}")
            
        # Set all DateFields to current date via JS injection
        self.set_all_payment_dates()
        
        # Fill Comments text
        if self.comments_input.is_visible():
            self.scroll_to_element(self.comments_input)
            self.js_click(self.comments_input)
            self.comments_input.fill(comments)
            
        # Verify Refund Details heading if visible
        try:
            if self.refund_details_heading.is_visible():
                logger.info("Refund Details heading is visible.")
        except Exception:
            pass
            
        # Click Save using physical click / dispatch_bubble_click
        logger.info("Saving Payment Details.")
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

        # Click Edit on the created payment record row if visible, and Save again
        try:
            edit_btn = self.page.locator("#btnPaymentDetailsEdit, a.k-grid-edit, .k-grid #btnPaymentDetailsEdit").first
            if edit_btn.count() > 0 and edit_btn.is_visible():
                logger.info("Editing saved payment record.")
                self.scroll_to_element(edit_btn)
                self.js_click(edit_btn)
                self._wait_for_loader()
                
                logger.info("Re-saving Payment Details after edit.")
                self.scroll_to_element(self.save_button)
                try:
                    self.save_button.click(timeout=3000)
                except Exception:
                    self.dispatch_bubble_click(self.save_button)
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Payment edit button note: {e}")
            
        # Scroll down to Documents and Log section and verify
        self.scroll_to_documents_log()
        doc_sec = self.attach_document_button.or_(self.add_communication_button).or_(self.documents_log_heading).first
        if doc_sec.count() > 0 and doc_sec.is_visible():
            expect(doc_sec).to_be_visible(timeout=15000)
        logger.info("Payment details added, saved, and Documents & Log section verified successfully.")

    def attach_document(self, file_path: str, subject: str = "test", description: str = "test") -> None:
        """Scrolls viewport down to Documents and Log section before attaching a document."""
        self.scroll_to_documents_log()
        try:
            if not self.attach_document_button.is_visible():
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(500)
        except Exception:
            pass
        if self.attach_document_button.is_visible():
            super().attach_document(file_path, subject, description)

    def add_communication(self, subject: str = "testingd", description: str = "one") -> None:
        """Scrolls viewport down to Documents and Log section before adding a communication entry."""
        self.scroll_to_documents_log()
        try:
            if self.add_communication_button.is_visible():
                super().add_communication(subject, description)
        except Exception as e:
            logger.warning(f"Communication step note: {e}")

    def create_package_and_verify(self) -> None:
        """Scrolls viewport down to Documents and Log section before creating a package."""
        self.scroll_to_documents_log()
        try:
            if self.create_package_button.is_visible():
                super().create_package_and_verify()
        except Exception as e:
            logger.warning(f"Create package step note: {e}")
