import re
import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DealerDocumentsAndLogPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.documents_log_menu_link = page.locator("#navigationMenu2 a[href*='DealerPermitLog']")
        
        # Heading/Tab Validation
        self.dealer_details_heading = page.get_by_role("heading", name="Dealer Details")
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
        
        # Send Email button
        self.send_email_button = page.get_by_role("button", name="Send Email")
        self.cancel_button = page.get_by_role("button", name=" Cancel")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("dealer")

    def navigate_to_documents_log(self) -> None:
        """Navigates to the Dealers -> Documents and Log page."""
        logger.info("Navigating to Dealer Documents and Log page")
        self._expand_navigation_menu()
        
        logger.info("Clicking Documents and Log submenu link")
        self.documents_log_menu_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def verify_page_headings(self) -> None:
        """Verifies that the Dealer Details heading, Documents and Log heading, and form container are visible."""
        logger.info("Verifying page headings and container")
        expect(self.dealer_details_heading).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_container).to_be_visible(timeout=10000)

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
        self.attach_doc_button.click()
        
        # Wait for the Attach page to load
        self.page.wait_for_url(re.compile(r"4321LogAttachStaffFull", re.I), wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1000)
        
        logger.info("Locating file input element")
        file_input = self.page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(1000)
        
        self.select_current_date(0)
        
        if not title:
            title = self.fake.word() + " Test Document"
        logger.info(f"Filling doctitle: {title}")
        self.doc_title_input.click()
        self.doc_title_input.fill(title)
        
        if not desc:
            desc = self.fake.sentence()
        logger.info(f"Filling docdesc: {desc}")
        self.doc_desc_input.click()
        self.doc_desc_input.fill(desc)
        
        logger.info("Saving document upload")
        self.save_button.first.click()
        
        # Wait for redirect back to the Documents and Log listing page
        logger.info("Waiting for redirect back to Documents and Log page")
        self.page.wait_for_url(re.compile(r"4319DealerPermitLog", re.I), wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        logger.info("Document attached and saved successfully")

    def add_communication(self, subject: str = None, description: str = None) -> None:
        """Clicks Add Communication, fills details, and saves."""
        logger.info("Adding communication log entry")
        self.add_communication_button.click()
        self.page.wait_for_timeout(1000)
        
        self.select_current_date(0)
        
        now = datetime.datetime.now()
        date_str = now.strftime("%m/%d/%Y")
        logger.info(f"Filling communication date: {date_str}")
        try:
            self.comm_date_input.fill(date_str)
        except Exception as e:
            logger.warning(f"Could not fill Communication Date: {e}")
            
        if not subject:
            subject = self.fake.sentence(nb_words=3)
        logger.info(f"Filling subject: {subject}")
        self.subject_input.click()
        self.subject_input.fill(subject)
        
        if not description:
            description = self.fake.paragraph(nb_sentences=2)
        logger.info(f"Filling description: {description}")
        self.desc_input.click()
        self.desc_input.fill(description)
        
        logger.info("Saving communication details")
        self.save_button.first.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        logger.info("Communication entry saved successfully")

    def click_send_email_and_verify_navigation(self) -> None:
        """Clicks Send Email, verifies navigation to the email page, and clicks Cancel to return."""
        logger.info("Clicking 'Send Email' button")
        self.send_email_button.click()
        
        # Wait for the email form page to load (contains ATSP4321LogSendEmailFull)
        logger.info("Waiting for the Send Email page to load")
        try:
            self.page.wait_for_url(re.compile(r"ATSP4321LogSendEmailFull", re.I), wait_until="domcontentloaded", timeout=15000)
        except Exception:
            logger.warning("Auto-navigation to Send Email page timed out, attempting to click again")
            self.send_email_button.click()
            self.page.wait_for_url(re.compile(r"ATSP4321LogSendEmailFull", re.I), wait_until="domcontentloaded", timeout=15000)
            
        self.page.wait_for_timeout(2000)
        
        # Click Cancel
        logger.info("Clicking Cancel to return")
        self.cancel_button.click()
        self.page.wait_for_url(re.compile(r"4319DealerPermitLog", re.I), wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        logger.info("Returned from Send Email page successfully")
