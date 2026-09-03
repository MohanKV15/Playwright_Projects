import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitPaymentPage(BasePage):
    """Page Object Model for the Permit Payments section under Renewals module."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Menu Links
        self.renewals_menu_link = page.get_by_role("link", name="Renewals ")
        self.permit_payments_link = page.get_by_role("link", name="Permit Payments")

        # Headings & Containers
        self.permit_payments_heading = page.get_by_role("heading", name="Permit Renewal Payments")
        self.help_text = page.get_by_text("(Please search for the dealer")
        
        # Payment Details Page Elements
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.payment_selection_heading = page.get_by_role("heading", name="Payment Selection")
        self.partial_form_first = page.locator("#partial-form").first
        self.partial_form_second = page.locator("#partial-form").nth(1)

        # Filter Inputs & Buttons
        self.search_button = page.get_by_role("button", name=" Search")
        self.back_button = page.get_by_role("button", name=" Back")
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.dealer_number_input = page.get_by_role("textbox", name="Dealer Number")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all renewals links are visible."""
        logger.info("Expanding Renewals PanelBar navigation panel via JS.")
        self._expand_kendo_panel("renewal")

    def navigate_to_permit_payments(self) -> None:
        """Navigates to Renewals -> Permit Payments and asserts initial page elements are visible."""
        logger.info("Navigating to Permit Payments page")
        self._expand_navigation_menu()

        # If sub-menu link is not visible, toggle the parent Renewals menu link
        if not self.permit_payments_link.is_visible():
            logger.info("Permit Payments link not visible; clicking Renewals menu header to expand.")
            self.renewals_menu_link.click()
            self.page.wait_for_timeout(1000)

        self.permit_payments_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

        # Assert initial view elements
        expect(self.permit_payments_heading).to_be_visible(timeout=15000)
        expect(self.help_text).to_be_visible(timeout=10000)

    def select_status(self, status: str) -> None:
        """Clicks the status dropdown inside #renewalPaymentDiv and selects the matching status."""
        logger.info(f"Selecting status: '{status}'")
        self._wait_for_loader()
        
        # Trigger the dropdown wrapper
        dropdown_trigger = self.page.locator("#renewalPaymentDiv").locator(".k-input, .k-dropdown-wrap, [role='listbox']").first
        dropdown_trigger.click()
        self.page.wait_for_timeout(500)
        
        # Click the dropdown option matching the status
        self.js_click(self.page.get_by_role("option", name=status, exact=True))
        self.page.wait_for_timeout(500)

    def click_search(self) -> None:
        """Clicks the Search button and synchronizes with background processes."""
        logger.info("Clicking Search button")
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def has_grid_records(self) -> bool:
        """Checks if the search results grid contains any records."""
        grid_row_selector = ".k-grid-content tbody tr, #renewalPaymentGrid tbody tr, [role='grid'] tbody tr"
        try:
            # Check if grid contains any row
            rows = self.page.locator(grid_row_selector)
            if rows.count() == 0:
                return False
            
            # Check if the first row has the text "No records to display"
            first_row_text = rows.first.inner_text().strip()
            if "no records to display" in first_row_text.lower():
                return False
            
            return True
        except Exception:
            return False

    def get_first_record_dealer_info(self) -> tuple[str, str]:
        """Reads and returns the Dealer Name and Dealer Number of the first record in the grid dynamically."""
        self._wait_for_loader()
        grid_row_selector = ".k-grid-content tbody tr, #grdPayments tbody tr, [role='grid'] tbody tr"
        self.page.wait_for_selector(grid_row_selector, timeout=15000)
        first_row = self.page.locator(grid_row_selector).first

        cells = first_row.locator("td")
        cell_count = cells.count()
        logger.info(f"First row cell count: {cell_count}")
        
        dealer_name = ""
        dealer_number = ""
        
        if cell_count > 3:
            dealer_name = cells.nth(2).inner_text().strip()
            dealer_number = cells.nth(3).inner_text().strip()
            
        logger.info(f"Extracted Dealer Number: '{dealer_number}', Dealer Name: '{dealer_name}'")
        return dealer_name, dealer_number

    def search_by_dealer_info(self, dealer_name: str, dealer_number: str) -> None:
        """Enters the dealer name and number into the fields and clicks search."""
        self._wait_for_loader()
        logger.info(f"Filtering grid by Dealer Name: '{dealer_name}' and Dealer Number: '{dealer_number}'")
        
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)
        self.page.wait_for_timeout(300)
        
        self.dealer_number_input.click()
        self.dealer_number_input.fill(dealer_number)
        self.page.wait_for_timeout(300)

        self.click_search()

    def clear_search_fields(self) -> None:
        """Clears the Dealer Name and Dealer Number fields."""
        logger.info("Clearing search input fields")
        self.dealer_name_input.click()
        self.dealer_name_input.clear()
        self.page.wait_for_timeout(200)

        self.dealer_number_input.click()
        self.dealer_number_input.clear()
        self.page.wait_for_timeout(200)

    def verify_payment_details_page(self) -> None:
        """Asserts that the page has navigated to the Payment Details page and validates forms."""
        logger.info("Verifying Payment Details headings and form containers")
        expect(self.payment_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        
        # Payment Selection heading is only visible for unpaid/applicable bills, so check nth(1) container too
        expect(self.partial_form_second).to_be_visible(timeout=10000)

    def click_back(self) -> None:
        """Clicks the Back button to return to the search list."""
        logger.info("Clicking Back button")
        self.back_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()



