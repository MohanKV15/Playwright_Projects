import re
import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AddLicenseApplicationPage(BasePage):
    """Page Object for Add License Application and verification actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Sidebar Navigation Elements
        self.licenses_menu_link = page.get_by_role("link", name=re.compile(r"Licenses\s*", re.I))
        self.license_listing_link = page.get_by_role("link", name="License Listing")

        # Add Button & Initial Headers
        self.add_license_app_button = page.get_by_role("button", name=" Add License Application")
        self.license_details_h3 = page.locator("h3").filter(has_text="License Details")
        self.partial_form_container = page.locator("#partial-form")
        self.app_info_heading = page.get_by_role("heading", name="Application Information")

        # Dealer Find & Selection modal
        self.btn_license_find = page.locator("#btnLicenseFind")
        self.dealer_name_modal_input = page.locator("#Dealer_Name")
        self.modal_search_button = page.get_by_role("button", name="Search")
        self.selected_chk = page.locator("#selectedChk")

        # Non-Resident Authorization section
        self.non_res_auth_text = page.get_by_text("Non-Resident Authorization of")
        self.non_res_bond_text = page.get_by_text("Non-New Jersey Resident Authorized to do Business Surety Bond Received? Bond")
        self.bond_received_chk = page.locator(".k-checkbox-label").first

        # Agent Information Inputs
        self.agent_mailing_address_2 = page.get_by_label("Agent's Mailing Address 2")
        self.city_name_input = page.locator("#city_name")
        self.state_dropdown_trigger = page.locator("#frmLicDetail").get_by_text("--Select--")
        self.state_option = lambda name: page.get_by_role("option", name=name)
        self.zip_code_input = page.locator("#zip_code")
        self.agent_first_name = page.get_by_label("Agent's First Name")
        self.com_phone = page.locator("#com_phone")

        # License Details h4
        self.license_details_h4 = page.locator("h4").filter(has_text="License Details")

        # Date pickers (calendar dropdown triggers & day selectors)
        self.select_buttons = page.get_by_label("select")
        self.day_link = lambda day: page.get_by_role("link", name=str(day), exact=True).first

        # Status Dropdown
        self.status_dropdown_trigger = page.locator("#frmLicDetail").get_by_text("--Select Status--")
        self.status_option = lambda status: page.get_by_role("option", name=status, exact=True)

        # Action Buttons
        self.save_button = page.get_by_text("Save")

        # Verification Search inputs & results grid
        self.dealer_name_search = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.results_wrapper = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.grid_cell_result = lambda name: page.get_by_role("gridcell", name=name)

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

    def click_add_license_application(self) -> None:
        """Clicks on Add License Application button and verifies initial headings."""
        logger.info("Clicking Add License Application button.")
        self.add_license_app_button.click()
        self.page.wait_for_timeout(1000)

        # Assert initial visibility of headings and forms
        expect(self.license_details_h3).to_be_visible(timeout=10000)
        expect(self.partial_form_container).to_be_visible(timeout=10000)
        expect(self.app_info_heading).to_be_visible(timeout=10000)

    def handle_popup_by_text(self, text: str, timeout: int = 15000) -> None:
        """Asserts a visible Kendo popup containing text exists and clicks its OK button."""
        logger.info(f"Waiting for visible popup containing text: '{text}'")
        dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible").filter(has_text=text).first
        dialog.wait_for(state="visible", timeout=timeout)
        logger.info(f"Found visible popup containing '{text}'. Clicking OK.")
        dialog.get_by_role("button", name="OK").click()
        self.page.wait_for_timeout(1000)

    def search_and_select_dealer_in_modal(self, dealer_name: str = "vansh") -> None:
        """Clicks Find Dealer, searches for the dealer, checks result and dismisses modal popup."""
        logger.info("Opening Find Dealer modal.")
        self.btn_license_find.click()
        self.page.wait_for_timeout(1000)

        logger.info(f"Searching for dealer: {dealer_name} in modal.")
        self.dealer_name_modal_input.click()
        self.dealer_name_modal_input.fill(dealer_name)
        self.modal_search_button.click()
        self.page.wait_for_timeout(1000)

        logger.info("Selecting/checking the dealer from results.")
        self.selected_chk.check()

        # Handle modal popup expectation
        self.handle_popup_by_text("u-njoda.bemcorp.net")

        # Assert non-resident text is visible
        expect(self.non_res_auth_text).to_be_visible(timeout=10000)
        expect(self.non_res_bond_text).to_be_visible(timeout=10000)

    def fill_agent_and_non_resident_details(
        self,
        address_2: str = None,
        city: str = None,
        state: str = "Alaska",
        zip_code: str = None,
        first_name: str = None,
        phone: str = None,
    ) -> None:
        """Fills non-resident bond checkbox and agent's personal/mailing details."""
        fake = Faker()
        address_2 = address_2 or fake.secondary_address()
        city = city or fake.city()
        zip_code = zip_code or fake.postcode()[:5]
        first_name = first_name or fake.first_name()
        phone = phone or fake.numerify("###-###-####")

        logger.info("Checking Bond Received checkbox.")
        self.bond_received_chk.click()
        self.page.wait_for_timeout(500)

        # Agent signature / date: select nth(1) of date pickers and choose "15"
        logger.info("Setting Agent Signature Date to 15.")
        self.select_buttons.nth(1).click()
        self.page.wait_for_timeout(500)
        self.js_click(self.day_link("15"))
        self.page.wait_for_timeout(500)

        # Mailing Address 2
        logger.info(f"Filling Address 2: {address_2}")
        self.agent_mailing_address_2.click()
        self.agent_mailing_address_2.fill(address_2)

        # City Name
        logger.info(f"Filling City: {city}")
        self.city_name_input.click()
        self.city_name_input.fill(city)

        # State Dropdown selection
        logger.info(f"Selecting State: {state}")
        self.state_dropdown_trigger.click()
        self.page.wait_for_timeout(500)
        self.js_click(self.state_option(state))
        self.page.wait_for_timeout(500)

        # Zip Code
        logger.info(f"Filling Zip Code: {zip_code}")
        self.zip_code_input.click()
        self.zip_code_input.fill(zip_code)

        # Agent's First Name
        logger.info(f"Filling Agent First Name: {first_name}")
        self.agent_first_name.click()
        self.agent_first_name.fill(first_name)

        # Phone Number
        logger.info(f"Filling Phone: {phone}")
        self.com_phone.click()
        self.com_phone.fill(phone)

    def fill_license_details(self, status: str = "VALID") -> None:
        """Fills dates and status inside the License Details (h4) section."""
        logger.info("Asserting License Details h4 is visible.")
        expect(self.license_details_h4).to_be_visible(timeout=10000)

        # Set Effective Date: nth(3) select button click, select "15"
        logger.info("Setting Effective Date to 15.")
        self.select_buttons.nth(3).click()
        self.page.wait_for_timeout(500)
        self.js_click(self.day_link("15"))
        self.page.wait_for_timeout(500)

        # Set Expiration Date: nth(4) select button click, select "15"
        logger.info("Setting Expiration Date to 15.")
        self.select_buttons.nth(4).click()
        self.page.wait_for_timeout(500)
        self.js_click(self.day_link("15"))
        self.page.wait_for_timeout(500)

        # Set Status Dropdown selection
        logger.info(f"Selecting Status: {status}")
        self.status_dropdown_trigger.click()
        self.page.wait_for_timeout(500)
        self.js_click(self.status_option(status))
        self.page.wait_for_timeout(500)

    def click_save(self) -> None:
        """Clicks Save button."""
        logger.info("Clicking Save button.")
        self.save_button.click()
        self.page.wait_for_timeout(1000)

    def handle_save_popups(self) -> None:
        """Asserts presence of confirmation popup texts and clicks OK."""
        self.handle_popup_by_text("Operation Completed")

    def search_dealer_and_verify_result(self, dealer_name: str = "vansh", cell_value: str = "001056") -> None:
        """Re-navigates to License Listing, searches for dealer and asserts grid cell visibility."""
        logger.info("Re-navigating to License Listing page for verification.")
        self.navigate_to_license_listing()

        logger.info(f"Searching for dealer Name: {dealer_name}")
        self.dealer_name_search.click()
        self.dealer_name_search.fill(dealer_name)
        self.search_button.click()
        self.page.wait_for_timeout(2000)

        # Assert resulting grid content wrapper is visible
        expect(self.results_wrapper).to_be_visible(timeout=10000)
        # Assert grid cell exists
        expect(self.grid_cell_result(cell_value).first).to_be_visible(timeout=10000)
        logger.info(f"Verification successful: Gridcell containing '{cell_value}' is visible.")
