import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LicenseGenerateFormsPage(BasePage):
    """Page Object for License Generate Forms tab and validations."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Sidebar Navigation Elements
        self.licenses_menu_link = page.get_by_role("link", name=re.compile(r"Licenses\s*", re.I))
        self.license_listing_link = page.get_by_role("link", name="License Listing")

        # Listing search and edit row locators
        self.dealer_name_search = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        # Edit button of the first row dynamically
        self.first_row_edit_button = page.locator("#btnLicEdit").first

        # Tab Navigation
        self.generate_forms_tab = page.get_by_role("link", name="Generate Forms")

        # Headings & Tab Content Assertions
        self.license_details_heading = page.get_by_role("heading", name="License Details")
        self.partial_form_first = page.locator("#partial-form").first
        self.generate_forms_heading = page.get_by_role("heading", name="Generate Forms")
        self.layout_container_child = page.locator("#frmCustomer > .form-wrapper > .row > div:nth-child(2)")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("license")

    def navigate_to_license_listing(self) -> None:
        """Navigates to the Licenses -> License Listing page."""
        logger.info("Navigating to License Listing page")
        self._expand_navigation_menu()

        # If the sub-menu link is not visible, toggle the parent Licenses menu link
        if not self.license_listing_link.is_visible():
            logger.info("License Listing link not visible; clicking Licenses menu header to expand.")
            self.licenses_menu_link.click()
            self.page.wait_for_timeout(1000)

        logger.info("Clicking License Listing link")
        self.license_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def search_and_edit_first_license(self, dealer_name: str = "vansh") -> None:
        """Searches for dealer and opens/clicks Edit on the first matching record."""
        logger.info(f"Searching for dealer: {dealer_name}")
        self.dealer_name_search.click()
        self.dealer_name_search.fill(dealer_name)
        self.dealer_name_search.press("Enter")
        self.page.wait_for_timeout(2000)

        logger.info("Clicking Edit button of the first record in the table.")
        self.first_row_edit_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def navigate_to_generate_forms(self) -> None:
        """Clicks Generate Forms tab and asserts visibility of headings & layout containers."""
        logger.info("Navigating to Generate Forms tab.")
        self.generate_forms_tab.click()
        self.page.wait_for_timeout(1000)

        # Assert visual elements in the tab
        expect(self.license_details_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.generate_forms_heading).to_be_visible(timeout=10000)
        expect(self.layout_container_child).to_be_visible(timeout=10000)
        logger.info("Generate Forms tab headings and layout containers verified successfully.")

    def verify_documents_in_grid(self, expected_documents: list[str]) -> None:
        """Verifies that all the expected document records are present in the grid."""
        logger.info(f"Verifying presence of expected documents in the grid: {expected_documents}")
        
        # Locate all rows in the grid body
        rows = self.page.locator(".k-grid-content tbody tr, [role='grid'] tbody tr, tbody tr")
        
        # Poll for documents up to 15 seconds to allow asynchronous grid population
        import time
        timeout = 15.0
        start_time = time.time()
        
        actual_documents = []
        while time.time() - start_time < timeout:
            row_count = rows.count()
            actual_documents = []
            for i in range(row_count):
                td_locator = rows.nth(i).locator("td")
                if td_locator.count() > 1:
                    doc_name = td_locator.nth(1).inner_text().strip()
                    if doc_name:
                        actual_documents.append(doc_name)
            
            # Check if all expected documents are found
            if all(doc in actual_documents for doc in expected_documents):
                break
            
            self.page.wait_for_timeout(500)
            
        logger.info(f"Actual documents found in grid: {actual_documents}")
        
        # Check that each expected document is present in the actual documents list
        for doc in expected_documents:
            assert doc in actual_documents, f"Expected document '{doc}' was not found in the grid. Found: {actual_documents}"
            
        logger.info("All expected document records verified successfully in the grid.")

