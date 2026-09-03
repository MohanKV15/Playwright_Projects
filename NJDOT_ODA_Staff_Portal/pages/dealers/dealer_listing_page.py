import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DealerListingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation / Sidebar Menu Links
        self.dealers_menu_link = page.get_by_role("link", name=re.compile(r"Dealers\s*", re.I))
        self.dealer_listing_link = page.get_by_role("link", name="Dealer Listing")
        
        # Search criteria
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        
        # Search Results (First column cell of the first row to avoid clicking the Delete button in the row)
        self.first_record_details_link = page.locator(".k-grid-content tbody tr td, tbody tr td, tr td").first
        
        
        # Dealer Details Tab/Section Heading
        self.dealer_details_heading = page.get_by_role("heading", name="Dealer Details")
        
        # Contacts Section
        self.contacts_heading = page.get_by_role("heading", name="Dealer Contacts")
        self.contacts_container = page.locator("#partial-form").nth(1)
        self.add_contact_button = page.get_by_role("button", name=" Add Contact")
        self.back_button = page.get_by_role("button", name=" Back")
        
        # Name Change Section
        self.name_change_heading = page.get_by_role("heading", name="Dealer Name Change")
        self.name_change_container = page.locator("#partial-form").nth(3)
        self.add_request_button = page.get_by_role("button", name=" Add Request")
        self.name_change_form = page.locator("#divDealerDetailsNameChange #partial-form")
        self.cancel_button = page.locator("#btnDealerDealerCancel")
        
        # Violations Section
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.violations_container = page.locator("#partial-form").nth(4)

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("dealer")

    def dismiss_any_kendo_popup_dialog(self, timeout_ms: int = 1500) -> bool:
        """Checks if a Kendo popup dialog (warning or error) is visible, and clicks OK to dismiss it."""
        ok_btn = self.page.get_by_role("button", name="OK")
        try:
            if ok_btn.is_visible(timeout=timeout_ms):
                logger.info("Dismissing active popup dialog by clicking OK")
                ok_btn.click()
                self.page.wait_for_timeout(1000)
                return True
        except Exception:
            pass
        return False

    def navigate_to_dealer_listing(self) -> None:
        """Navigates to the Dealers category then clicks Dealer Listing."""
        logger.info("Navigating to Dealer Listing page")
        self._expand_navigation_menu()
        
        # If the sub-menu link is not visible, toggle the parent Dealers menu link
        if not self.dealer_listing_link.is_visible():
            logger.info("Clicking Dealers menu link to expand.")
            self.dealers_menu_link.click()
            self.page.wait_for_timeout(1000)
        
        logger.info("Clicking Dealer Listing submenu link")
        self.dealer_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def search_dealer(self, dealer_name: str = "vansh") -> None:
        """Enters the dealer name and clicks the search button."""
        logger.info(f"Searching for dealer: '{dealer_name}'")
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)
        self.page.wait_for_timeout(500)
        
        logger.info("Clicking Search button")
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def open_first_record(self) -> None:
        """Clicks the details/action element of the first record in the results."""
        logger.info("Opening the first dealer record from search results")
        self.first_record_details_link.first.wait_for(state="visible", timeout=10000)
        self.first_record_details_link.first.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        
        # Self-healing check for any onload popup dialogs
        self.dismiss_any_kendo_popup_dialog(timeout_ms=5000)
        
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)

    def verify_dealer_details(self) -> None:
        """Validates that dealer details and contacts sections are visible."""
        logger.info("Verifying Dealer Details and Contacts sections visibility")
        self.dismiss_any_kendo_popup_dialog(timeout_ms=1000)
        expect(self.dealer_details_heading).to_be_visible(timeout=15000)
        expect(self.contacts_heading).to_be_visible(timeout=10000)
        expect(self.contacts_container).to_be_visible(timeout=10000)

    def navigate_add_contact_and_back(self) -> None:
        """Clicks 'Add Contact', verifies the navigation, and clicks 'Back' to return."""
        logger.info("Clicking 'Add Contact' button")
        self.dismiss_any_kendo_popup_dialog(timeout_ms=2000)
        self.add_contact_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        
        logger.info("Returning to dealer details using 'Back' button")
        self.back_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        
        # Verify we are back on the dealer details page
        expect(self.dealer_details_heading).to_be_visible(timeout=10000)

    def request_name_change_and_cancel(self) -> None:
        """Verifies name change section, adds request, verifies form, and cancels."""
        logger.info("Verifying Dealer Name Change section")
        self.dismiss_any_kendo_popup_dialog(timeout_ms=1000)
        expect(self.name_change_heading).to_be_visible(timeout=10000)
        expect(self.name_change_container).to_be_visible(timeout=10000)
        
        logger.info("Clicking 'Add Request' button")
        self.add_request_button.click()
        self.page.wait_for_timeout(1000)
        
        logger.info("Verifying name change form container")
        expect(self.name_change_heading).to_be_visible(timeout=10000)
        expect(self.name_change_form).to_be_visible(timeout=10000)
        
        logger.info("Clicking cancel button to abort name change request")
        self.cancel_button.click()
        self.page.wait_for_timeout(1500)

    def verify_violation_details(self) -> None:
        """Validates that violation details and its container section are visible."""
        logger.info("Verifying Violation Details section visibility")
        self.dismiss_any_kendo_popup_dialog(timeout_ms=1000)
        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.violations_container).to_be_visible(timeout=10000)
