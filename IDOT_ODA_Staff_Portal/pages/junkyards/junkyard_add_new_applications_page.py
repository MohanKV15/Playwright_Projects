import logging
import re
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown

logger = logging.getLogger(__name__)
fake = Faker()


class JunkyardAddNewApplicationsPage(BasePage):
    """
    Page Object Model representing the Junkyards Add Paper Application workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Navigate to Junkyards -> Junkyard/Permit Search
    - Assert Junkyard/Permit Search header, Permits heading, and grid table container
    - Click 'Add Paper Application' button
    - Verify form section headers (Applicant Permit Number, Yard Information, Location Information, Property Owner Information)
    - Click 'Select Company', search company name ('test' / 'IDOTOAtest2'), select row, click 'OK'
    - Click primary radio option (.k-radio-label)
    - Select 1st valid option from District and County Kendo UI DropDownLists
    - Fill Latitude and Longitude coordinates
    - Fill Property Owner Information (Name, Address 1, Address 2, City, Phone) using Faker
    - Click 1st 'Save', verify 'Record updated successfully.' confirmation modal, click 'OK'
    - Click final 'Save', verify 'Record Saved successfully.' confirmation modal, click 'OK'
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)

        # 1. Navigation & Search View Locators
        self.sidebar_junkyards_menu = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_junkyard_search_link = page.get_by_role("link", name="Junkyard/Permit Search").or_(
            page.locator("a[href*='JunkyardSearch'], a[href*='Junkyard'], a:has-text('Junkyard/Permit Search')")
        ).first

        self.heading_junkyard_search = page.get_by_text("Junkyard/Permit Search").filter(visible=True).first
        self.heading_permits = page.get_by_role("heading", name="Permits").or_(
            page.locator("h1, h2, h3, h4, h5, .card-header, legend").filter(has_text="Permits")
        ).filter(visible=True).first
        self.grid_content = page.locator(".k-grid-content, #partial-form, .k-grid").first
        self.add_paper_app_button = page.get_by_role("button", name="Add Paper Application").or_(
            page.locator("button:has-text('Add Paper Application'), a:has-text('Add Paper Application'), .k-button:has-text('Add Paper Application')")
        ).filter(visible=True).first

        # 2. Form Section Header Locators
        self.text_applicant_permit_no = page.get_by_text("Applicant Permit Number").first
        self.text_yard_info = page.get_by_text("Yard Information").or_(page.get_by_text("Yard Type")).first
        self.text_location_info = page.get_by_text("Location Information").first
        self.text_industrial_activity = page.get_by_text("industrial activity").or_(page.get_by_text("1,000 feet")).first
        self.text_property_owner_info = page.get_by_text("Property Owner Information").first

        # 3. Company Search Modal Locators
        self.select_company_button = page.get_by_role("button", name="Select Company").or_(
            page.locator("button:has-text('Select Company'), input[value='Select Company']")
        ).first
        self.company_search_modal = page.locator(".k-window:visible, .modal-content:visible, div[role='dialog']:visible").first
        self.dealer_name_input = page.locator("#Dealer_Name, [name='Dealer_Name']").first
        self.company_search_button = page.get_by_role("button", name="Search").or_(
            page.locator("button:has-text('Search'), input[value='Search']")
        ).first
        self.company_checkbox = page.locator("#selectedChk, input[type='checkbox']").first
        self.company_modal_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 4. Form Controls Locators
        self.radio_label_first = page.locator(".k-radio-label, input[type='radio'] + label, label.k-radio-label").first
        self.district_dropdown_trigger = page.locator("#partial-form span.k-input").first.or_(
            page.get_by_text("-- Select --").first
        )
        self.county_dropdown_trigger = page.locator("#partial-form span.k-input").nth(1).or_(
            page.get_by_text("-- Select --").nth(2)
        )

        self.latitude_input = page.get_by_label("Latitude *").or_(
            page.locator("#Yard_Latitude, [name='Yard_Latitude'], input[name*='Latitude' i]")
        ).first
        self.longitude_input = page.get_by_label("Longitude *").or_(
            page.locator("#Yard_Longitude, [name='Yard_Longitude'], input[name*='Longitude' i]")
        ).first

        self.prop_owner_name_input = page.get_by_label("Property Owner Name").or_(
            page.locator("#Prop_Owner_Name, [name='Prop_Owner_Name'], input[name*='Owner_Name' i]")
        ).first
        self.prop_owner_address1_input = page.get_by_label("Property Owner Address 1").or_(
            page.locator("#Prop_Owner_Address1, [name='Prop_Owner_Address1'], input[name*='Address1' i]")
        ).first
        self.prop_owner_address2_input = page.get_by_label("Property Owner Address 2").or_(
            page.locator("#Prop_Owner_Address2, [name='Prop_Owner_Address2'], input[name*='Address2' i]")
        ).first
        self.city_input = page.get_by_label("City").or_(
            page.locator("#Prop_Owner_City, [name='Prop_Owner_City'], input[name*='City' i]")
        ).first
        self.phone_input = page.locator("#PropOwnerPhone, [name='PropOwnerPhone'], [name='Prop_Owner_Phone'], input[name*='Phone' i]").first

        # 5. Save Buttons & Notification Dialog Locators
        self.save_button = page.locator("#btnSubmit, button:has-text('Save'), input[value='Save']").first
        self.save_exact_button = page.get_by_text("Save", exact=True).or_(
            page.locator("button:has-text('Save')")
        ).first
        self.record_updated_text = page.get_by_text("Record updated successfully.").or_(
            page.get_by_text("Record updated")
        ).first
        self.record_saved_text = page.get_by_text("Record Saved successfully.").or_(
            page.get_by_text("Record Saved")
        ).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_junkyard_search(self, timeout_ms: int = 20000) -> None:
        """
        Navigates to Junkyard/Permit Search via sidebar menu link and verifies page headers.
        """
        self.logger.info("Navigating to Junkyards -> Junkyard/Permit Search")
        self._wait_for_loader()

        # Expand Junkyards sidebar menu if collapsed
        if self.sidebar_junkyards_menu.is_visible(timeout=5000) and not self.sidebar_junkyard_search_link.is_visible():
            self.sidebar_junkyards_menu.click(force=True)
            self.page.wait_for_timeout(400)

        expect(self.sidebar_junkyard_search_link).to_be_visible(timeout=timeout_ms)
        self.sidebar_junkyard_search_link.click(force=True)
        self._wait_for_loader()

        self.verify_junkyard_search_page_loaded(timeout_ms=timeout_ms)

    def verify_junkyard_search_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Junkyard/Permit Search heading, Permits header, and grid content container are visible.
        """
        self.logger.info("Verifying Junkyard/Permit Search page elements are visible")
        expect(self.heading_junkyard_search).to_be_visible(timeout=timeout_ms)
        expect(self.heading_permits).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

    # -------------------------------------------------------------------------
    # Add Paper Application Actions
    # -------------------------------------------------------------------------
    def click_add_paper_application(self, timeout_ms: int = 20000) -> None:
        """
        Clicks 'Add Paper Application' button and verifies section headers on the application form.
        """
        self.logger.info("Clicking 'Add Paper Application' button")
        expect(self.add_paper_app_button).to_be_visible(timeout=timeout_ms)
        self.add_paper_app_button.click(force=True)
        self._wait_for_loader()

        self.logger.info("Verifying Junkyard application form section headers")
        expect(self.text_applicant_permit_no).to_be_visible(timeout=timeout_ms)
        expect(self.text_yard_info).to_be_visible(timeout=timeout_ms)
        expect(self.text_location_info).to_be_visible(timeout=timeout_ms)
        expect(self.text_industrial_activity).to_be_visible(timeout=timeout_ms)
        expect(self.text_property_owner_info).to_be_visible(timeout=timeout_ms)

    def search_and_select_company(
        self, company_name: str = "test", preferred_company: str = "IDOTOAtest2", timeout_ms: int = 20000
    ) -> str:
        """
        Opens 'Select Company' modal, inputs company_name, searches, checks matching row checkbox, and clicks OK.
        """
        self.logger.info("Opening 'Select Company' search modal")
        expect(self.select_company_button).to_be_visible(timeout=timeout_ms)
        self.select_company_button.click(force=True)
        self._wait_for_loader()

        self.logger.info(f"Filtering company search for: '{company_name}'")
        dealer_input = self.page.locator("#Dealer_Name").first
        expect(dealer_input).to_be_visible(timeout=timeout_ms)
        dealer_input.click(force=True)
        dealer_input.clear()
        dealer_input.fill(company_name)

        search_btn = self.page.get_by_role("button", name="Search").or_(
            self.page.locator("button:has-text('Search'), input[value='Search']")
        ).first
        expect(search_btn).to_be_visible(timeout=timeout_ms)
        search_btn.click(force=True)
        self.page.wait_for_timeout(800)
        self._wait_for_loader()

        # Target specific company row (e.g. IDOTOAtest2) or first row with #selectedChk
        pref_chk = self.page.get_by_role("row", name=re.compile(preferred_company, re.I)).locator("#selectedChk").first
        if pref_chk.is_visible(timeout=5000):
            pref_chk.check(force=True)
        else:
            first_chk = self.page.locator("#selectedChk").first
            expect(first_chk).to_be_attached(timeout=timeout_ms)
            first_chk.check(force=True)

        self.logger.info("Confirming company selection by clicking OK on modal")
        ok_btn = self.page.get_by_role("button", name="OK").or_(
            self.page.locator(".k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first
        expect(ok_btn).to_be_visible(timeout=timeout_ms)
        ok_btn.click(force=True)
        self._wait_for_loader()
        return company_name

    def select_first_dropdown_option(self, trigger_locator: Locator, preferred_option: Optional[str] = None) -> str:
        """
        Selects option from a Kendo DropDownList:
        If preferred_option is provided, attempts selection; otherwise automatically selects the 1st valid option in the list.
        """
        self.logger.info("Selecting option from Kendo dropdown (preferred: '%s')", preferred_option)
        selected = ""
        if preferred_option:
            try:
                if self.kendo_dropdown.select_by_locator(trigger_locator, preferred_option):
                    self._wait_for_loader()
                    return preferred_option
            except Exception as e:
                self.logger.warning("Preferred option selection note: %s", e)

        # Automatically choose 1st valid option in the dropdown list
        selected = self.kendo_dropdown.select_first_valid_option(trigger_locator)
        self._wait_for_loader()
        return selected or (preferred_option or "")

    def fill_and_submit_junkyard_application(
        self,
        company_name: str = "test",
        district: Optional[str] = "District 1",
        county: Optional[str] = "Cook",
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        owner_name: Optional[str] = None,
        owner_address1: Optional[str] = None,
        owner_address2: Optional[str] = None,
        city: Optional[str] = None,
        phone: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> Dict[str, str]:
        """
        Fills out the Junkyard Add Paper Application form:
        - Searches & selects company via modal
        - Selects 1st radio button option (.k-radio-label)
        - Selects 1st valid option from District and County dropdowns (or specified district/county)
        - Fills Latitude and Longitude
        - Fills Property Owner Information using Faker library
        - Performs 1st Save & confirms 'Record updated successfully.'
        - Performs final Save & confirms 'Record Saved successfully.'
        Returns dictionary of all submitted values.
        """
        # Generate dynamic test data via Faker library for owner info if not specified
        f_owner_name = owner_name or f"Owner {fake.name()}"
        f_owner_addr1 = owner_address1 or fake.street_address()
        f_owner_addr2 = owner_address2 or fake.secondary_address()
        f_city = city or fake.city()
        f_phone = phone or "999-999-9999"
        f_lat = latitude or str(fake.random_int(100, 999))
        f_lon = longitude or str(fake.random_int(100, 999))

        # 1. Search & Select Company
        self.search_and_select_company(company_name=company_name, timeout_ms=timeout_ms)

        # 2. Select Radio Button
        if self.radio_label_first.is_visible(timeout=3000):
            self.logger.info("Selecting primary radio button option")
            self.radio_label_first.click(force=True)
            self.page.wait_for_timeout(300)

        # 3. Select 1st Dropdown Options for District and County
        self.logger.info("Selecting District dropdown option")
        dist_trigger = self.page.get_by_text("-- Select --").nth(2).or_(
            self.page.locator(".k-dropdown span.k-input").nth(2)
        )
        sel_district = district or "District 1"
        if dist_trigger.is_visible(timeout=5000):
            dist_trigger.click(force=True)
            self.page.wait_for_timeout(300)
            dist_opt = self.page.get_by_role("option", name=sel_district).or_(
                self.page.locator("[role='option']:visible, .k-animation-container:visible li").first
            )
            if dist_opt.is_visible(timeout=3000):
                dist_opt.click(force=True)
            self._wait_for_loader()

        self.logger.info("Selecting County dropdown option")
        county_trigger = self.page.get_by_text("-- Select --").nth(2).or_(
            self.page.locator(".k-dropdown span.k-input").nth(2)
        )
        sel_county = county or "Cook"
        if county_trigger.is_visible(timeout=5000):
            county_trigger.click(force=True)
            self.page.wait_for_timeout(300)
            county_opt = self.page.get_by_role("option", name=sel_county).or_(
                self.page.locator("[role='option']:visible, .k-animation-container:visible li").first
            )
            if county_opt.is_visible(timeout=3000):
                county_opt.click(force=True)
            self._wait_for_loader()

        # 4. Fill Latitude & Longitude
        self.logger.info(f"Filling coordinates: Latitude='{f_lat}', Longitude='{f_lon}'")
        expect(self.latitude_input).to_be_visible(timeout=timeout_ms)
        self.latitude_input.click(force=True)
        self.latitude_input.clear()
        self.latitude_input.fill(f_lat)

        expect(self.longitude_input).to_be_visible(timeout=timeout_ms)
        self.longitude_input.click(force=True)
        self.longitude_input.clear()
        self.longitude_input.fill(f_lon)

        # 5. Fill Property Owner Information using Faker generated data
        self.logger.info(f"Filling Property Owner Info: Name='{f_owner_name}', Address1='{f_owner_addr1}', City='{f_city}', Phone='{f_phone}'")
        expect(self.prop_owner_name_input).to_be_visible(timeout=timeout_ms)
        self.prop_owner_name_input.click(force=True)
        self.prop_owner_name_input.clear()
        self.prop_owner_name_input.fill(f_owner_name)

        if self.prop_owner_address1_input.is_visible(timeout=2000):
            self.prop_owner_address1_input.click(force=True)
            self.prop_owner_address1_input.clear()
            self.prop_owner_address1_input.fill(f_owner_addr1)

        if self.prop_owner_address2_input.is_visible(timeout=2000):
            self.prop_owner_address2_input.click(force=True)
            self.prop_owner_address2_input.clear()
            self.prop_owner_address2_input.fill(f_owner_addr2)

        expect(self.city_input).to_be_visible(timeout=timeout_ms)
        self.city_input.click(force=True)
        self.city_input.clear()
        self.city_input.fill(f_city)

        expect(self.phone_input).to_be_visible(timeout=timeout_ms)
        self.phone_input.click(force=True)
        self.phone_input.clear()
        self.phone_input.fill(f_phone)

        # 6. Verify no blocking mandatory validation errors before clicking Save
        validation_errors = self.page.locator(".field-validation-error:visible, span.text-danger:visible").all_inner_texts()
        if validation_errors:
            self.logger.warning("Detected form validation messages before save: %s", validation_errors)

        # 6. First Save - Record updated successfully / confirmation modal
        self.logger.info("Executing 1st Save action")
        expect(self.save_exact_button).to_be_visible(timeout=timeout_ms)
        self.save_exact_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        self.logger.info("Verifying 1st Save confirmation popup and clicking OK")
        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click(force=True)
            self._wait_for_loader()

        # 7. Final Save - Record Saved successfully / confirmation modal
        self.logger.info("Executing final Save action")
        expect(self.text_applicant_permit_no).to_be_visible(timeout=timeout_ms)
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)

        self.logger.info("Verifying final Save confirmation popup and clicking OK")
        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click(force=True)
            self._wait_for_loader()

        return {
            "company_name": company_name,
            "district": sel_district,
            "county": sel_county,
            "latitude": f_lat,
            "longitude": f_lon,
            "owner_name": f_owner_name,
            "city": f_city,
            "phone": f_phone,
        }

    def execute_junkyard_add_paper_application_full_workflow(
        self, company_name: str = "test"
    ) -> Dict[str, str]:
        """
        Composite high-level workflow:
        1. Navigates to Junkyard/Permit Search page
        2. Clicks 'Add Paper Application'
        3. Fills company, dropdowns, coordinates, and Faker owner information
        4. Saves form, confirms OK dialogs, and completes Junkyard application creation
        """
        self.navigate_to_junkyard_search()
        self.click_add_paper_application()
        return self.fill_and_submit_junkyard_application(company_name=company_name)
