import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata.junkyard_data import generate_junkyard_test_data

logger = logging.getLogger(__name__)
fake = Faker()


class JunkyardPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Customer Portal:
    Permit Application - Junkyard workflow.

    Inherits all core form filling, property owner details, attachment uploading,
    acknowledgment & signature, submission, and payment gateway integration directly
    from PrimaryHighwayPage without duplicate code.
    Only implements Junkyard-specific navigation, Yard Information, and Location Information.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # 1. Navigation Locators for Junkyard
        # -------------------------------------------------------------
        self.junkyard_card = page.get_by_text("Junkyard", exact=True)
        self.junkyard_btn = page.locator("#btnJunkyard")
        self.junkyard_heading = (
            page.get_by_role("heading", name=re.compile(r"Permit Application - Junkyard", re.I))
            .or_(page.locator("text=Permit Application - Junkyard"))
            .first
        )
        self.junkyard_subheading = page.get_by_text(
            "The applicant must fully complete and submit the", exact=False
        ).first
        self.yard_info_heading = page.get_by_text("Yard Information", exact=False).first

        # -------------------------------------------------------------
        # 2. Yard Information Locators
        # -------------------------------------------------------------
        self.yard_type_junkyard_radio = page.locator("label[for='MessageTypeYes_Junkyard']")
        self.yard_type_scrap_radio = page.locator("label[for='MessageTypeNo_Scrap Processing Facility']")
        self.sec_of_state_input = page.locator("#SecOfState")
        self.date_yard_established_input = page.locator("#DateYardEstablished")
        self.yard_screened_yes_radio = page.locator("label[for='YardScreenedYes_Yes']")
        self.yard_screened_no_radio = page.locator("label[for='YardScreenedNo_No']")
        self.screening_mat_dropdown = page.locator("#ScreeningMat")

        # -------------------------------------------------------------
        # 3. Location Information Locators (Junkyard Specific)
        # -------------------------------------------------------------
        self.district_dropdown = page.locator("#District")
        self.county_dropdown = page.locator("#County")
        self.route_dropdown = page.locator("#Route")
        self.latitude_input = page.locator("#locationlat")
        self.longitude_input = page.locator("#locationLong")
        self.yard_location_dist = page.locator("#LocationDist")
        self.yard_direction_dropdown = page.locator("#LocationDirection")
        self.route_landmarks_input = page.locator("#RouteLandmarks")
        self.within_limits_yes_radio = page.locator("label[for='LocInUnzonedYes1_1']")
        self.within_limits_no_radio = page.locator("label[for='LocIsUnzoneNo_2']")
        self.municipality_auth_input = page.locator("#MunOrZoningAuth")
        self.zoning_classification_input = page.locator("#ZoningClass")

        # Location Condition Radios
        self.activity_1000ft_yes_radio = page.locator("label[for='InLimitsYes_1']")
        self.activity_same_side_yes_radio = page.locator("label[for='IsSameYes_1']")
        self.zoned_area_yes_radio = page.locator("label[for='LocIsUnzoneYesYes_1']")

    # -----------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------
    def navigate_to_junkyard_application(self) -> "JunkyardPage":
        """
        Navigates from Dashboard to the Junkyard permit application form:
        1. Calls inherited navigate_to_permit_application_menu().
        2. Asserts 'Junkyard' option is visible and clicks '#btnJunkyard'.
        3. Asserts 'Permit Application - Junkyard' heading and 'Yard Information' section.
        """
        self.logger.info("Navigating to Junkyard Application Form")
        self._wait_for_loader(timeout=30000)

        if self.junkyard_heading.is_visible(timeout=1500):
            return self

        self.navigate_to_permit_application_menu()
        expect(self.junkyard_card).to_be_visible(timeout=30000)
        expect(self.junkyard_btn).to_be_visible(timeout=30000)
        self.junkyard_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.junkyard_heading).to_be_visible(timeout=35000)
        try:
            expect(self.junkyard_subheading).to_be_visible(timeout=10000)
        except Exception:
            pass
        expect(self.yard_info_heading).to_be_visible(timeout=10000)

        self.logger.info("Successfully navigated to Junkyard Permit Application")
        return self

    # -----------------------------------------------------------------
    # Yard Information
    # -----------------------------------------------------------------
    def fill_yard_information(self, data: Optional[Dict[str, Any]] = None) -> "JunkyardPage":
        """
        Fills Yard Information section using Faker:
        1. Selects Yard Type (Junkyard).
        2. Fills Secretary of State UDL# using Faker.
        3. Sets Date Yard Established via KendoDatePicker.
        4. Selects Yard Screened (Yes) and selects Screening Material option.
        """
        self.logger.info("Filling Yard Information section")
        form_data = data or generate_junkyard_test_data()
        self._wait_for_loader()

        self.yard_type_junkyard_radio.click()

        sec_num = form_data.get("sec_of_state") or f"UDL{fake.random_int(100000, 999999)}"
        self.sec_of_state_input.fill(sec_num)

        est_date = form_data.get("date_yard_established") or fake.date_this_decade().strftime("%m/%d/%Y")
        self.kendo_datepicker.set_date_by_id("DateYardEstablished", est_date)

        self.yard_screened_yes_radio.click()
        self.page.wait_for_timeout(300)
        self.kendo_dropdown.select_first_option("ScreeningMat")

        return self

    # -----------------------------------------------------------------
    # Location Information
    # -----------------------------------------------------------------
    def fill_location_information(self, data: Optional[Dict[str, Any]] = None) -> "JunkyardPage":
        """
        Fills Location Information for Junkyard using Faker:
        1. Cascading dropdowns: District -> County -> Route.
        2. GPS Coordinates: Latitude & Longitude.
        3. Yard location distance and direction ('East').
        4. Route landmarks using Faker.
        5. Incorporated limits (Yes) with Municipality & Zoning Classification via Faker.
        6. Industrial activity and zoning condition radios (Yes).
        """
        self.logger.info("Filling Location Information for Junkyard")
        form_data = data or generate_junkyard_test_data()
        self._wait_for_loader()

        self.kendo_dropdown.select_first_option("District")
        self.page.wait_for_timeout(1000)
        self.kendo_dropdown.select_first_option("County")
        self.page.wait_for_timeout(1000)
        self.kendo_dropdown.select_first_option("Route")

        lat = form_data.get("latitude", "39.7817")
        lon = form_data.get("longitude", "-89.6501")
        self.latitude_input.fill(str(lat))
        self.longitude_input.fill(str(lon))

        dist = float(form_data.get("location_distance", 1.0))
        self.kendo_numeric.set_value_by_id("LocationDist", dist)

        direction = form_data.get("location_direction", "East")
        try:
            if not self.kendo_dropdown.select("LocationDirection", option_text=direction, timeout_ms=3000):
                self.kendo_dropdown.select_first_option("LocationDirection")
        except Exception:
            self.kendo_dropdown.select_first_option("LocationDirection")

        landmarks = form_data.get("route_landmarks") or f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}"
        self.route_landmarks_input.fill(landmarks)

        self.within_limits_yes_radio.click()

        muni = form_data.get("municipality") or f"{fake.city()[:15]}"
        zoning = form_data.get("zoning_class") or f"Commercial C-{fake.random_int(1, 5)}"
        self.municipality_auth_input.fill(muni)
        self.zoning_classification_input.fill(zoning)

        if self.activity_1000ft_yes_radio.is_visible(timeout=1000):
            self.activity_1000ft_yes_radio.click()
        if self.activity_same_side_yes_radio.is_visible(timeout=500):
            self.activity_same_side_yes_radio.click()
        if self.zoned_area_yes_radio.is_visible(timeout=500):
            self.zoned_area_yes_radio.click()

        return self

    # -----------------------------------------------------------------
    # Complete Workflow
    # -----------------------------------------------------------------
    def submit_complete_junkyard_application(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> PaymentPage:
        """
        Executes full end-to-end permit application submission for Junkyard:
        1. Navigates to Junkyard application.
        2. Fills Yard Information.
        3. Fills Location Information.
        4. Fills Property Owner Information (inherited from parent).
        5. Uploads Proof of Property (inherited from parent).
        6. Fills Acknowledgment and Signature (inherited from parent).
        7. Submits application and returns to Dashboard (inherited from parent).
        """
        test_data = data or generate_junkyard_test_data()
        self.navigate_to_junkyard_application()
        self.fill_yard_information(test_data)
        self.fill_location_information(test_data)
        self.fill_property_owner_information(test_data)
        self.upload_proof_of_property(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        return self.submit_and_confirm_application()
