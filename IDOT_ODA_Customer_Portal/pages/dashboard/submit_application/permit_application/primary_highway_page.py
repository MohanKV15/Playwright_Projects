import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.base_permit_page import (
    BasePermitApplicationPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata import (
    TestDataFactory,
    generate_primary_highway_test_data,
)

logger = logging.getLogger(__name__)
fake = Faker()


class PrimaryHighwayPage(BasePermitApplicationPage):
    """
    Page Object Model representing the Customer Portal:
    Permit Application - Business Area Sign - Primary Highway workflow.

    Encapsulates Primary Highway navigation, Sign Information, Location Information,
    and end-to-end submission workflow.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # 1. Navigation Locators
        # -------------------------------------------------------------
        self.primary_highway_btn = page.locator("#btnPrimary")
        self.primary_highway_heading = page.locator("text=Primary Highway").first

        # -------------------------------------------------------------
        # 2. Section Headers
        # -------------------------------------------------------------
        self.sec_sign_info = page.locator("text=Sign Information").first
        self.sec_location_info = page.locator("text=Location Information").first

        # -------------------------------------------------------------
        # 3. Sign Information Locators
        # -------------------------------------------------------------
        self.erection_date_input = page.locator(".k-datepicker input").first
        self.static_message_radio = page.locator("label[for='MessageType_Static']").first
        self.airport_no_radio = page.locator("label[for='TwoMileNo_No']").first
        self.airport_name_input = page.get_by_role(
            "textbox", name=re.compile(r"Name of airport", re.I)
        )

        # -------------------------------------------------------------
        # 4. Location Information Locators
        # -------------------------------------------------------------
        self.incorp_limits_yes_radio = page.locator("label[for='LocInLimitYes_Yes']").first
        self.municipality_input = page.get_by_role(
            "textbox", name=re.compile(r"Name of Municipality", re.I)
        )
        self.zoning_input = page.get_by_role(
            "textbox", name=re.compile(r"Present Zoning Classification", re.I)
        )

        self.unzoned_yes_radio = page.locator("label[for='LocUnzonedYes_Yes']").first
        self.com600_yes_radio = page.locator("label[for='LocActivityYes_Yes']").first
        self.com_visible_yes_radio = page.locator("label[for='IsVisibleYes_Yes']").first

        self.sign_distance1_input = page.locator("#signlocated")
        self.distance1_unit_radio = page.locator("label[for='Feet_Feet']").first
        self.landmarks_input = page.get_by_role(
            "textbox", name=re.compile(r"Of Route, other landmarks etc", re.I)
        )
        self.sign_distance2_input = page.locator("#signlocated2")
        self.distance2_unit_radio = page.locator("label[for='Feet2_Feet']").first
        self.sign_distance_range_radio = page.locator(
            "label[for='hund_two_100'], label[for='three_four_30'], label[for='six_ten_600']"
        ).first

    # -----------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------
    def navigate_to_primary_highway_application(self) -> "PrimaryHighwayPage":
        """Navigates from Dashboard to the Primary Highway permit application form."""
        self.logger.info("Navigating to Primary Highway Application Form")
        self._wait_for_loader(timeout=30000)

        if self.primary_highway_heading.is_visible(timeout=1500):
            return self

        self.navigate_to_permit_application_menu()
        expect(self.primary_highway_btn).to_be_visible(timeout=30000)
        self.primary_highway_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.primary_highway_heading).to_be_visible(timeout=35000)
        return self

    # -----------------------------------------------------------------
    # Sign Information (Always 1st option in dropdowns, dynamic Faker)
    # -----------------------------------------------------------------
    def fill_sign_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Sign Information selecting 1st option for all dropdowns and dynamic Faker dimensions."""
        self.logger.info("Filling Sign Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        self.scroll_to_section(self.sec_sign_info)

        # Erection Date
        erect_date = form_data.get("erection_date") or TestDataFactory.today()
        self.kendo_datepicker.set_first_datepicker(erect_date)

        # Message Type (Static)
        self.static_message_radio.click()

        # Dropdowns: always 1st option in the list
        for ddl_id in ("StructureType", "ConfigNumber", "VerticalSupports", "NumOfSupports", "SignLighting"):
            self.kendo_dropdown.select_first_option(ddl_id)

        # Dimensions via KendoNumericTextBox
        w = float(form_data.get("face_width", 3.5))
        h = float(form_data.get("face_height", 2.0))
        m = float(form_data.get("height_to_molding", 2.5))
        t = float(form_data.get("height_to_top", 12.0))

        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Width1", w)
        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Height1", h)
        self.kendo_numeric.set_value_by_id("HeightBottomMolding", m)
        self.kendo_numeric.set_value_by_id("HeightToTop", t)

        # Airport Restrictions (No)
        self.airport_no_radio.click()
        if self.airport_name_input.is_visible(timeout=300):
            airport = form_data.get("airport_name") or f"{fake.city()[:12]} Municipal Airport"
            self.airport_name_input.fill(airport)

        return self

    # -----------------------------------------------------------------
    # Reusable Location Sub-section: Sign Distances, Directions, Landmarks
    # -----------------------------------------------------------------
    def fill_sign_distances_and_landmarks(self, form_data: Dict[str, Any]) -> None:
        """
        Fills sign distances, direction dropdowns (always 1st option), and landmark text.
        Shared between Primary Highway and Directional Sign to avoid code duplication.
        """
        dist1 = float(form_data.get("sign_distance1", 2.5))
        dist2 = float(form_data.get("sign_distance2", 3.0))
        landmarks = form_data.get("landmarks") or f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}"

        # Distance 1, Unit (Feet), Direction 1 (always 1st option)
        self.distance1_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction")

        # Landmarks
        self.landmarks_input.fill(landmarks)

        # Distance 2, Unit (Feet), Direction 2 (always 1st option)
        self.distance2_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction2")

        # Set numeric inputs
        self.kendo_numeric.set_value_by_id("signlocated", dist1)
        self.kendo_numeric.set_value_by_id("signlocated2", dist2)

    # -----------------------------------------------------------------
    # Location Information
    # -----------------------------------------------------------------
    def fill_location_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Location Information: cascading dropdowns, limits, zoning, distances, and landmarks."""
        self.logger.info("Filling Location Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        self.scroll_to_section(self.sec_location_info)

        # Cascading dropdowns (always 1st option)
        self.fill_district_county_route(
            district_id="EP_Permit_Application_District",
            county_id="EP_Permit_Application_County",
            route_id="EP_Permit_Application_Route",
        )

        # Incorporated limits (Yes) with Municipality & Zoning
        self.incorp_limits_yes_radio.click()
        municipality = form_data.get("municipality") or fake.city()[:15]
        self.municipality_input.fill(municipality)

        if self.zoning_input.is_visible(timeout=1000):
            zoning = form_data.get("zoning") or f"Commercial C-{fake.random_int(1, 5)}"
            self.zoning_input.fill(zoning)

        # Condition Radios (Yes)
        if self.unzoned_yes_radio.is_visible(timeout=1000):
            self.unzoned_yes_radio.click()
        if self.com600_yes_radio.is_visible(timeout=500):
            self.com600_yes_radio.click()
        if self.com_visible_yes_radio.is_visible(timeout=500):
            self.com_visible_yes_radio.click()

        # Distances, Directions (1st dropdown), and Landmarks
        self.fill_sign_distances_and_landmarks(form_data)

        # Distance range radio
        if self.sign_distance_range_radio.is_visible(timeout=1000):
            self.sign_distance_range_radio.click()

        return self

    # -----------------------------------------------------------------
    # Full End-to-End Workflow
    # -----------------------------------------------------------------
    def submit_complete_primary_highway_application(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> PaymentPage:
        """Executes full end-to-end submission for Business Area Sign - Primary Highway."""
        test_data = data or generate_primary_highway_test_data()
        self.navigate_to_primary_highway_application()
        self.fill_sign_information(test_data)
        self.fill_location_information(test_data)
        self.fill_property_owner_information(test_data)
        self.upload_proof_of_property(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        return self.submit_and_confirm_application()
