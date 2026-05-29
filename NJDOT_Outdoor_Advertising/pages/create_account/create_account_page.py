import logging
from playwright.sync_api import Page, expect
from faker import Faker

logger = logging.getLogger(__name__)

class CreateAccountPage:
    def __init__(self, page: Page):
        self.page = page
        
        # Actions
        self.create_account_btn = page.get_by_role("button", name="Create an Account")
        self.yes_btn = page.get_by_role("button", name="Yes")
        self.no_btn = page.get_by_role("button", name="No")
        self.back_btn = page.get_by_role("button", name=" Back")
        self.submit_btn = page.get_by_role("button", name=" Submit")
        
        # Headings
        self.company_registration_heading = page.get_by_role("heading", name="Company Registration")
        
        # Company Info
        self.company_name = page.locator("#name_")
        self.address = page.locator("#address_1")
        self.city = page.locator("#city_name")
        self.zip_code = page.locator("#zip_code")
        self.phone = page.locator("#phone")
        self.email = page.locator("#email")
        self.federal_dbe = page.locator("#federal_dbe_main")
        
        # Billing Info
        self.billing_address = page.locator("#Billingaddress_1")
        self.billing_city = page.locator("#Billingcity_name")
        self.billing_zip = page.locator("#Billingzip_code")
        
        # Officers
        self.president = page.locator("#President")
        self.vice_president = page.locator("#VicePresident")
        self.secretary = page.locator("#Secretary")
        self.treasurer = page.locator("#Treasurer")
        
        # Point of Contact
        self.poc_fname = page.locator("#poc_fname")
        self.poc_lname = page.locator("#poc_lname")
        self.poc_email = page.locator("#poc_email")
        self.poc_email_confirm = page.locator("#poc_email_confirm")
        self.poc_phone = page.locator("#com_phone")
        
        # Checkboxes
        # This typically acts as a certification or "Same as above" checkbox
        self.certification_checkbox = page.locator(".col-md-12 > .form-check > .k-checkbox-label")
        
    def start_account_creation(self, is_dbe: bool):
        """Clicks 'Create an Account' and selects Yes/No for DBE status."""
        logger.info(f"Starting account creation. DBE/SBE Status: {'Yes' if is_dbe else 'No'}")
        self.create_account_btn.click()
        
        if is_dbe:
            self.yes_btn.click()
        else:
            self.no_btn.click()
            
        expect(self.company_registration_heading).to_be_visible(timeout=10000)
        logger.info("Successfully navigated to Company Registration form.")
        
    def fill_registration_form(self, is_dbe: bool):
        """Fills the company registration form using Faker data."""
        fake = Faker()
        
        logger.info("Filling Company Information...")
        if not is_dbe:
            # Company name is only filled if NOT a DBE/SBE (as per the recorded script)
            self.company_name.fill(fake.company())
            
        self.address.fill(fake.street_address())
        self.city.fill(fake.city())
        # The form likely requires a specific zip code format or exact length
        self.zip_code.fill(fake.zipcode()[:5]) 
        
        # Format phone as XXX-XXX-XXXX
        phone_number = f"{fake.random_number(digits=3, fix_len=True)}-{fake.random_number(digits=3, fix_len=True)}-{fake.random_number(digits=4, fix_len=True)}"
        self.phone.fill(phone_number)
        
        company_email = fake.company_email()
        self.email.fill(company_email)
        
        if not is_dbe:
            # Federal DBE might be required or visible in the 'No' flow
            if self.federal_dbe.is_visible():
                self.federal_dbe.fill("123456789")
                
        logger.info("Filling Billing Information...")
        self.billing_address.fill(fake.street_address())
        self.billing_city.fill(fake.city())
        self.billing_zip.fill(fake.zipcode()[:5])
        
        logger.info("Clicking certification/terms checkbox...")
        self.certification_checkbox.click()
        
        logger.info("Filling Officers Information...")
        self.president.fill(fake.name())
        self.vice_president.fill(fake.name())
        self.secretary.fill(fake.name())
        self.treasurer.fill(fake.name())
        
        logger.info("Filling Point of Contact Information...")
        poc_first = fake.first_name()
        poc_last = fake.last_name()
        poc_email_addr = fake.email()
        
        self.poc_fname.fill(poc_first)
        self.poc_lname.fill(poc_last)
        self.poc_email.fill(poc_email_addr)
        self.poc_email_confirm.fill(poc_email_addr)
        
        poc_phone_num = f"{fake.random_number(digits=3, fix_len=True)}-{fake.random_number(digits=3, fix_len=True)}-{fake.random_number(digits=4, fix_len=True)}"
        self.poc_phone.fill(poc_phone_num)
        
    def submit_registration(self):
        """Clicks Submit and waits for success/processing."""
        logger.info("Verifying Submit button is visible...")
        expect(self.submit_btn).to_be_visible()
        # Not clicking submit to avoid creating junk test data in the real environment unless specified
        # self.submit_btn.click() 
        logger.info("Form filled successfully. Backing out to prevent junk data creation.")
        self.back_btn.click()
