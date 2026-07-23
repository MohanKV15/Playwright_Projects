import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class CompletenessCheckPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation
        self.completeness_tab = page.get_by_role("link", name="Completeness Check")
        
        # Layout Verification
        self.partial_form_section = page.locator("#partial-form > section > div > div").first
        self.header_element = page.locator("#LogAppHeader")
        self.details_heading = page.get_by_role("heading", name="Completeness Details")
        self.details_save_text = page.get_by_text("Completeness Details Save")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        
        # Action Buttons
        self.save_completeness_button = page.get_by_role("button", name=" Save")
        self.gen_completeness_letter_button = page.get_by_role("button", name="Generate Completeness Letter")
        self.gen_1st_info_button = page.get_by_role("button", name="Generate 1st Information")
        self.gen_30day_followup_button = page.get_by_role("button", name="Generate 1st 30 Day Follow-up")

    def navigate_to_completeness_check(self) -> None:
        """Transitions to the Completeness Check tab."""
        logger.info("Navigating to Completeness Check tab.")
        self._wait_for_loader()
        self.js_click(self.completeness_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates that all key layout areas and headings are visible."""
        logger.info("Verifying Completeness Check initial layout.")
        expect(self.partial_form_section).to_be_visible(timeout=15000)
        expect(self.header_element).to_be_visible(timeout=15000)
        expect(self.details_heading).to_be_visible(timeout=15000)
        expect(self.details_save_text).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)

    def save_completeness_details(self) -> None:
        """Clicks the Save button and awaits the loader response."""
        logger.info("Saving Completeness Details.")
        self._wait_for_loader()
        self.js_click(self.save_completeness_button)
        self._wait_for_loader()
        logger.info("Saved Completeness Details successfully.")

    def generate_letters_and_verify_popups(self) -> None:
        """Generates all completeness and follow-up letters, verifying each popup displays the PDF mainCanvas."""
        self._wait_for_loader()
        
        logger.info("Generating Completeness Letter...")
        with self.page.expect_popup() as page1_info:
            self.js_click(self.gen_completeness_letter_button)
        page1 = page1_info.value
        expect(page1.locator("#mainCanvas")).to_be_visible(timeout=25000)
        page1.close()
        logger.info("Completeness Letter popup verified and closed.")
        
        logger.info("Generating 1st Information...")
        with self.page.expect_popup() as page2_info:
            self.js_click(self.gen_1st_info_button)
        page2 = page2_info.value
        expect(page2.locator("#mainCanvas")).to_be_visible(timeout=25000)
        page2.close()
        logger.info("1st Information popup verified and closed.")
        
        logger.info("Generating 1st 30 Day Follow-up...")
        with self.page.expect_popup() as page3_info:
            self.js_click(self.gen_30day_followup_button)
        page3 = page3_info.value
        expect(page3.locator("#mainCanvas")).to_be_visible(timeout=25000)
        page3.close()
        logger.info("1st 30 Day Follow-up popup verified and closed.")
