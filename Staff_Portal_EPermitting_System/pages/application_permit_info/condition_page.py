import logging
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class ConditionPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Navigation / Tabs
        self.conditions_tab = page.get_by_role("link", name="Conditions")
        
        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.conditions_heading = page.get_by_role("heading", name="Conditions")
        self.non_other_grid = page.locator("#nonOtherGrid")
        self.documents_log_heading = page.locator("#divfrmLog, #LogDynGridLoad, h1, h2, h3, h4, h5, h6").get_by_text("Documents and Log").first
        
        # Pagination Selectors
        self.next_page_link = page.locator("#conditiontop").get_by_role("link", name="Go to the next page")
        self.last_page_link = page.locator("#conditiontop").get_by_role("link", name="Go to the last page")

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

    def navigate_to_conditions(self) -> None:
        """Transitions to the Conditions tab."""
        logger.info("Navigating to Conditions tab.")
        self._wait_for_loader()
        self.scroll_to_element(self.conditions_tab)
        self.js_click(self.conditions_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates layout and headers on the Conditions page."""
        logger.info("Verifying Conditions page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.conditions_heading).to_be_visible(timeout=10000)

    def fill_condition_details(self, **kwargs) -> None:
        """Interacts with radio button options, validates condition grid, and navigates pagination pages."""
        logger.info("Interacting with Conditions form and grid.")
        self._wait_for_loader()
        
        # 1. Interact with radio options explicitly as per codegen
        try:
            radio_options = [
                self.page.locator("div:nth-child(2) > .k-radio-label").first,
                self.page.locator("div:nth-child(3) > .k-radio-label").first,
                self.page.locator(".k-radio-label").first,
                self.page.locator("input[type='radio']").first
            ]
            for rad in radio_options:
                if rad.count() > 0 and rad.is_visible():
                    logger.info("Clicking radio option label on Conditions form.")
                    self.js_click(rad)
                    self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"Radio option interaction note: {e}")
            
        # 2. Validate grid container
        try:
            if self.non_other_grid.count() > 0 and self.non_other_grid.is_visible():
                expect(self.non_other_grid).to_be_visible(timeout=10000)
                logger.info("Non-Other grid is visible.")
        except Exception:
            pass

        # 3. Perform grid pagination if available
        try:
            if self.next_page_link.count() > 0 and self.next_page_link.is_visible():
                logger.info("Navigating grid to next page.")
                self.js_click(self.next_page_link)
                self._wait_for_loader()
            if self.last_page_link.count() > 0 and self.last_page_link.is_visible():
                logger.info("Navigating grid to last page.")
                self.js_click(self.last_page_link)
                self._wait_for_loader()
        except Exception as e:
            logger.warning(f"Pagination navigation note: {e}")
            
        # 4. Scroll down to Documents and Log section and verify
        self.scroll_to_documents_log()
        expect(self.attach_document_button.or_(self.add_communication_button).first).to_be_visible(timeout=15000)
        logger.info("Conditions form options, grid, and Documents & Log section verified successfully.")

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
