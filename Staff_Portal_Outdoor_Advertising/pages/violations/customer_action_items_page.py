import logging
import re
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationCustomerActionItemsPage(BasePage):
    """Page Object Model for the Violations Customer Action Items section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")

        # Search elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.dealer_name_search_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.customer_results_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.edit_violation_button = page.locator("#btnViolationsEdit")

        # Customer Action Items Tab Elements
        self.customer_action_items_tab = page.get_by_role("link", name="Customer Action Items")
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.customer_communication_heading = page.get_by_role("heading", name="Customer Communication")
        self.communication_grid_container = page.locator("#frmCustomer > .form-wrapper > .row > div:nth-child(4)")
        self.add_new_button = page.get_by_role("button", name="Add New")

        # Communication Form Page Elements
        self.app_details_dialog_container = page.locator("div").filter(has_text="Application Details Permit").nth(4)
        self.violation_details_text = page.get_by_text("Violation Details Violation")
        self.communication_details_heading = page.get_by_role("heading", name="Customer Communication Details")

        # Dropdowns inside #divfrmCommunication
        self.option_dropdown = page.locator("#divfrmCommunication").get_by_text("Select option")
        self.status_dropdown = page.locator("#divfrmCommunication").get_by_text("Requested", exact=True)
        self.review_person_dropdown = page.locator("#divfrmCommunication").get_by_text("Select Review Person")

        # Text fields
        self.message_input = page.get_by_role("textbox", name="Message to Customer *")
        self.notes_input = page.get_by_role("textbox", name="Notes on Action Items")
        self.save_button = page.get_by_role("button", name=" Save")

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Violations."""
        logger.info("Expanding Violations PanelBar navigation.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations Listing."""
        self._expand_navigation_menu()
        if not self.violations_listing_link.is_visible():
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Searches violations grid by dealer name."""
        logger.info(f"Searching for dealer '{dealer_name}' in listing grid.")
        self.dealer_name_search_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_search_input.click()
        self.dealer_name_search_input.fill(dealer_name)
        self.search_button.click()
        self._wait_for_loader()
        expect(self.customer_results_container).to_be_visible(timeout=15000)

    def click_edit_on_first_record(self) -> None:
        """Clicks edit button on the first record in search results."""
        logger.info("Opening the first violation record details.")
        self.edit_violation_button.first.wait_for(state="visible", timeout=10000)
        self.edit_violation_button.first.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def navigate_to_customer_action_items(self) -> None:
        """Navigates to Customer Action Items tab from Details view."""
        logger.info("Navigating to Customer Action Items tab.")
        self.customer_action_items_tab.wait_for(state="visible", timeout=10000)
        self.customer_action_items_tab.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Verify page contents are loaded
        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.customer_communication_heading).to_be_visible(timeout=10000)
        expect(self.communication_grid_container).to_be_visible(timeout=10000)

    def click_add_new(self) -> None:
        """Clicks Add New button and verifies form layout."""
        logger.info("Clicking Add New button.")
        self.add_new_button.wait_for(state="visible", timeout=10000)
        self.add_new_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Assert details headings are loaded
        expect(self.app_details_dialog_container).to_be_visible(timeout=15000)
        expect(self.violation_details_heading).to_be_visible(timeout=10000)
        expect(self.violation_details_text).to_be_visible(timeout=10000)
        expect(self.communication_details_heading).to_be_visible(timeout=10000)

    def fill_communication_details(self) -> None:
        """Fills out Customer Communication details, always selecting the 1st visible dropdown options."""
        logger.info("Filling customer communication details using Faker.")
        fake = Faker()

        # 1. Option dropdown
        logger.info("Opening Option dropdown.")
        self.option_dropdown.click()
        self._select_first_dropdown_option()

        # 2. Status dropdown
        logger.info("Opening Status dropdown.")
        self.status_dropdown.click()
        self._select_first_dropdown_option()

        # 3. Review Person dropdown
        logger.info("Opening Review Person dropdown.")
        self.review_person_dropdown.click()
        self._select_first_dropdown_option()

        # 4. Fill Message
        logger.info("Filling Message to Customer.")
        self.message_input.click()
        self.message_input.fill(fake.paragraph(nb_sentences=2))

        # Focus element out
        self.page.locator(".\\32 .col-md-3").click()

        # 5. Fill Notes
        logger.info("Filling Notes on Action Items.")
        self.notes_input.click()
        self.notes_input.fill(fake.sentence())

    def save_communication(self) -> None:
        """Saves the record and verifies grid listing returns."""
        logger.info("Saving Customer Communication record.")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Verify grid view has loaded successfully
        expect(self.communication_grid_container).to_be_visible(timeout=15000)

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option']")
        self.page.wait_for_timeout(500)
        
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            options.nth(1).click()
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            options.nth(0).click()
        self.page.wait_for_timeout(500)
