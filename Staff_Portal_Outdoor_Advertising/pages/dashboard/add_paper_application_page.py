import re
import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class AddPaperApplicationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Modal Triggers
        self.kendo_ok_button = page.get_by_role("button", name="OK")
        self.add_paper_app_btn = page.get_by_role("button", name="Add Paper Application")
        self.application_heading = page.get_by_role("heading", name="Application")
        
        # Dealer Selection Locators
        self.select_dealer_btn = page.get_by_role("button", name="Select Dealer")
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name", exact=True)
        self.dealer_search_btn = page.get_by_role("button", name=" Search")
        self.customer_grid = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.dealer_checkbox = page.locator("#selectedChk")
        
        # Form Locators
        self.license_required_dropdown = page.locator("#divAppDetailsForm").get_by_text("--Is License Required?--")
        
        self.application_fee_input = page.get_by_label("Application Fee *")
        
        self.county_dropdown = page.locator("#divAppDetailsForm").get_by_text("---Select County---")
        
        self.location_input = page.get_by_label("Location of Sign")
        self.comments_input = page.get_by_label("Additional Comments")
        
        self.height_input = page.locator("#ODA_Outdoor_Face_Detail_Face_Height1")
        self.width_input = page.locator("#ODA_Outdoor_Face_Detail_Face_Width1")
        
        self.sign_type_dropdown = page.locator("#divAppDetailsForm").get_by_text("--Select Sign Type--")
        
        self.material_dropdown = page.locator("#divAppDetailsForm").get_by_text("--Select Material--")
        
        self.owner_info_heading = page.get_by_text("Property Owner Information")
        self.owner_name_input = page.get_by_label("Property Owner's Name")
        self.street_address_input = page.get_by_label("Street Address", exact=True)
        self.city_input = page.get_by_label("City")
        self.other_input = page.get_by_label("Other")
        
        self.completeness_radio = page.locator(".col-md-12 > div:nth-child(2) > .k-radio-label").first
        self.completeness_heading = page.get_by_text("Completeness Check Review")
        
        self.save_button = page.get_by_text("Save", exact=True)
        self.cancel_button = page.get_by_role("button", name=" Cancel")
        self.partial_form = page.locator("#partial-form").first
        self.application_number_input = page.get_by_role("textbox", name=re.compile(r"Application Number|Application.Permit #|Tracking", re.IGNORECASE)).first

    def _safe_click(self, locator, timeout=5000) -> None:
        """Helper to ensure robust clicking with fallback"""
        try:
            locator.click(timeout=timeout)
        except Exception:
            logger.warning(f"Native click failed, falling back to JS click")
            try:
                locator.evaluate("el => el.click()")
            except Exception as e:
                logger.error(f"JS click also failed: {e}")
                raise

    def _select_first_dropdown_option(self) -> None:
        """
        Professionally clicks the first valid option in an open Kendo dropdown.
        It bypasses the 0th index if it's a '--Select--' placeholder.
        """
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option']")
        # Use a short explicit wait to let Kendo fully render options
        self.page.wait_for_timeout(300)
        
        if options.count() > 1:
            options.nth(1).click() # 1st actual data option (0 is usually placeholder)
        else:
            options.nth(0).click()

    def open_paper_application_form(self) -> None:
        logger.info("Opening Add Paper Application form")
        
        # 1. Wait for page load and any redirections to settle under slow/parallel execution
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        
        # 2. Quick check if we are already on the application page
        if "4319PermitPaperAppNew" in self.page.url:
            logger.info("Landed directly on the Add Paper Application page due to stateful redirect.")
            expect(self.application_heading).to_be_visible(timeout=15000)
            return
            
        # 3. Wait up to 20 seconds for any ongoing auto-redirection to complete
        try:
            self.page.wait_for_url("**/4319PermitPaperAppNew", timeout=20000)
            logger.info("Redirected to the Add Paper Application page during wait.")
            expect(self.application_heading).to_be_visible(timeout=15000)
            return
        except Exception:
            pass

        # 4. If no redirection, click the button using a longer timeout to allow navigation to finish
        try:
            self.add_paper_app_btn.click(timeout=30000)
        except Exception:
            if "4319PermitPaperAppNew" in self.page.url:
                logger.info("Navigation completed despite native click timeout/error.")
            else:
                logger.warning("Native click failed or timed out, attempting JS click fallback.")
                self.add_paper_app_btn.evaluate("el => el.click()")
                
        expect(self.application_heading).to_be_visible(timeout=15000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(2000)

    def select_dealer(self, dealer_name: str) -> None:
        logger.info(f"Selecting dealer: {dealer_name}")
        self._safe_click(self.select_dealer_btn)
        
        # Wait for the select dealer modal and its default initial search to load/settle
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)
        
        self._safe_click(self.dealer_name_input)
        self.dealer_name_input.fill(dealer_name)
        
        self._safe_click(self.dealer_search_btn)
        
        # Wait for the search results request to finish loading
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)
        
        # Wait specifically for the checkbox to be visible before clicking
        self.dealer_checkbox.wait_for(state="visible", timeout=15000)
        
        # Checking the dealer triggers a Kendo UI confirm dialog
        self._safe_click(self.dealer_checkbox)
        
        # Wait for the Kendo OK button to be visible and click it
        self.kendo_ok_button.wait_for(state="visible", timeout=5000)
        self._safe_click(self.kendo_ok_button)

    def fill_application_details(self) -> None:
        logger.info("Filling main application details with Faker data")
        
        # License
        self._safe_click(self.license_required_dropdown)
        self._select_first_dropdown_option()
        
        # Fee
        self._safe_click(self.application_fee_input)
        fee = str(self.fake.random_int(min=100, max=999))
        self.application_fee_input.fill(fee)
        
        # County
        self._safe_click(self.county_dropdown)
        self._select_first_dropdown_option()
        
        # Sign Location & Comments
        self._safe_click(self.location_input)
        self.location_input.fill(self.fake.street_address())
        
        self._safe_click(self.comments_input)
        self.comments_input.fill(self.fake.sentence())
        
        # Dimensions - Pressing 'Enter' triggers the area calculation!
        self._safe_click(self.height_input)
        self.height_input.fill(str(self.fake.random_int(min=10, max=100)))
        self.height_input.press("Enter")
        
        self._safe_click(self.width_input)
        self.width_input.fill(str(self.fake.random_int(min=10, max=100)))
        self.width_input.press("Enter")
        
        # Type & Material
        self._safe_click(self.sign_type_dropdown)
        self._select_first_dropdown_option()
        
        self._safe_click(self.material_dropdown)
        self._select_first_dropdown_option()
        
        expect(self.owner_info_heading).to_be_visible(timeout=5000)

    def fill_property_owner_details(self) -> None:
        logger.info("Filling Property Owner details with Faker data")
        self._safe_click(self.owner_name_input)
        self.owner_name_input.fill(self.fake.name())
        
        self._safe_click(self.street_address_input)
        self.street_address_input.fill(self.fake.street_address())
        
        self._safe_click(self.city_input)
        self.city_input.fill(self.fake.city())
        
        self._safe_click(self.other_input)
        self.other_input.fill(self.fake.word())
        
        self._safe_click(self.completeness_radio)
        expect(self.completeness_heading).to_be_visible(timeout=5000)

    def save_application(self) -> None:
        logger.info("Saving the paper application")
        self._safe_click(self.save_button)
        
        # Accept the Kendo confirmation dialog if it appears
        # If the page immediately navigates away (e.g. to the Tracking_No page), this is bypassed safely.
        try:
            self.kendo_ok_button.click(timeout=2000)
        except Exception:
            pass
        
        # Wait for the modal partial form to appear indicating successful save
        expect(self.partial_form).to_be_visible(timeout=15000)

    def cancel_form(self) -> None:
        logger.info("Canceling / closing the form modal")
        self._safe_click(self.cancel_button)
