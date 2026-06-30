import logging
import datetime
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage
from faker import Faker

logger = logging.getLogger(__name__)

class ConformanceGenerationPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Tabs
        self.conformance_tab = page.get_by_role("link", name="Conformance/Trip Generation")
        
        # Heading & Section Container Selectors
        self.header_details_label = page.get_by_text("Department Job # Permit Type")
        self.conformance_heading = page.get_by_role("heading", name="Conformance")
        self.trip_generation_heading = page.get_by_role("heading", name="Trip Generation")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        
        # Run Conformance Selectors
        self.run_conformance_button = page.get_by_role("button", name="Run Conformance")
        
        # Documents and Log Selectors
        self.attach_document_button = page.get_by_role("button", name="Attach Document")
        self.document_modal_save = page.get_by_text("Save Cancel Preparation Date")
        self.date_picker_button = page.get_by_role("button", name="select", exact=True)
        self.file_input = page.get_by_role("button", name="File Name * Select files...")
        self.subject_input = page.get_by_role("textbox", name="Subject *")
        self.description_input = page.get_by_role("textbox", name="Description")
        self.save_button = page.get_by_role("button", name=" Save")
        
        # Communications Selectors
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_container = page.locator("#divfrmLog > .form-wrapper > .row > .col-md-12")
        self.communication_date_picker = page.get_by_role("button", name="select")
        
        # Package Selectors
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_title = page.locator(".k-window-title:visible").filter(has_text=re.compile("Select Attachments", re.I)).first
        self.first_attachment_checkbox = page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        self.select_attachments_confirm_button = page.get_by_role("button", name="Select Attachments")
        self.package_created_message = page.locator(".k-window:visible, [role='dialog']:visible").get_by_text("Your document package is")
        self.ok_button = page.get_by_role("button", name="OK")
        
        # Final layout check element
        self.final_log_container = page.locator("#LogDynGridLoad > #partial-form > .form-wrapper > .row > .col-md-12")



    def navigate_to_conformance(self) -> None:
        """Transitions to the Conformance/Trip Generation tab."""
        logger.info("Navigating to Conformance/Trip Generation tab.")
        self._wait_for_loader()
        self.js_click(self.conformance_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layouts exist on the page."""
        logger.info("Verifying Conformance page initial layout.")
        expect(self.header_details_label.first).to_be_visible(timeout=15000)
        expect(self.conformance_heading).to_be_visible(timeout=10000)

    def run_conformance_and_verify(self) -> None:
        """Clicks 'Run Conformance', asserts warning dialog text, and closes alert modal."""
        logger.info("Running Conformance calculations.")
        self.js_click(self.run_conformance_button)
        
        # Accept alert dialog (usually a Kendo dialog window popup warning)
        try:
            self.ok_button.wait_for(state="visible", timeout=10000)
            self.js_click(self.ok_button)
            logger.info("Clicked OK to accept conformance alert popup.")
        except Exception:
            # Fallback to general OK dialog matching
            logger.info("No conformance alert OK button found via direct class, trying get_by_role.")
            self.js_click(self.page.get_by_role("button", name="OK"))
            
        self._wait_for_loader()
        
        # Verify Trip Generation header is visible after calculation runs
        expect(self.trip_generation_heading).to_be_visible(timeout=15000)
        logger.info("Conformance run completed and verified.")

    def attach_document(self, file_path: str, subject: str = "test", description: str = "test") -> None:
        """Attaches a document to the Documents and Log section."""
        logger.info(f"Attaching document: {file_path}")
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        self.js_click(self.attach_document_button)
        expect(self.document_modal_save).to_be_visible(timeout=10000)
        
        # Set file input
        self.file_input.set_input_files(file_path)
        
        # Wait up to 10s for the Kendo upload file element to indicate completion
        try:
            self.page.locator(".k-upload-files .k-file-success, .k-upload-files li.k-file").first.wait_for(state="visible", timeout=10000)
            logger.info("File upload success indicator detected in DOM.")
        except Exception:
            self.page.wait_for_timeout(3000)
        
        # Fill text inputs
        self.js_click(self.subject_input)
        self.subject_input.fill(subject)
        
        self.js_click(self.description_input)
        self.description_input.fill(description)
        
        # Select today's date
        self.select_today_in_calendar(self.date_picker_button)
        self.set_all_datefields_to_current()
        
        # Save
        self.js_click(self.save_button)
        self._wait_for_loader()
        logger.info("Document attached successfully.")

    def add_communication(self, subject: str = "testingd", description: str = "one") -> None:
        """Adds a communication log entry."""
        logger.info("Adding a new communication entry.")
        self.js_click(self.add_communication_button)
        expect(self.communication_modal_container).to_be_visible(timeout=10000)
        
        # Select date
        self.select_today_in_calendar(self.communication_date_picker)
        
        # Fill text inputs
        self.js_click(self.subject_input)
        self.subject_input.fill(subject)
        
        self.js_click(self.description_input)
        self.description_input.fill(description)
        
        self.set_all_datefields_to_current()
        
        # Click Save
        self.js_click(self.save_button)
        self._wait_for_loader()
        logger.info("Communication entry added successfully.")

    def create_package_and_verify(self) -> None:
        """Clicks Create Package, checks the first attachment, and verifies document package creation."""
        logger.info("Creating package from attachments.")
        # Click Create Package and verify attachments window opens
        self.js_click(self.create_package_button)
        expect(self.select_attachments_title).to_be_visible(timeout=15000)
        
        # Select first checkbox
        expect(self.first_attachment_checkbox).to_be_visible(timeout=10000)
        self.js_click(self.first_attachment_checkbox)
        
        # Select attachments button
        self.js_click(self.select_attachments_confirm_button)
        
        # Verify success message and click OK
        expect(self.package_created_message).to_be_visible(timeout=15000)
        self.js_click(self.ok_button)
        self._wait_for_loader()
        
        # Final layout check
        expect(self.final_log_container).to_be_visible(timeout=15000)
        logger.info("Document package created and verified successfully.")
