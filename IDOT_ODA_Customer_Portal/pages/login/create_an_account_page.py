import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class CreateAnAccountPage(BasePage):
    """
    Page Object representing the IDOT Outdoor Advertising Company Registration / Create an Account page.
    Encapsulates all recorded elements for Company Details, Physical Address, Billing Address,
    Point of Contact information, and Back button navigation.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Page Headings & Branding
        self.header_title = page.get_by_role("heading", name=re.compile(r"Outdoor Advertising", re.IGNORECASE))
        self.registration_title = page.get_by_role("heading", name="Company Registration")
        self.company_details_title = page.get_by_role("heading", name="Company Details")

        # Company Details Form Fields
        self.company_name_input = page.locator("#name_")
        self.address_line1_input = page.locator("#address_1")
        self.city_input = page.locator("#city_name")
        self.state_dropdown_trigger = page.get_by_text("Illinois").first
        self.state_option_florida = page.get_by_role("option", name="Florida")
        self.first_dropdown_option = page.get_by_role("option").first
        self.zip_code_input = page.locator("#zip_code")
        self.phone_input = page.locator("#phone")
        self.email_input = page.locator("#email")

        # Checkboxes
        self.same_as_physical_checkbox = page.locator(".k-checkbox-label").first
        self.officers_checkbox = page.locator(".col-md-12 > .form-check > .k-checkbox-label")

        # Billing Address Form Fields
        self.billing_address_line1_input = page.locator("#Billingaddress_1")
        self.billing_city_input = page.locator("#Billingcity_name")
        self.billing_state_dropdown_trigger = page.locator("#divforbilling").get_by_text("--Select--")
        self.billing_state_option_alaska = page.get_by_role("option", name="Alaska")
        self.billing_zip_code_input = page.locator("#Billingzip_code")

        # Point of Contact (POC) Form Fields
        self.poc_first_name_input = page.locator("#poc_fname")
        self.poc_last_name_input = page.locator("#poc_lname")
        self.poc_email_input = page.locator("#poc_email")
        self.poc_email_confirm_input = page.locator("#poc_email_confirm")
        self.company_phone_input = page.locator("#com_phone")

        # Navigation Buttons
        self.back_button = page.get_by_role("button", name=re.compile(r"Back", re.IGNORECASE))

    def verify_company_registration_loaded(self) -> None:
        """Asserts visibility of key registration headings and sections."""
        self.logger.info("Verifying Company Registration page headings")
        expect(self.registration_title).to_be_visible()
        expect(self.company_details_title).to_be_visible()

    def fill_company_details(self, data: Dict[str, Any]) -> None:
        """Fills mandatory Company Details and Physical Address fields."""
        self.logger.info("Filling Company Details and Physical Address")
        if data.get("company_name"):
            self.safe_fill(self.company_name_input, data["company_name"])
        if data.get("address_1"):
            self.safe_fill(self.address_line1_input, data["address_1"])
        if data.get("city"):
            self.safe_fill(self.city_input, data["city"])

        # Select State Dropdown (use first available option or specified state)
        if self.state_dropdown_trigger.is_visible():
            self.state_dropdown_trigger.click()
            if self.first_dropdown_option.is_visible():
                self.first_dropdown_option.click()

        if data.get("zip_code"):
            self.safe_fill(self.zip_code_input, data["zip_code"])
        if data.get("phone"):
            self.safe_fill(self.phone_input, data["phone"])
        if data.get("email"):
            self.safe_fill(self.email_input, data["email"])

    def toggle_same_as_physical_checkbox(self) -> None:
        """Clicks the 'Same as Physical Address' checkbox."""
        self.logger.info("Toggling Same as Physical Address checkbox")
        if self.same_as_physical_checkbox.is_visible():
            self.same_as_physical_checkbox.click()

    def fill_billing_details(self, data: Dict[str, Any]) -> None:
        """Fills Billing Address fields."""
        self.logger.info("Filling Billing Address fields")
        if data.get("billing_address_1") and self.billing_address_line1_input.is_visible():
            self.safe_fill(self.billing_address_line1_input, data["billing_address_1"])
        if data.get("billing_city") and self.billing_city_input.is_visible():
            self.safe_fill(self.billing_city_input, data["billing_city"])

        if self.billing_state_dropdown_trigger.is_visible():
            self.billing_state_dropdown_trigger.click()
            if self.first_dropdown_option.is_visible():
                self.first_dropdown_option.click()

        if data.get("billing_zip_code") and self.billing_zip_code_input.is_visible():
            self.safe_fill(self.billing_zip_code_input, data["billing_zip_code"])

    def fill_poc_details(self, data: Dict[str, Any]) -> None:
        """Fills Point of Contact (POC) details."""
        self.logger.info("Filling Point of Contact details")
        if data.get("poc_fname") and self.poc_first_name_input.is_visible():
            self.safe_fill(self.poc_first_name_input, data["poc_fname"])
        if data.get("poc_lname") and self.poc_last_name_input.is_visible():
            self.safe_fill(self.poc_last_name_input, data["poc_lname"])
        if data.get("poc_email") and self.poc_email_input.is_visible():
            self.safe_fill(self.poc_email_input, data["poc_email"])
        if data.get("poc_email") and self.poc_email_confirm_input.is_visible():
            self.safe_fill(self.poc_email_confirm_input, data["poc_email"])
        if data.get("com_phone") and self.company_phone_input.is_visible():
            self.safe_fill(self.company_phone_input, data["com_phone"])

    def fill_full_registration_form(self, data: Dict[str, Any]) -> None:
        """Fills complete Company Registration form sections."""
        self.fill_company_details(data)
        self.toggle_same_as_physical_checkbox()
        self.fill_billing_details(data)
        self.fill_poc_details(data)

    def click_back_button(self) -> None:
        """Clicks the Back button to return to the Login page."""
        self.logger.info("Clicking Back button on Company Registration page")
        self.safe_click(self.back_button)
