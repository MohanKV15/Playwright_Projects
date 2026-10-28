import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.testdata import generate_company_registration_data

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
        self.state_dropdown = page.locator("#state_d, #state, select[name*='state']").or_(
            page.locator(".k-dropdown").filter(has_text=re.compile(r"Illinois|State|Select", re.I))
        ).first
        self.zip_code_input = page.locator("#zip_code")
        self.phone_input = page.locator("#phone")
        self.email_input = page.locator("#email")

        # Checkboxes
        self.same_as_physical_checkbox = page.locator(".k-checkbox-label").first
        self.officers_checkbox = page.locator(".col-md-12 > .form-check > .k-checkbox-label")

        # Billing Address Form Fields
        self.billing_address_line1_input = page.locator("#Billingaddress_1")
        self.billing_city_input = page.locator("#Billingcity_name")
        self.billing_state_dropdown = page.locator("#Billingstate_d, #Billingstate, #divforbilling .k-dropdown").first
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

    def fill_company_details(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fills mandatory Company Details and Physical Address fields using Faker data."""
        self.logger.info("Filling Company Details and Physical Address")
        form_data = data or generate_company_registration_data()

        if form_data.get("company_name"):
            self.safe_fill(self.company_name_input, form_data["company_name"])
        if form_data.get("address_1"):
            self.safe_fill(self.address_line1_input, form_data["address_1"])
        if form_data.get("city"):
            self.safe_fill(self.city_input, form_data["city"])

        # Select State Dropdown (always 1st option in the list)
        if self.state_dropdown.is_visible(timeout=1000):
            self.kendo_dropdown.select_first_option(self.state_dropdown)

        if form_data.get("zip_code"):
            self.safe_fill(self.zip_code_input, form_data["zip_code"])
        if form_data.get("phone"):
            self.safe_fill(self.phone_input, form_data["phone"])
        if form_data.get("email"):
            self.safe_fill(self.email_input, form_data["email"])

    def toggle_same_as_physical_checkbox(self) -> None:
        """Clicks the 'Same as Physical Address' checkbox."""
        self.logger.info("Toggling Same as Physical Address checkbox")
        if self.same_as_physical_checkbox.is_visible():
            self.same_as_physical_checkbox.click()

    def fill_billing_details(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fills Billing Address fields using Faker data."""
        self.logger.info("Filling Billing Address fields")
        form_data = data or generate_company_registration_data()

        if form_data.get("billing_address_1") and self.billing_address_line1_input.is_visible():
            self.safe_fill(self.billing_address_line1_input, form_data["billing_address_1"])
        if form_data.get("billing_city") and self.billing_city_input.is_visible():
            self.safe_fill(self.billing_city_input, form_data["billing_city"])

        # Select Billing State Dropdown (always 1st option in the list)
        if self.billing_state_dropdown.is_visible(timeout=1000):
            self.kendo_dropdown.select_first_option(self.billing_state_dropdown)

        if form_data.get("billing_zip_code") and self.billing_zip_code_input.is_visible():
            self.safe_fill(self.billing_zip_code_input, form_data["billing_zip_code"])

    def fill_poc_details(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fills Point of Contact (POC) details using Faker data."""
        self.logger.info("Filling Point of Contact details")
        form_data = data or generate_company_registration_data()

        poc_email = form_data.get("poc_email") or form_data.get("email")

        if form_data.get("poc_fname") and self.poc_first_name_input.is_visible():
            self.safe_fill(self.poc_first_name_input, form_data["poc_fname"])
        if form_data.get("poc_lname") and self.poc_last_name_input.is_visible():
            self.safe_fill(self.poc_last_name_input, form_data["poc_lname"])
        if poc_email and self.poc_email_input.is_visible():
            self.safe_fill(self.poc_email_input, poc_email)
        if poc_email and self.poc_email_confirm_input.is_visible():
            self.safe_fill(self.poc_email_confirm_input, poc_email)
        if form_data.get("com_phone") and self.company_phone_input.is_visible():
            self.safe_fill(self.company_phone_input, form_data["com_phone"])

    def fill_full_registration_form(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fills complete Company Registration form sections using dynamic Faker data."""
        form_data = data or generate_company_registration_data()
        self.fill_company_details(form_data)
        self.toggle_same_as_physical_checkbox()
        self.fill_billing_details(form_data)
        self.fill_poc_details(form_data)

    def click_back_button(self) -> None:
        """Clicks the Back button to return to the Login page."""
        self.logger.info("Clicking Back button on Company Registration page")
        self.safe_click(self.back_button)
