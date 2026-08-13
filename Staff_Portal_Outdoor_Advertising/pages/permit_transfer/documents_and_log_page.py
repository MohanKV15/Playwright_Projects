import re
import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitTransferDocumentsAndLogPage(BasePage):
    """Page Object Model for the Permit Transfer Documents and Log tab."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Tab Selector
        self.documents_log_tab = page.get_by_role("link", name="Documents and Log")

        # Attach Document Pop-up & Fields
        self.attach_doc_button = page.get_by_role("button", name="Attach Document")
        self.doc_title_input = page.locator("#doctitle")
        self.doc_desc_input = page.locator("#docdesc")

        # Add Communication Pop-up & Fields
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_header = page.locator("div").filter(has_text="Communication").nth(4)
        
        # Date Picker elements
        self.select_button = page.get_by_role("button", name="select")
        self.day_link = lambda d: page.get_by_role("link", name=str(d), exact=True)

        # Communication Fields
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")
        self.save_button = page.get_by_role("button", name=" Save")

        # Create Package Pop-up & Fields
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_heading = page.get_by_text("Select Attachments for Permit")
        self.attachment_grid_header = page.locator("div").filter(has_text="Date & TimeNameSelectparent_").nth(4)
        self.close_button = page.get_by_role("button", name="Close")

        # Send Email Overlay Elements
        self.send_email_button = page.get_by_role("button", name="Send Email")
        self.cancel_button = page.get_by_role("button", name=" Cancel")

    def navigate_to_documents_log(self) -> None:
        """Clicks the Documents and Log tab."""
        logger.info("Navigating to the Documents and Log tab.")
        self.documents_log_tab.wait_for(state="visible", timeout=15000)
        self.documents_log_tab.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

    def add_communication(self, subject: str = "test", description: str = "test", date_day: str = "26") -> None:
        """Clicks Add Communication, opens modal, selects date, fills subject/description, and saves."""
        logger.info("Clicking Add Communication button.")
        self.add_communication_button.click()
        self.page.wait_for_timeout(1000)

        # Assert communication header
        expect(self.communication_modal_header).to_be_visible(timeout=10000)

        # Open datepicker and select target day
        logger.info(f"Selecting date day: {date_day}")
        self.select_button.click()
        self.page.wait_for_timeout(500)
        self.day_link(date_day).click()
        self.page.wait_for_timeout(500)

        # Fill textboxes
        logger.info(f"Filling Subject: {subject}")
        self.subject_input.click()
        self.subject_input.fill(subject)

        logger.info(f"Filling Description: {description}")
        self.description_input.click()
        self.description_input.fill(description)

        # Click Save
        logger.info("Clicking Save button.")
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

    def verify_and_close_package_modal(self) -> None:
        """Clicks Create Package, verifies selectors, and clicks Close."""
        logger.info("Clicking Create Package button.")
        self.create_package_button.click()
        self.page.wait_for_timeout(1000)

        # Assertions
        expect(self.select_attachments_heading).to_be_visible(timeout=10000)
        expect(self.attachment_grid_header).to_be_visible(timeout=10000)

        # Close Modal
        logger.info("Clicking Close button.")
        self.close_button.click()
        self.page.wait_for_timeout(1000)

    def verify_send_email_and_cancel(self) -> None:
        """Clicks Send Email, checks cancel button, and cancels."""
        logger.info("Clicking Send Email button.")
        self.send_email_button.click()
        self.page.wait_for_timeout(1000)

        # Assert cancel is visible and click
        expect(self.cancel_button).to_be_visible(timeout=10000)
        logger.info("Clicking Cancel button.")
        self.cancel_button.click()
        self.page.wait_for_timeout(1000)

    def attach_document(self, file_path: str | None = None, title: str = None, desc: str = None, date_day: str = "26") -> None:
        """Clicks Attach Document, uploads a file, selects date, enters title/description, and saves."""
        import os
        from utils.config import Config
        if not file_path or not os.path.exists(file_path):
            file_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")

        logger.info(f"Attaching document: {file_path}")
        self.attach_doc_button.click()
        self.page.wait_for_timeout(1000)

        # Set input files
        logger.info("Locating file input element")
        file_input = self.page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(1000)

        # Select date day
        logger.info(f"Selecting date day: {date_day}")
        self.select_button.click()
        self.page.wait_for_timeout(500)
        self.day_link(date_day).click()
        self.page.wait_for_timeout(500)

        # Fill details
        if not title:
            title = f"Doc {self.fake.word()}"
        logger.info(f"Filling title: {title}")
        self.doc_title_input.click()
        self.doc_title_input.fill(title)

        if not desc:
            desc = self.fake.sentence()
        logger.info(f"Filling description: {desc}")
        self.doc_desc_input.click()
        self.doc_desc_input.fill(desc)

        # Click Save
        logger.info("Clicking Save button")
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()
