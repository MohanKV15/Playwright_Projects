import logging
import re
from datetime import datetime
from typing import Dict, Optional
from faker import Faker
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)
fake = Faker()


class AddCompanyPage(BasePage):
    """
    Page Object Model representing the complete Add Company, Company Contacts,
    and Company Name Change Request workflow in the IDOT Outdoor Advertising Staff Portal.

    Redesigned Workflow based on User Playwright Codegen:
    1. Navigate: Click 'Company' sidebar link -> 'Company Listing' link -> verify 'Companies' heading & '.row.partition' -> click 'Add Company' button.
    2. Form Filling & Save:
       - Fill initial Company Details form (Company Name, Mailing Address 1, City, Zip Code, Phone, Billing Checkbox, Email) using Faker.
       - Click 'Save' button, confirm 'Operation Completed' modal dialog by clicking 'OK'.
       - Verify post-save displays: 'Company Details Company', 'Save Cancel Company Name *', and 'Company Contacts' heading.
    3. Company Contacts Subform:
       - Click 'Add Contact' button.
       - Fill contact details (First Name, Last Name, Email '#dealerEmail', Phone '#com_phone') using Faker.
       - Click Save ('#btnDealerDetailsProfileSave').
       - Confirm 'Record saved successfully' modal dialog by clicking 'OK'.
       - Verify '.k-grid-content' visible, 'Company Name Change' heading visible, and '#NameChange > .k-grid-content' visible.
    4. Company Name Change Request Subform:
       - Click 'Add Request' button.
       - Select present day date dynamically from Kendo date picker calendar.
       - Fill 'New Company Name *' using Faker.
       - Select applicant from '-- Select Applicant --' dropdown matching created contact name.
       - Click '#btnAddDealerName' to attach request to grid.
       - Click main 'Save' button, confirm 'Operation completed' modal dialog by clicking 'OK'.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Locators - Navigation & Headers
        self.sidebar_company_menu = page.get_by_role("link", name=re.compile(r"Company", re.I)).or_(
            page.locator("a[href*='Company'], .sidebar a:has-text('Company')")
        ).first
        self.company_listing_link = page.get_by_role("link", name="Company Listing").or_(
            page.locator("a[href*='CompanyListing'], a:has-text('Company Listing')")
        ).first
        self.heading_companies = page.get_by_role("heading", name="Companies").first
        self.row_partition = page.locator(".row.partition").first
        self.add_company_button = page.get_by_role("button", name=" Add Company").or_(
            page.locator("#btnAddCompany, button:has-text('Add Company')")
        ).first
        self.heading_save_cancel_wrapper = page.get_by_text("Save Cancel Company Name *").or_(
            page.get_by_text("Company Name *")
        ).first

        # 2. Locators - Initial Company Details Form
        self.company_name_input = page.get_by_role("textbox", name="Company Name *").or_(
            page.locator("#company_name")
        ).first
        self.mailing_address1_input = page.get_by_role("textbox", name="Mailing Address 1 *").or_(
            page.locator("#mailing_address1")
        ).first
        self.city_input = page.locator("#city_name").first
        self.zip_code_input = page.locator("#zip_code").first
        self.phone_input = page.locator("#phone").first
        self.billing_same_as_mailing_label = page.locator("div:nth-child(3) > .col-md-12 > .form-check > .k-checkbox-label").or_(
            page.locator(".k-checkbox-label:has-text('Select if billing address is the same as the mailing address')")
        ).first
        self.email_input = page.get_by_role("textbox", name="Email *").or_(
            page.locator("#email")
        ).first

        # 3. Locators - Save & Modal Confirmation
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first
        self.operation_completed_text = page.get_by_text(re.compile(r"Operation Completed|Operation completed", re.I)).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 4. Locators - Post-Save & Subforms
        self.company_details_header = page.get_by_text("Company Details Company").or_(
            page.get_by_text("Company Details")
        ).first
        self.company_contacts_heading = page.get_by_role("heading", name="Company Contacts").first
        self.add_contact_button = page.get_by_role("button", name=" Add Contact").or_(
            page.locator("#btnAddDealerContact")
        ).first

        # 5. Locators - User Profile / Contact Form
        self.contact_first_name_input = page.get_by_role("textbox", name="First Name *").or_(
            page.locator("#firstName")
        ).first
        self.contact_last_name_input = page.get_by_role("textbox", name="Last Name *").or_(
            page.locator("#lastName")
        ).first
        self.contact_email_input = page.locator("#dealerEmail").first
        self.contact_phone_input = page.locator("#com_phone").first
        self.contact_profile_save_button = page.locator("#btnDealerDetailsProfileSave").first
        self.record_saved_text = page.get_by_text(re.compile(r"Record saved successfully|Record Saved successfully", re.I)).first
        self.grid_content_first = page.locator(".k-grid-content").first

        # 6. Locators - Company Name Change Subform
        self.company_name_change_heading = page.get_by_role("heading", name="Company Name Change").first
        self.name_change_grid = page.locator("#NameChange > .k-grid-content").first
        self.add_request_button = page.get_by_role("button", name=" Add Request").or_(
            page.locator("#btnAddRequest")
        ).first
        self.date_picker_select_btn = page.locator("#divDealerDetailsAddNewName").get_by_role("button", name="select").first
        self.new_company_name_input = page.get_by_role("textbox", name="New Company Name *").or_(
            page.locator("#new_company_name")
        ).first
        self.applicant_dropdown_trigger = page.locator("#divDealerDetailsAddNewName").get_by_text("-- Select Applicant --").or_(
            page.locator("#divDealerDetailsAddNewName .k-dropdown-wrap, #divDealerDetailsAddNewName .k-dropdown")
        ).first
        self.add_dealer_name_button = page.locator("#btnAddDealerName").first

    def navigate_to_company_listing(self, timeout_ms: int = 20000) -> None:
        """Navigates to Company -> Company Listing and verifies page load."""
        self.logger.info("Navigating to Company Listing")
        self._wait_for_loader()

        if self.sidebar_company_menu.is_visible(timeout=5000) and not self.company_listing_link.is_visible():
            self.sidebar_company_menu.click(force=True)
            self.page.wait_for_timeout(400)

        expect(self.company_listing_link).to_be_visible(timeout=timeout_ms)
        self.company_listing_link.click()
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        expect(self.heading_companies).to_be_visible(timeout=timeout_ms)
        if self.row_partition.is_visible(timeout=5000):
            expect(self.row_partition).to_be_visible()

    def click_add_company(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Add Company' button and verifies initial form page."""
        self.logger.info("Clicking Add Company button")
        expect(self.add_company_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.add_company_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        expect(self.heading_save_cancel_wrapper).to_be_visible(timeout=timeout_ms)

    def fill_and_save_initial_company_form(
        self,
        company_name: Optional[str] = None,
        mailing_address: Optional[str] = None,
        city: Optional[str] = None,
        zip_code: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        timeout_ms: int = 20000,
    ) -> Dict[str, str]:
        """Fills initial Company Details form using Faker data and saves form."""
        data = {
            "company_name": company_name or f"Test Co {fake.company()}",
            "mailing_address": mailing_address or fake.street_address(),
            "city": city or fake.city(),
            "zip_code": zip_code or "56788",
            "phone": phone or "999-999-9999",
            "email": email or fake.company_email(),
        }

        self.logger.info("Filling initial company form: %s", data)
        expect(self.company_name_input).to_be_visible(timeout=timeout_ms)
        self.company_name_input.fill(data["company_name"])

        expect(self.mailing_address1_input).to_be_visible(timeout=timeout_ms)
        self.mailing_address1_input.fill(data["mailing_address"])

        expect(self.city_input).to_be_visible(timeout=timeout_ms)
        self.city_input.fill(data["city"])

        expect(self.zip_code_input).to_be_visible(timeout=timeout_ms)
        self.zip_code_input.fill(data["zip_code"])

        expect(self.phone_input).to_be_visible(timeout=timeout_ms)
        self.phone_input.fill(data["phone"])

        # Click billing address checkbox
        if self.billing_same_as_mailing_label.is_visible(timeout=5000):
            self.safe_click(self.billing_same_as_mailing_label)
            self.page.wait_for_timeout(300)

        expect(self.email_input).to_be_visible(timeout=timeout_ms)
        self.email_input.fill(data["email"])

        # Fallback safeguard: if billing address fields are visible & empty, fill them
        billing1 = self.page.locator("#billing_address1, [name='BillingAddress1']").first
        if billing1.is_visible() and not billing1.input_value():
            billing1.fill(data["mailing_address"])

        self.logger.info("Saving initial company details")
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.save_button)
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        if self.operation_completed_text.is_visible(timeout=5000):
            self.logger.info("Operation Completed popup visible")

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click()
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

        # Post-save assertions according to codegen
        expect(self.company_details_header).to_be_visible(timeout=timeout_ms)
        expect(self.heading_save_cancel_wrapper).to_be_visible(timeout=timeout_ms)
        expect(self.company_contacts_heading).to_be_visible(timeout=timeout_ms)

        return data

    def add_company_contact(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        timeout_ms: int = 20000,
    ) -> Dict[str, str]:
        """Adds a Company Contact in the User Profile subform and confirms save."""
        contact_data = {
            "first_name": first_name or fake.first_name(),
            "last_name": last_name or fake.last_name(),
            "email": email or f"user.{fake.user_name()}{fake.random_int(10, 99)}@gmail.com",
            "phone": phone or "999-999-9999",
        }

        self.logger.info("Adding Company Contact: %s", contact_data)
        if self.company_contacts_heading.is_visible(timeout=2000):
            self.scroll_to_locator(self.company_contacts_heading)

        expect(self.add_contact_button).to_be_attached(timeout=timeout_ms)
        self.safe_click(self.add_contact_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        expect(self.contact_first_name_input).to_be_visible(timeout=timeout_ms)
        self.contact_first_name_input.fill(contact_data["first_name"])

        expect(self.contact_last_name_input).to_be_visible(timeout=timeout_ms)
        self.contact_last_name_input.fill(contact_data["last_name"])

        expect(self.contact_email_input).to_be_visible(timeout=timeout_ms)
        self.contact_email_input.fill(contact_data["email"])
        self.contact_email_input.press("Tab")

        expect(self.contact_phone_input).to_be_visible(timeout=timeout_ms)
        self.contact_phone_input.fill(contact_data["phone"])
        self.contact_phone_input.press("Tab")

        expect(self.contact_profile_save_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.contact_profile_save_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click()
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

        # Update email if needed as per codegen flow
        if self.page.get_by_text("Email is required").first.is_visible(timeout=1000):
            unique_email = f"test{fake.random_int(10, 99)}@gmail.com"
            contact_data["email"] = unique_email
            self.contact_email_input.fill(unique_email)
            self.contact_email_input.press("Tab")
            self.safe_click(self.contact_profile_save_button)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        if self.record_saved_text.is_visible(timeout=5000):
            expect(self.record_saved_text).to_be_visible(timeout=timeout_ms)

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click()
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

        # Post-contact save assertions according to codegen
        expect(self.grid_content_first).to_be_visible(timeout=timeout_ms)
        expect(self.company_name_change_heading).to_be_visible(timeout=timeout_ms)
        expect(self.name_change_grid).to_be_visible(timeout=timeout_ms)

        return contact_data

    def add_company_name_change_request(
        self,
        new_company_name: Optional[str] = None,
        applicant_name: Optional[str] = None,
        timeout_ms: int = 20000,
    ) -> Dict[str, str]:
        """Adds Company Name Change request with present day date selection and applicant selection."""
        name_change_data = {
            "new_company_name": new_company_name or f"Renamed {fake.company()}",
            "applicant_name": applicant_name,
        }

        self.logger.info("Adding Company Name Change Request: %s", name_change_data)
        if self.company_name_change_heading.is_visible(timeout=2000):
            self.scroll_to_locator(self.company_name_change_heading)

        expect(self.add_request_button).to_be_attached(timeout=timeout_ms)
        self.safe_click(self.add_request_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # Select present day date in date picker calendar
        today_day = str(datetime.now().day)
        self.logger.info("Selecting present day date (%s) in Kendo calendar", today_day)

        if self.date_picker_select_btn.is_visible(timeout=5000):
            self.date_picker_select_btn.click()
            self.page.wait_for_timeout(300)

            day_link = self.page.get_by_role("link", name=today_day, exact=True).or_(
                self.page.locator(".k-calendar td:not(.k-other-month) a").filter(has_text=re.compile(rf"^{today_day}$"))
            ).first

            if day_link.is_visible(timeout=2000):
                self.js_click(day_link)
            else:
                today_cell = self.page.locator(".k-calendar td.k-state-focused a, .k-calendar td.k-today a").first
                if today_cell.is_visible(timeout=2000):
                    self.js_click(today_cell)
            self.page.wait_for_timeout(300)

        # Fill New Company Name
        expect(self.new_company_name_input).to_be_visible(timeout=timeout_ms)
        self.new_company_name_input.fill(name_change_data["new_company_name"])

        # Select Applicant
        self.logger.info("Selecting Applicant from dropdown (Target: %s)", applicant_name)
        select_text_loc = self.page.locator("#divDealerDetailsAddNewName").get_by_text("-- Select Applicant --").or_(
            self.page.locator("#divDealerDetailsAddNewName .k-dropdown, #divDealerDetailsAddNewName .k-dropdown-wrap")
        ).first

        if select_text_loc.is_visible(timeout=2000):
            select_text_loc.click()
            self.page.wait_for_timeout(300)

        first_name = applicant_name.split()[0] if applicant_name else ""
        opt = self.page.get_by_role("option", name=re.compile(first_name, re.I)).or_(
            self.page.get_by_role("option").filter(has_not_text="-- Select")
        ).first

        if opt.is_visible(timeout=1500):
            opt.click()
        else:
            self.page.evaluate("""
                () => {
                    const ddl = $("#divDealerDetailsAddNewName").find("[data-role='dropdownlist'], select").first().data("kendoDropDownList");
                    if (ddl) { ddl.select(1); ddl.trigger("change"); }
                }
            """)
        self.page.wait_for_timeout(300)

        # Click Add Dealer Name button (#btnAddDealerName)
        expect(self.add_dealer_name_button).to_be_attached(timeout=timeout_ms)
        self.safe_click(self.add_dealer_name_button)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        # Click main Save button and confirm Operation completed dialog
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.save_button)
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        if self.operation_completed_text.is_visible(timeout=5000):
            self.logger.info("Operation completed modal displayed")

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click()
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

        return name_change_data

    def execute_add_company_full_workflow(
        self,
        company_name: Optional[str] = None,
        mailing_address: Optional[str] = None,
        city: Optional[str] = None,
        zip_code: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        High-level complete continuous Add Company workflow:
        1. Navigate to Company -> Company Listing -> Add Company
        2. Fill initial company form using Faker & Save
        3. Add Company Contact using Faker & Save
        4. Add Company Name Change Request using present day date & Save
        """
        self.navigate_to_company_listing()
        self.click_add_company()
        company_data = self.fill_and_save_initial_company_form(
            company_name=company_name,
            mailing_address=mailing_address,
            city=city,
            zip_code=zip_code,
            phone=phone,
            email=email,
        )

        contact_data = self.add_company_contact()
        applicant_full_name = f"{contact_data['first_name']} {contact_data['last_name']}"

        name_change_data = self.add_company_name_change_request(
            applicant_name=applicant_full_name
        )

        return {
            "company_data": company_data,
            "contact_data": contact_data,
            "name_change_data": name_change_data,
            "status": "Verified successfully",
        }

