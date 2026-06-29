import logging
import re
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationDocumentsAndLogPage(BasePage):
    """Page Object Model for the Violations Documents and Log section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Navigation elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")

        # Search elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.dealer_name_search_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.customer_results_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.edit_violation_button = page.locator("#btnViolationsEdit")

        # Documents and Log Tab link
        self.documents_log_tab_link = page.get_by_role("link", name="Documents and Log")

        # Layout validations inside tab
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.partial_form_second = page.locator("#partial-form").nth(2)
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.grid_container = page.locator(".k-grid").first

        # Attach Document elements
        self.attach_document_btn = page.get_by_role("button", name="Attach Document")
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        self.select_files_trigger = page.locator("div").filter(has_text=re.compile(r"^Select files\.\.\.$")).first
        self.doc_title_input = page.locator("#doctitle")
        self.doc_desc_input = page.locator("#docdesc")
        self.save_button = page.get_by_role("button", name=" Save")
        self.ok_button = page.get_by_role("button", name="OK")

        # Add Communication elements
        self.add_communication_btn = page.get_by_role("button", name="Add Communication")
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")

        # Send Email and log elements
        self.send_email_btn = page.get_by_role("button", name="Send Email")
        self.email_overlay = page.locator("div").filter(has_text="To: CC: BCC: Subject Message").nth(4)
        self.cancel_button = page.get_by_role("button", name=" Cancel")

        # View log overlay elements
        self.view_communication_btn = page.get_by_role("button").nth(5)
        self.communication_log_overlay = page.locator("div").filter(has_text="Communication").nth(4)

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Violations."""
        logger.info("Expanding Violations PanelBar navigation.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations Listing and validates elements."""
        self._expand_navigation_menu()
        if not self.violations_listing_link.is_visible():
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Searches violations grid by dealer name."""
        logger.info(f"Searching for dealer '{dealer_name}' in listing grid.")
        self.dealer_name_search_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_search_input.click()
        self.dealer_name_search_input.fill(dealer_name)
        self.search_button.click()
        self._wait_for_loader()
        expect(self.customer_results_container).to_be_visible(timeout=15000)

    def click_edit_on_first_record(self, record_name: str = None) -> None:
        """Clicks edit button on the first matching record in search results."""
        logger.info("Opening the first violation record details.")
        edit_btn = self.page.locator("#btnViolationsEdit").first
        expect(edit_btn).to_be_visible(timeout=10000)
        edit_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def navigate_to_documents_log(self) -> None:
        """Clicks the Documents and Log tab."""
        logger.info("Navigating to the Documents and Log tab.")
        self.documents_log_tab_link.wait_for(state="visible", timeout=15000)
        self.documents_log_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Validate headers and layouts
        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.partial_form_second).to_be_visible(timeout=10000)
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        expect(self.grid_container).to_be_visible(timeout=10000)

    def select_current_date(self, picker_index: int = 0) -> None:
        """Opens the date picker at the given index and selects the current day (today's date)."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        self.date_picker_buttons.nth(picker_index).click()
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link
        try:
            self.focused_date_link.first.click(timeout=3000)
            logger.info("Selected focused date link successfully")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 2nd attempt: try selecting today using Kendo classes
        try:
            self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first.click(timeout=2000)
            logger.info("Selected today's date using k-today/k-state-today/k-state-selected selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: look for the day number link inside the visible calendar grid
        try:
            today_day = str(datetime.datetime.now().day)
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def attach_document(self, file_path: str, title: str = None, desc: str = None) -> None:
        """Clicks Attach Document, selects date, uploads file, fills metadata, and saves."""
        logger.info("Opening Attach Document dialog.")
        self.attach_document_btn.click()
        self.page.wait_for_timeout(1000)

        # 1. Select date
        self.select_current_date(0)

        # 2. File upload directly on input[type='file']
        logger.info(f"Uploading file: {file_path}")
        file_input = self.page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(500)

        # 3. Enter document title
        if not title:
            title = self.fake.word() + " Test Title"
        logger.info(f"Filling title: {title}")
        self.doc_title_input.click()
        self.doc_title_input.fill(title)

        # 4. Enter document description
        if not desc:
            desc = self.fake.sentence()
        logger.info(f"Filling description: {desc}")
        self.doc_desc_input.click()
        self.doc_desc_input.fill(desc)

        # 5. Click Save
        logger.info("Saving document attachment.")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # 6. Return to Documents and Log tab
        logger.info("Returning to Documents and Log tab.")
        self.documents_log_tab_link.wait_for(state="visible", timeout=15000)
        self.documents_log_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def add_communication(self, subject: str = None, description: str = None) -> None:
        """Clicks Add Communication, selects date, fills fields, and saves."""
        logger.info("Adding communication entry.")
        self.add_communication_btn.click()
        self.page.wait_for_timeout(1000)

        # 1. Select date
        self.select_current_date(0)

        # 2. Fill Subject
        if not subject:
            subject = self.fake.sentence(nb_words=3)
        logger.info(f"Filling communication subject: {subject}")
        self.subject_input.click()
        self.subject_input.fill(subject)

        # 3. Fill Description
        if not description:
            description = self.fake.paragraph(nb_sentences=2)
        logger.info(f"Filling communication description: {description}")
        self.description_input.click()
        self.description_input.fill(description)

        # 4. Save
        logger.info("Saving communication record.")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def verify_record_in_grid(self, text_value: str) -> None:
        """Verifies that the given text value is visible in the grid container table."""
        logger.info(f"Verifying that record '{text_value}' is visible in the Documents & Log grid.")
        expect(self.grid_container.get_by_text(text_value).first).to_be_visible(timeout=15000)
        logger.info(f"Successfully verified record '{text_value}' visibility.")

    def click_send_email_and_cancel(self) -> None:
        """Clicks Send Email button, verifies fields overlay, and clicks Cancel."""
        logger.info("Opening Send Email overlay.")
        self.send_email_btn.click()
        self.page.wait_for_timeout(1000)

        # Verify overlay is visible
        expect(self.email_overlay).to_be_visible(timeout=10000)
        
        # Click Cancel
        logger.info("Canceling Send Email overlay.")
        self.cancel_button.click()
        self.page.wait_for_timeout(500)

    def click_view_communication_details_and_cancel(self) -> None:
        """Clicks view communication details button, verifies popup contents, and clicks Cancel."""
        logger.info("Opening View Communication Log overlay.")
        self.view_communication_btn.click()
        self.page.wait_for_timeout(1000)

        # Verify overlay is visible
        expect(self.communication_log_overlay).to_be_visible(timeout=10000)

        # Click Cancel
        logger.info("Canceling View Communication Log overlay.")
        self.cancel_button.click()
        self.page.wait_for_timeout(500)
        expect(self.grid_container).to_be_visible(timeout=10000)

        
