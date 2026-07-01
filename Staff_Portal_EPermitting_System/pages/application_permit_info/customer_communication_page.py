import logging
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class CustomerCommunicationPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Tab selection
        self.customer_comms_tab = page.get_by_role("link", name="Customer Communications")
        
        # Page Headers & Containers
        self.app_header = page.locator("#LogAppHeader")
        self.comms_heading = page.get_by_role("heading", name="Customer Communication")
        self.grid_container = page.locator(".row > div:nth-child(3)").first
        
        # Form Selectors
        self.add_new_button = page.get_by_role("button", name=" Add New")
        self.details_heading = page.get_by_role("heading", name="Customer Communication Details")
        
        # Dropdown Triggers
        self.comm_type_dropdown = page.locator("#divfrmCommunication span.k-widget.k-dropdown, #divfrmCommunication span[role='listbox']").nth(0)
        self.comm_status_dropdown = page.locator("#divfrmCommunication span.k-widget.k-dropdown, #divfrmCommunication span[role='listbox']").nth(1)
        self.review_person_dropdown = page.locator("#divReviewPerson span.k-widget.k-dropdown, #divReviewPerson span[role='listbox']").first
        
        # Message & Send
        self.message_input = page.get_by_role("textbox", name="Message to Customer *")
        self.send_button = page.get_by_role("button", name=" Send")

    def navigate_to_customer_communications(self) -> None:
        """Transitions to the Customer Communications tab."""
        logger.info("Navigating to Customer Communications tab.")
        self._wait_for_loader()
        self.js_click(self.customer_comms_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layouts exist on the page."""
        logger.info("Verifying Customer Communications layout.")
        expect(self.app_header).to_be_visible(timeout=15000)
        expect(self.comms_heading).to_be_visible(timeout=10000)
        expect(self.grid_container).to_be_visible(timeout=10000)

    def _select_option(self, trigger: Locator, option_text: str) -> None:
        """Helper to click a dropdown, wait for options, and select by text."""
        logger.info(f"Selecting dropdown option: '{option_text}'")
        self.js_click(trigger)
        self.page.wait_for_selector("[role='listbox']:visible, .k-list-container:visible", timeout=5000)
        
        # Match option containing option_text
        option = self.page.locator("[role='listbox']:visible [role='option'], .k-list-container:visible [role='option']").filter(has_text=option_text).first
        self.js_click(option)
        self._wait_for_loader()

    def add_customer_communication(self, comm_type: str = "Additional Info Requested", comm_status: str = "Waiting for Response", review_person: str = "Steve Ruskan", message: str = "test message") -> None:
        """Fills out the Customer Communication Details subform and sends it."""
        logger.info("Adding new customer communication.")
        self.js_click(self.add_new_button)
        expect(self.details_heading).to_be_visible(timeout=10000)
        
        # Select dropdown values
        self._select_option(self.comm_type_dropdown, comm_type)
        self._select_option(self.comm_status_dropdown, comm_status)
        self._select_option(self.review_person_dropdown, review_person)
        
        # Fill message and click Send
        self.js_click(self.message_input)
        self.message_input.fill(message)
        
        self.js_click(self.send_button)
        self._wait_for_loader()
        
        # Verify grid reloads and is visible
        expect(self.grid_container).to_be_visible(timeout=15000)
        logger.info("Customer communication added and verified successfully.")
