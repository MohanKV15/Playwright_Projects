import re
import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LicenseCustomerActionItemsPage(BasePage):
    """Page Object for License Customer Action Items tab and communications form."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Sidebar Navigation Elements
        self.licenses_menu_link = page.get_by_role("link", name=re.compile(r"Licenses\s*", re.I))
        self.license_listing_link = page.get_by_role("link", name="License Listing")

        # Listing search and edit row locators
        self.dealer_name_search = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        # Edit button of the first row dynamically
        self.first_row_edit_button = page.locator("#btnLicEdit").first

        # Tab Navigation
        self.customer_action_items_tab = page.get_by_role("link", name="Customer Action Items")

        # Headings & Tab Content Assertions
        self.license_details_heading = page.get_by_role("heading", name="License Details")
        self.customer_communication_heading = page.get_by_role("heading", name="Customer Communication")
        self.communication_grid_block = page.locator("#frmCustomer > .form-wrapper > .row > div:nth-child(4)")

        # Trigger Add New Button
        self.add_new_button = page.get_by_role("button", name="Add New")

        # Add Form Verification labels & headings
        self.license_details_text = page.get_by_text("License Details License")
        self.comm_details_heading = page.get_by_role("heading", name="Customer Communication Details")

        # Dropdowns in Communication Details Modal
        self.option_dropdown = page.locator("#divfrmCommunication").get_by_text("Select option")
        self.option_choice = lambda name: page.get_by_role("option", name=name)

        self.status_dropdown = page.locator("#divfrmCommunication").get_by_text("Requested", exact=True)
        self.status_choice = lambda name: page.get_by_role("option", name=name)

        self.reviewer_dropdown = page.locator("#divfrmCommunication").get_by_text("Select Review Person")
        self.reviewer_choice = lambda name: page.get_by_role("option", name=name)

        # Form Inputs
        self.message_input = page.get_by_role("textbox", name="Message to Customer *")
        self.notes_input = page.get_by_role("textbox", name="Notes on Action Items")

        # Action Save Button
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

    def navigate_to_customer_action_items(self) -> None:
        """Clicks Customer Action Items tab and asserts visibility of headings & grid block."""
        logger.info("Navigating to Customer Action Items tab.")
        self.customer_action_items_tab.click()
        self.page.wait_for_timeout(1000)

        expect(self.license_details_heading).to_be_visible(timeout=10000)
        expect(self.customer_communication_heading).to_be_visible(timeout=10000)
        expect(self.communication_grid_block).to_be_visible(timeout=10000)

    def click_add_new(self) -> None:
        """Clicks Add New button and verifies communication form details load."""
        logger.info("Clicking Add New communication button.")
        self.add_new_button.click()
        self.page.wait_for_timeout(1000)

        expect(self.license_details_heading).to_be_visible(timeout=10000)
        expect(self.license_details_text).to_be_visible(timeout=10000)
        expect(self.comm_details_heading).to_be_visible(timeout=10000)
        expect(self.option_dropdown).to_be_visible(timeout=10000)

    def fill_communication_details(
        self,
        option: str = "License Fee",
        status: str = "Requested",
        reviewer: str = "Charles Craddock",
        message: str = None,
        notes: str = None,
    ) -> None:
        """Selects Kendo options and fills message / notes text fields."""
        if message is None:
            message = f"Msg {self.fake.word()}"
        if notes is None:
            notes = f"Note {self.fake.word()}"
        logger.info(f"Selecting Option: {option}")
        self.option_dropdown.click()
        self.page.wait_for_timeout(500)
        self.option_choice(option).click()
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting Status: {status}")
        self.status_dropdown.click()
        self.page.wait_for_timeout(500)
        self.status_choice(status).click()
        self.page.wait_for_timeout(500)

        logger.info(f"Selecting Reviewer: {reviewer}")
        self.reviewer_dropdown.click()
        self.page.wait_for_timeout(500)
        self.reviewer_choice(reviewer).click()
        self.page.wait_for_timeout(500)

        logger.info(f"Filling Message: {message}")
        self.message_input.click()
        self.message_input.fill(message)

        logger.info(f"Filling Notes: {notes}")
        self.notes_input.click()
        self.notes_input.fill(notes)

    def click_save(self) -> None:
        """Clicks Save and verifies communication grid is visible."""
        logger.info("Clicking Save button.")
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        expect(self.communication_grid_block).to_be_visible(timeout=10000)

    def verify_communication_record_in_grid(self, option: str, status: str) -> None:
        """Asserts that a grid row containing the option and status is visible."""
        logger.info(f"Verifying that a row containing '{option}' and '{status}' is visible in the grid.")
        row = self.communication_grid_block.locator("tr, tbody tr").filter(has_text=option).filter(has_text=status).first
        expect(row).to_be_visible(timeout=15000)
        logger.info("Record successfully verified in grid row.")
