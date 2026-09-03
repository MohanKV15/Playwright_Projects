import logging
import re
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitTransferCustomerActionItemsPage(BasePage):
    """Page Object Model for the Permit Transfer Customer Action Items tab in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Tab navigation
        self.customer_action_items_tab = page.get_by_role("link", name="Customer Action Items")

        # Headings & Tab Content Assertions
        self.transfer_details_heading = page.get_by_role("heading", name="Transfer Details")
        self.partial_form_first = page.locator("#partial-form").first
        self.customer_communication_heading = page.get_by_role("heading", name="Customer Communication")
        self.grid_content = page.locator(".k-grid-content")
        self.add_new_btn = page.get_by_role("button", name="Add New")

        # Details Page Elements
        self.details_transfer_details_text = page.get_by_text("Transfer Details Permit")
        self.comm_details_heading = page.get_by_role("heading", name="Customer Communication Details")
        self.select_option_dropdown = page.locator("#divfrmCommunication").get_by_text("Select option")
        self.status_dropdown = page.locator("#divfrmCommunication").get_by_text("Requested", exact=True)
        self.review_person_dropdown = page.locator("#divfrmCommunication").get_by_text("Select Review Person")
        self.message_input = page.get_by_role("textbox", name="Message to Customer *")
        
        self.save_button = page.get_by_role("button", name=" Save")
        self.results_container = page.locator("#frmCustomer > .form-wrapper > .row > div:nth-child(4)")

    def navigate_to_customer_action_items(self) -> None:
        """Navigates to the Customer Action Items tab and verifies headings & grids load."""
        logger.info("Navigating to Customer Action Items tab.")
        self.customer_action_items_tab.wait_for(state="visible", timeout=10000)
        self.customer_action_items_tab.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.transfer_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.customer_communication_heading).to_be_visible(timeout=10000)
        expect(self.grid_content).to_be_visible(timeout=10000)

    def click_add_new(self) -> None:
        """Clicks Add New button and verifies Details form view loads."""
        logger.info("Clicking Add New button.")
        self.add_new_btn.wait_for(state="visible", timeout=10000)
        self.add_new_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.partial_form_first).to_be_visible(timeout=15000)
        expect(self.details_transfer_details_text).to_be_visible(timeout=10000)
        expect(self.comm_details_heading).to_be_visible(timeout=10000)
        expect(self.select_option_dropdown).to_be_visible(timeout=10000)

    def _select_dropdown_option_by_name(self, name: str) -> None:
        """Selects a specific option by name in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        option = self.page.locator("[role='listbox']:visible").get_by_role("option", name=name, exact=True)
        logger.info(f"Selecting option '{name}' in Kendo dropdown")
        self.js_click(option)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)

    def fill_communication_details(
        self,
        option_name: str = "Additional Info Requested",
        review_person: str = "Charles Craddock",
        message: str = None
    ) -> None:
        """Fills out the Customer Communication details using Kendo dropdowns and Faker."""
        logger.info("Filling Customer Communication details.")

        # Select option
        self.select_option_dropdown.click()
        self._select_dropdown_option_by_name(option_name)

        # Click status (Requested)
        logger.info("Clicking status dropdown.")
        self.status_dropdown.click()
        self.page.wait_for_timeout(500)

        # Select Review Person
        self.review_person_dropdown.click()
        self._select_dropdown_option_by_name(review_person)

        # Fill message (Faker)
        if not message:
            message = self.fake.paragraph(nb_sentences=2)
        logger.info(f"Filling Message: {message}")
        self.message_input.click()
        self.message_input.fill(message)

    def save_communication(self) -> None:
        """Saves the customer communication and verifies return to grid listing."""
        logger.info("Saving Customer Communication.")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.results_container).to_be_visible(timeout=15000)
