import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitTransferStatusLogPage(BasePage):
    """Page Object Model for the Permit Transfer Status Log tab in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Tab navigation
        self.status_log_tab_link = page.get_by_role("link", name="Status Log")
        self.documents_log_tab_link = page.get_by_role("link", name="Documents and Log")

        # Headings & Tab Content Assertions
        self.partial_form_first = page.locator("#partial-form").first
        self.status_log_heading = page.get_by_role("heading", name="Status Log")
        self.log_container_child = page.locator("div:nth-child(2) > div:nth-child(2)").first

    def navigate_to_status_log(self) -> None:
        """Navigates to the Status Log tab and verifies layout elements."""
        logger.info("Navigating to Status Log tab.")
        self.status_log_tab_link.wait_for(state="visible", timeout=10000)
        self.status_log_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.partial_form_first).to_be_visible(timeout=15000)
        expect(self.status_log_heading).to_be_visible(timeout=10000)
        expect(self.log_container_child).to_be_visible(timeout=10000)

    def navigate_to_documents_log(self) -> None:
        """Navigates to the Documents and Log tab."""
        logger.info("Navigating to Documents and Log tab.")
        self.documents_log_tab_link.wait_for(state="visible", timeout=10000)
        self.documents_log_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
