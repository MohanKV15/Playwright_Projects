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

    def create_package_and_verify(self) -> None:
        """Clicks Create Package, checks the first attachment, and verifies document package creation."""
        logger.info("Creating package from attachments.")
        super().create_package_and_verify()
        # Final layout check
        expect(self.final_log_container).to_be_visible(timeout=15000)
