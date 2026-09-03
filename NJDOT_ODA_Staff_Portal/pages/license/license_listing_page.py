import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LicenseListingPage(BasePage):
    """Page Object for License Listing page and license details actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Sidebar Navigation Elements
        self.licenses_menu_link = page.get_by_role("link", name=re.compile(r"Licenses\s*", re.I))
        self.license_listing_link = page.get_by_role("link", name="License Listing")

        # Search Criteria Inputs & Buttons
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.dealer_number_input = page.get_by_role("textbox", name="Dealer Number")
        self.search_button = page.get_by_role("button", name=" Search")

        # Detail Visibility Assertions
        self.license_details_h3 = page.locator("h3").filter(has_text="License Details")
        self.partial_form_container = page.locator("#partial-form")
        self.app_info_heading = page.get_by_role("heading", name="Application Information")
        self.non_res_heading = page.get_by_role("heading", name="Non-Resident Authorization of")
        self.non_res_bond_text = page.get_by_text("Non-New Jersey Resident Authorized to do Business Surety Bond Received? Bond")
        self.license_details_h4 = page.locator("h4").filter(has_text="License Details")

        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")

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

    def search_dealer_license(self, name: str = "vansh", number: str = "701001") -> None:
        """Search for a dealer's license by Name and Number."""
        logger.info(f"Searching license for dealer Name: '{name}', Number: '{number}'")
        self.dealer_name_input.wait_for(state="visible", timeout=15000)
        self.dealer_name_input.click()
        self.dealer_name_input.fill(name)
        self.dealer_number_input.click()
        self.dealer_number_input.fill(number)

        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def assert_license_details_visible(self) -> None:
        """Verify visibility of all required License Details sections and text fields."""
        logger.info("Asserting License Details headings and forms are visible.")

        # Self-healing click fallback in case detail view needs a click on the grid record
        edit_btn = self.page.locator("#btnLicEdit, a.k-grid-edit, button.k-grid-edit, [role='gridcell'] button").first
        if edit_btn.count() > 0 and edit_btn.is_visible() and not self.license_details_h3.is_visible():
            logger.info("Details section not visible; clicking the Edit button of the first record.")
            edit_btn.click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(1500)

        expect(self.license_details_h3).to_be_visible(timeout=15000)
        expect(self.partial_form_container).to_be_visible(timeout=10000)
        expect(self.app_info_heading).to_be_visible(timeout=10000)
        expect(self.non_res_heading).to_be_visible(timeout=10000)
        expect(self.non_res_bond_text).to_be_visible(timeout=10000)
        expect(self.license_details_h4).to_be_visible(timeout=10000)

    def click_save(self) -> None:
        """Click the Save button."""
        logger.info("Clicking the Save button.")
        self.save_button.wait_for(state="visible", timeout=10000)
        self.save_button.click()
        self.page.wait_for_timeout(2000)

    def handle_kendo_popup_and_ok(self) -> None:
        """Assert popup text is visible and click OK to dismiss it."""
        logger.info("Handling the Kendo alert dialog.")

        # Assert popup alert contents
        popup_text_1 = self.page.get_by_text("u-njoda.bemcorp.net")
        popup_text_2 = self.page.get_by_text("Operation Completed")

        # Fallback assertion if either is visible
        try:
            expect(popup_text_1.first).to_be_visible(timeout=15000)
        except Exception:
            expect(popup_text_2.first).to_be_visible(timeout=15000)

        # Click OK
        ok_button = self.page.get_by_role("button", name="OK")
        ok_button.wait_for(state="visible", timeout=10000)
        ok_button.click()
        logger.info("Successfully clicked OK and dismissed dialog.")
        self.page.wait_for_timeout(1000)
