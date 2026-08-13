import re
import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LicenseDocumentsAndLogPage(BasePage):
    """Page Object for License Documents and Log tab actions and validations."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Tab Selector
        self.documents_log_tab = page.get_by_role("link", name="Documents and Log")

        # Headings & Tab Content Assertions
        self.license_details_heading = page.get_by_role("heading", name="License Details")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.partial_form_first = page.locator("#partial-form").first
        self.grid_container = page.locator("div:nth-child(2) > .col-md-12")

        # Attach Document Fields
        self.attach_doc_button = page.get_by_role("button", name="Attach Document")
        self.doc_title_input = page.locator("#doctitle")
        self.doc_desc_input = page.locator("#docdesc")
        self.save_button = page.get_by_role("button", name=" Save")

        # Add Communication Fields
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")

        # Create Package Modal Fields
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_heading = page.get_by_text("Select Attachments for Permit")
        self.attachment_table_header = page.locator("div").filter(has_text="Date & TimeNameSelectparent_").nth(4)
        self.kendo_overlay = page.locator(".k-overlay")
        self.ok_button = page.get_by_role("button", name="OK")

    def navigate_to_documents_log(self) -> None:
        """Clicks the Documents and Log tab."""
        logger.info("Navigating to the Documents and Log tab.")
        self.documents_log_tab.wait_for(state="visible", timeout=15000)
        self.documents_log_tab.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def select_current_date(self, picker_index: int = 0) -> None:
        """Opens the date picker at the given index and selects today's date."""
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
        self.attach_doc_button.wait_for(state="visible", timeout=10000)
        self.attach_doc_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)

        # Select date
        self.select_current_date(0)

        # File upload
        file_input = self.page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(500)

        # Metadata
        if not title:
            title = self.fake.word() + " Test Document"
        logger.info(f"Entering doctitle: {title}")
        self.doc_title_input.click()
        self.doc_title_input.fill(title)

        if not desc:
            desc = self.fake.sentence()
        logger.info(f"Entering docdesc: {desc}")
        self.doc_desc_input.click()
        self.doc_desc_input.fill(desc)

        # Save
        logger.info("Saving document upload")
        self.save_button.click()
        self.page.wait_for_url("**/4319LicensePermitLog**", timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def add_communication(self, subject: str = None, description: str = None) -> None:
        """Clicks Add Communication, fills details, and saves."""
        logger.info("Adding communication entry")
        self.add_communication_button.wait_for(state="visible", timeout=10000)
        self.add_communication_button.click()
        self.page.wait_for_timeout(1000)

        # Select date
        self.select_current_date(0)

        # Fill subject & description
        if not subject:
            subject = self.fake.sentence(nb_words=3)
        logger.info(f"Filling subject: {subject}")
        self.subject_input.click()
        self.subject_input.fill(subject)

        if not description:
            description = self.fake.paragraph(nb_sentences=2)
        logger.info(f"Filling description: {description}")
        self.description_input.click()
        self.description_input.fill(description)

        # Save
        logger.info("Saving communication details")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def verify_headings(self) -> None:
        """Verifies visibility of headings and layout containers."""
        logger.info("Verifying headings and layout containers")
        expect(self.license_details_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        expect(self.grid_container).to_be_visible(timeout=10000)

    def create_package(self) -> None:
        """Automates package creation by checking dynamic checkboxes and handling the overlay/dialog."""
        logger.info("Initiating package creation")
        self.create_package_button.wait_for(state="visible", timeout=10000)
        self.create_package_button.click()
        
        # Wait for Dialog to load
        expect(self.select_attachments_heading).to_be_visible(timeout=10000)
        expect(self.attachment_table_header).to_be_visible(timeout=10000)

        # Check the first checkbox inside the attachment dialog
        dialog_checkbox = self.page.locator(".k-dialog input[type='checkbox'], .k-window input[type='checkbox'], input[type='checkbox']").first
        dialog_checkbox.wait_for(state="visible", timeout=5000)
        dialog_checkbox.check()

        # Click the 'Select Attachments' button to submit
        logger.info("Clicking the 'Select Attachments' button")
        self.page.get_by_role("button", name="Select Attachments").click()

        # Handle operation completion alerts
        expect(self.page.get_by_text("Document Package has been").first).to_be_visible(timeout=15000)

        # Click OK
        logger.info("Confirming Alert Dialog by clicking OK")
        self.ok_button.wait_for(state="visible", timeout=10000)
        self.ok_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        # Verify grid container is stable
        expect(self.grid_container).to_be_visible(timeout=10000)
        logger.info("Package creation completed and verified successfully.")
