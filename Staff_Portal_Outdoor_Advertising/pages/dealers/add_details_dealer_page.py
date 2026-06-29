import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class AddDetailsDealerPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation / Sidebar Menu Links
        self.dealers_menu_link = page.get_by_role("link", name=re.compile(r"Dealers\s*", re.I))
        self.dealer_listing_link = page.get_by_role("link", name="Dealer Listing")
        
        # Grid/Listing Actions
        self.add_dealer_button = page.get_by_role("button", name=" Add Dealer")
        
        # Heading & Form Container
        self.dealers_header = page.get_by_role("heading", name="Dealers")
        self.dealer_details_heading = page.get_by_role("heading", name="Dealer Details")
        self.form_container = page.locator("#partial-form").first
        
        # Form inputs: Mailing details
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name *")
        self.mailing_address_input = page.get_by_role("textbox", name="Mailing Address 1 *")
        self.city_input = page.locator("#city_name")
        self.state_dropdown = page.locator("#frmDealerDetailsMain").get_by_text("--**Select**--")
        self.zip_code_input = page.locator("#zip_code")
        self.phone_input = page.locator("#phone")
        self.email_input = page.get_by_role("textbox", name="Email *")
        
        # Checkboxes (Custom Kendo styled labels linked to inputs via 'for')
        self.corp_checkbox_label = page.locator("label[for='federal_dbe_main']")
        self.same_billing_checkbox_label = page.locator("label[for='same_billing_address_main']")
        
        # Form inputs: Billing details
        self.billing_address_input = page.get_by_role("textbox", name="Billing Address 1 *")
        self.billing_city_input = page.locator("#BillingCity")
        self.billing_state_dropdown = page.locator("#divforcompanybillingaddress").get_by_text("--Select--")
        self.billing_zip_code_input = page.locator("#BillingZipCode")
        
        # Save Actions
        self.save_button = page.get_by_role("button", name=" Save")
        self.ok_confirm_button = page.get_by_role("button", name="OK")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("dealer")

    def navigate_to_add_dealer(self) -> None:
        """Navigates to Dealer Listing then clicks Add Dealer button."""
        logger.info("Navigating to Add Dealer page")
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
        
        # Verify page header
        expect(self.dealers_header).to_be_visible(timeout=15000)
        
        logger.info("Clicking 'Add Dealer' button")
        self.add_dealer_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        
        # Verify Dealer Details form loaded
        expect(self.dealer_details_heading).to_be_visible(timeout=15000)
        expect(self.form_container).to_be_visible(timeout=15000)

    def select_dropdown_first_option(self, dropdown_locator) -> str:
        """Clicks a dropdown, waits for the options list, and selects the first non-placeholder option."""
        logger.info("Opening Kendo Dropdown")
        dropdown_locator.first.click()
        self.page.wait_for_timeout(500)
        
        # Wait for visible options list items (using :visible to avoid matching hidden elements)
        options = self.page.locator("li[role='option']:visible, .k-list-container:visible li")
        options.first.wait_for(state="visible", timeout=5000)
        
        # Loop through options to click the first real option (excluding placeholder/Select)
        for i in range(options.count()):
            text = options.nth(i).inner_text().strip()
            if text and "select" not in text.lower():
                logger.info(f"Selecting dropdown option: '{text}'")
                options.nth(i).click()
                self.page.wait_for_timeout(500)
                return text
                
        # Fallback
        logger.warning("No option without 'Select' found, clicking first option")
        text = options.first.inner_text().strip()
        options.first.click()
        self.page.wait_for_timeout(500)
        return text

    def fill_dealer_details(self, details: dict) -> dict:
        """Fills the Add Dealer form details and returns the final mapped values used (for dropdown verification)."""
        logger.info("Filling Mailing details section")
        
        self.dealer_name_input.fill(details["dealer_name"])
        self.mailing_address_input.fill(details["mailing_address"])
        self.city_input.fill(details["city"])
        
        # Select first State option
        selected_state = self.select_dropdown_first_option(self.state_dropdown)
        
        self.zip_code_input.fill(details["zip_code"])
        self.phone_input.click()
        self.phone_input.fill("")
        self.phone_input.press_sequentially(re.sub(r"\D", "", details["phone"]), delay=50)
        self.email_input.fill(details["email"])
        
        # Check current state of Corporation checkbox
        is_corp_checked = self.page.locator("#federal_dbe_main").is_checked()
        if details.get("is_corporation", False) != is_corp_checked:
            logger.info("Toggling Corporation checkbox")
            self.corp_checkbox_label.click()
            self.page.wait_for_timeout(500)
            
        # Toggle 'Same Billing Address' checkbox depending on same_billing value
        is_same_billing_checked = self.page.locator("#same_billing_address_main").is_checked()
        if details.get("same_billing", True) != is_same_billing_checked:
            logger.info("Toggling Same Billing Address checkbox")
            self.same_billing_checkbox_label.click()
            self.page.wait_for_timeout(1000)
            
        selected_billing_state = ""
        if not details.get("same_billing", True):
            self.billing_address_input.fill(details["billing_address"])
            self.billing_city_input.fill(details["billing_city"])
            
            selected_billing_state = self.select_dropdown_first_option(self.billing_state_dropdown)
            
            self.billing_zip_code_input.fill(details["billing_zip_code"])
            
        # Return final values including dynamically selected dropdown values
        final_values = details.copy()
        final_values["state"] = selected_state
        if not details.get("same_billing", True):
            final_values["billing_state"] = selected_billing_state
            
        return final_values

    def save_dealer(self) -> None:
        """Clicks Save, asserts the success alert, and dismisses it."""
        logger.info("Saving dealer record")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        
        # Verify success popups
        expect(self.page.get_by_text("Record saved successfully")).to_be_visible(timeout=15000)
        
        logger.info("Clicking OK on success dialog")
        self.ok_confirm_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def verify_saved_details(self, expected: dict) -> None:
        """Verifies that the saved details displayed on the page match the inputs."""
        logger.info("Verifying displayed values match saved details")
        
        # Verify page remains on Details mode
        expect(self.dealer_details_heading).to_be_visible(timeout=10000)
        expect(self.form_container).to_be_visible(timeout=10000)
        
        # Verify input fields hold correct values
        expect(self.dealer_name_input).to_have_value(expected["dealer_name"])
        expect(self.mailing_address_input).to_have_value(expected["mailing_address"])
        expect(self.city_input).to_have_value(expected["city"])
        
        # Kendo dropdown displays the selected option text in its element
        expect(self.page.locator("#frmDealerDetailsMain").get_by_text(expected["state"])).to_be_visible(timeout=10000)
        
        expect(self.zip_code_input).to_have_value(expected["zip_code"])
        # Format/phone might be sanitized or held raw. Clean check:
        phone_val = self.phone_input.input_value()
        clean_phone_val = re.sub(r"\D", "", phone_val)
        clean_expected_phone = re.sub(r"\D", "", expected["phone"])
        assert clean_expected_phone in clean_phone_val or clean_phone_val in clean_expected_phone, \
            f"Phone mismatch: expected '{expected['phone']}', got '{phone_val}'"
            
        expect(self.email_input).to_have_value(expected["email"])
        
        if not expected.get("same_billing", True):
            expect(self.billing_address_input).to_have_value(expected["billing_address"])
            expect(self.billing_city_input).to_have_value(expected["billing_city"])
            expect(self.page.locator("#divforcompanybillingaddress").get_by_text(expected["billing_state"])).to_be_visible(timeout=10000)
            expect(self.billing_zip_code_input).to_have_value(expected["billing_zip_code"])
