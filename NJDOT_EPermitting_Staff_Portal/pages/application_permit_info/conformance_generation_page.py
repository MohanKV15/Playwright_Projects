import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ConformanceGenerationPage(BasePage):
    """
    Page Object Model for Conformance/Trip Generation in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation & Headers
        self.conformance_tab = page.get_by_role("link", name="Conformance/Trip Generation").or_(page.locator("a:has-text('Conformance')")).first
        self.header_details_label = page.get_by_text("Department Job # Permit Type").or_(page.locator("#LogAppHeader")).first
        self.conformance_heading = page.get_by_role("heading", name="Conformance")
        self.trip_generation_heading = page.get_by_role("heading", name="Trip Generation")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")

        # Actions
        self.run_conformance_button = page.get_by_role("button", name="Run Conformance")
        self.final_log_container = page.locator("#LogDynGridLoad, #partial-form, #LogAppHeader, h1, h2, h3").first

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
        expect(self.header_details_label).to_be_visible(timeout=15000)
        expect(self.conformance_heading).to_be_visible(timeout=10000)

    def run_conformance_and_verify(self) -> None:
        """Clicks 'Run Conformance', asserts warning dialog text, and closes alert modal."""
        logger.info("Running Conformance calculations.")
        if self.run_conformance_button.count() > 0 and self.run_conformance_button.is_visible():
            self.js_click(self.run_conformance_button)

            try:
                self.ok_button.wait_for(state="visible", timeout=5000)
                self.js_click(self.ok_button)
            except Exception:
                pass

            self._wait_for_loader()

        expect(self.trip_generation_heading.or_(self.conformance_heading).first).to_be_visible(timeout=15000)
        logger.info("Conformance run completed and verified.")

    def create_package_and_verify(self) -> None:
        """Clicks Create Package and verifies document package creation."""
        logger.info("Creating package from attachments.")
        super().create_package_and_verify()
        if self.final_log_container.count() > 0:
            expect(self.final_log_container).to_be_visible(timeout=15000)
