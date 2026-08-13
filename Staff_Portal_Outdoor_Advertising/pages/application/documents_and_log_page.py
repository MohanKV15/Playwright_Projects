import re
import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DocumentsAndLogPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.documents_log_link = page.get_by_role("link", name="Documents and Log")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.partial_form_container = page.locator("#partial-form").nth(2)
        
        # Attach Document popup & fields
        self.attach_doc_button = page.get_by_role("button", name="Attach Document")
        self.doc_title_input = page.locator("#doctitle")
        self.doc_desc_input = page.locator("#docdesc")
        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I))
        
        # Add Communication popup & fields
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.comm_date_input = page.get_by_role("combobox", name="Communication Date")
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.desc_input = page.get_by_role("textbox", name="Description")
        
        # Create Package popup & fields
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_popup = page.locator("div").filter(has_text=re.compile(r"^Select Attachments for Permit Package$", re.I))
        self.select_attachments_dropdown = page.locator("div").filter(has_text="Select Attachments")
        self.kendo_overlay = page.locator(".k-overlay")
        
        # Kendo Confirmation/Alert Dialog
        self.confirm_dialog = page.locator("div").filter(has_text=re.compile(r"^u-njoda\.bemcorp\.net$")).first
        self.package_success_text = page.get_by_text("Document Package has been")
        self.ok_button = page.get_by_role("button", name="OK")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_documents_and_log_tab(self) -> None:
        """Navigates to the Documents and Log tab and verifies headings load."""
        logger.info("Navigating to the Documents and Log tab")
        self._expand_navigation_menu()
        self.documents_log_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings and container on the Documents and Log tab are visible."""
        logger.info("Verifying headings on the Documents and Log tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_container).to_be_visible(timeout=10000)

    def select_current_date(self, picker_index: int = 0) -> None:
        """Opens the date picker at the given index and selects the current day (focused/today's date)."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        picker_btn = self.page.get_by_role("button", name="select").nth(picker_index)
        picker_btn.wait_for(state="visible", timeout=5000)
        picker_btn.click()
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link
        try:
            self.page.get_by_label("Current focused date is").get_by_role("link").first.click(timeout=3000)
            logger.info("Selected focused date link successfully")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 2nd attempt: try selecting today using Kendo class '.k-today'
        try:
            self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first.click(timeout=2000)
            logger.info("Selected today's date using k-today/k-state-today/k-state-selected selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: click by grid cell title matching today's formatted date
        try:
            now = datetime.datetime.now()
            day_str = now.strftime("%d")
            day_unpadded = str(now.day)
            
            # Format: Weekday, Month Day,
            title_padded = now.strftime(f"%A, %B {day_str},")
            title_unpadded = now.strftime(f"%A, %B {day_unpadded},")
            
            for title in [title_padded, title_unpadded]:
                match = self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link").get_by_title(re.compile(rf"^{re.escape(title)}"), exact=False)
                if match.count() > 0:
                    match.first.click(timeout=2000)
                    logger.info(f"Selected date using title '{title}'")
                    self.page.wait_for_timeout(500)
                    return
                match_grid = self.page.get_by_role("grid").get_by_title(re.compile(rf"^{re.escape(title)}"), exact=False)
                if match_grid.count() > 0:
                    match_grid.first.click(timeout=2000)
                    logger.info(f"Selected date via grid matching title '{title}'")
                    self.page.wait_for_timeout(500)
                    return
        except Exception:
            pass

        # 4th attempt: look for the day number link inside the visible calendar grid
        try:
            today_day = str(datetime.datetime.now().day)
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def attach_document(self, file_path: str | None = None, title: str = None, desc: str = None) -> None:
        """Clicks Attach Document, uploads a file, enters details, and saves."""
        import os
        from utils.config import Config
        if not file_path or not os.path.exists(file_path):
            file_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")

        logger.info(f"Attaching document: {file_path}")
        self.attach_doc_button.click()
        self.page.wait_for_timeout(1000)
        
        # Find the hidden input type="file" and set the input files
        logger.info("Locating file input element")
        file_input = self.page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(1000)
        
        # Select the document date (first picker in the form)
        self.select_current_date(0)
        
        # Fill Title
        if not title:
            title = self.fake.word() + " Test Document"
        logger.info(f"Filling doctitle: {title}")
        self.doc_title_input.click()
        self.doc_title_input.fill(title)
        
        # Fill Description
        if not desc:
            desc = self.fake.sentence()
        logger.info(f"Filling docdesc: {desc}")
        self.doc_desc_input.click()
        self.doc_desc_input.fill(desc)
        
        # Click Save
        logger.info("Saving document upload")
        self.save_button.first.click()
        self.page.wait_for_timeout(2000)
        logger.info("Document attached and saved successfully")

    def add_communication(self, subject: str = None, description: str = None) -> None:
        """Clicks Add Communication, fills details, and saves."""
        logger.info("Adding communication log entry")
        self.add_communication_button.click()
        self.page.wait_for_timeout(1000)
        
        # Select the date (clicks date picker and selects today)
        self.select_current_date(0)
        
        # Fill Communication Date textbox/combobox as fallback/overwrite
        now = datetime.datetime.now()
        date_str = now.strftime("%m/%d/%Y")
        logger.info(f"Filling communication date: {date_str}")
        try:
            self.comm_date_input.fill(date_str)
        except Exception as e:
            logger.warning(f"Could not fill Communication Date combobox: {e}")
            
        # Fill Subject
        if not subject:
            subject = self.fake.sentence(nb_words=3)
        logger.info(f"Filling subject: {subject}")
        self.subject_input.click()
        self.subject_input.fill(subject)
        
        # Fill Description
        if not description:
            description = self.fake.paragraph(nb_sentences=2)
        logger.info(f"Filling description: {description}")
        self.desc_input.click()
        self.desc_input.fill(description)
        
        # Click Save
        logger.info("Saving communication details")
        self.save_button.first.click()
        self.page.wait_for_timeout(2000)
        logger.info("Communication entry saved successfully")

    def create_document_package(self) -> None:
        """Clicks Create Package, checks the first document's checkbox, verifies popup, and confirms."""
        logger.info("Creating Document Package")
        self.create_package_button.click()
        self.page.wait_for_timeout(1000)
        
        # Select first checkbox in the documents list (representing the 1st record)
        logger.info("Selecting the first available document checkbox")
        first_checkbox = self.page.locator("input[type='checkbox']").first
        first_checkbox.wait_for(state="visible", timeout=10000)
        first_checkbox.check()
        self.page.wait_for_timeout(500)
        
        # Verify attachments popup heading
        expect(self.select_attachments_popup).to_be_visible(timeout=10000)
        
        # Click the "Select Attachments" button at the bottom of the modal to submit
        logger.info("Clicking the Select Attachments submit button")
        submit_btn = self.page.get_by_role("button", name="Select Attachments")
        if submit_btn.count() == 0:
            submit_btn = self.page.locator("button:has-text('Select Attachments')").first
        submit_btn.click()
        self.page.wait_for_timeout(1000)
        
        # Verify success alert dialog and OK button click
        logger.info("Confirming success alert popups")
        expect(self.confirm_dialog).to_be_visible(timeout=15000)
        expect(self.package_success_text).to_be_visible(timeout=15000)
        self.ok_button.click()
        self.page.wait_for_timeout(2000)
        logger.info("Document Package created and validated successfully")
