import logging
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class AppealPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Navigation / Tabs
        self.appeal_tab = page.get_by_role("link", name="Appeal")
        
        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.appeal_heading = page.get_by_role("heading", name="Appeal")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        
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
            if self.documents_log_heading.is_visible():
                self.documents_log_heading.scroll_into_view_if_needed()
                self.page.evaluate("window.scrollBy(0, 150)")
                self.page.wait_for_timeout(500)
            elif self.attach_document_button.is_visible():
                self.attach_document_button.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Scroll to Documents and Log section note: {e}")

    def navigate_to_appeal(self) -> None:
        """Transitions to the Appeal tab."""
        logger.info("Navigating to Appeal tab.")
        self._wait_for_loader()
        self.scroll_to_element(self.appeal_tab)
        self.js_click(self.appeal_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layouts exist on the Appeal page."""
        logger.info("Verifying Appeal page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.appeal_heading).to_be_visible(timeout=10000)
        self.scroll_to_element(self.appeal_heading)

    def fill_appeal_details(self, comments: str = "test appeal comments") -> None:
        """Fills out the Appeal form fields, date pickers, radio options, comments, and saves with page scrolling."""
        logger.info("Filling out Appeal details with page scrolling.")
        self._wait_for_loader()
        
        # 1. Scroll & interact with form radio buttons / options explicitly
        try:
            radio_selectors = [
                self.page.locator("label:nth-child(5)").first,
                self.page.locator("label:nth-child(8)").first,
                self.page.locator(".k-radio-label").first,
                self.page.locator(".col-md-6 > .form-check > label:nth-child(5)").first,
                self.page.locator(".k-radio, input[type='radio']").first
            ]
            for radio_loc in radio_selectors:
                if radio_loc.count() > 0 and radio_loc.is_visible():
                    logger.info("Scrolling to and clicking radio button option on Appeal form.")
                    self.scroll_to_element(radio_loc)
                    self.js_click(radio_loc)
                    self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Radio button interaction note: {e}")
            
        # 2. Set all date fields to current date via helper
        self.set_all_datefields_to_current()
        
        # 3. Scroll to comments text input and fill
        if self.comments_input.is_visible():
            logger.info("Scrolling to Comments input.")
            self.scroll_to_element(self.comments_input)
            self.js_click(self.comments_input)
            self.comments_input.fill(comments)
        
        # 4. Scroll to Save button and click
        logger.info("Scrolling to Save button and saving Appeal form details.")
        self.save_button.wait_for(state="visible", timeout=10000)
        self.scroll_to_element(self.save_button)
        self.js_click(self.save_button)
        self._wait_for_loader()
        
        # 5. Scroll down to Documents and Log section and verify
        self.scroll_to_documents_log()
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
        logger.info("Appeal details saved and Documents & Log section verified successfully with scrolling.")

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
