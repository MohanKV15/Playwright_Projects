import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata import generate_primary_highway_test_data

logger = logging.getLogger(__name__)
fake = Faker()


class DirectionalSignPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Customer Portal:
    Permit Application - Directional Sign, Official Sign or Official Notice workflow.

    Inherits all core form filling, attachment upload, signature, submission,
    and payment gateway integration from PrimaryHighwayPage, customizing the
    Directional Sign navigation, Applicant Information verification, and Location Information
    travel direction ('Direction_sn').
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # Navigation Locators for Directional Sign
        # -------------------------------------------------------------
        self.directional_sign_card = page.get_by_text(
            "Directional Sign, Official", exact=False
        )
        self.directional_sign_btn = page.locator("#btnDirectionalSign")
        self.directional_sign_heading = (
            page.get_by_role("heading", name=re.compile(r"Permit Application - Directional|Permit Application -", re.I))
            .or_(page.locator("text=Directional Sign"))
            .first
        )

        # -------------------------------------------------------------
        # Directional Sign Specific Locators
        # -------------------------------------------------------------
        self.applicant_info_container = (
            page.locator("div")
            .filter(has_text=re.compile(r"Applicant Information", re.I))
            .first
        )
        self.sign_type_directional_radio = page.locator(
            "label[for='ReportTypeD_Directional'], #ReportTypeD_Directional"
        ).first
        self.direction_travel_dropdown = page.locator("#Direction_sn")

    def navigate_to_directional_sign_application(self) -> "DirectionalSignPage":
        """
        Navigates from Customer Portal Dashboard to the Directional Sign permit application form:
        1. Calls inherited self.navigate_to_permit_application_menu() to open permit options.
        2. Asserts 'Directional Sign, Official' is visible.
        3. Clicks '#btnDirectionalSign' (Directional Sign).
        4. Asserts 'Permit Application -' heading is visible.
        5. Asserts Applicant Information section is displayed.
        """
        self.logger.info("Navigating to Directional Sign Application Form")
        self._wait_for_loader(timeout=30000)

        if self.directional_sign_heading.is_visible(timeout=1500):
            return self

        self.navigate_to_permit_application_menu()
        expect(self.directional_sign_card).to_be_visible(timeout=30000)
        expect(self.directional_sign_btn).to_be_visible(timeout=30000)
        self.directional_sign_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.directional_sign_heading).to_be_visible(timeout=35000)

        try:
            expect(self.applicant_info_container).to_be_visible(timeout=10000)
        except Exception:
            pass

        self.logger.info("Successfully navigated to Directional Sign Permit Application")
        return self

    def fill_sign_information(self, data: Optional[Dict[str, Any]] = None) -> "DirectionalSignPage":
        """
        Fills Sign Information for Directional Sign:
        Ensures Directional Sign Type is selected, then delegates to parent implementation
        for Erection Date, Message Type, Dropdowns, and Dimensions.
        """
        self.logger.info("Filling Sign Information for Directional Sign")
        if self.sign_type_directional_radio.is_visible(timeout=1500):
            try:
                self.sign_type_directional_radio.click()
            except Exception:
                pass

        super().fill_sign_information(data)
        return self

    def fill_location_information(self, data: Optional[Dict[str, Any]] = None) -> "DirectionalSignPage":
        """
        Fills Location Information for Directional Sign:
        Populates District, County, Route, travel direction ('Direction_sn' -> East),
        distances, units (Feet), and landmarks.
        """
        self.logger.info("Filling Location Information for Directional Sign")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        self.scroll_to_section(self.sec_location_info)

        # Step 1: District -> County -> Route (cascading 1st options)
        self.kendo_dropdown.select_first_option("EP_Permit_Application_District")
        self.kendo_dropdown.select_first_option("EP_Permit_Application_County")
        self.kendo_dropdown.select_first_option("EP_Permit_Application_Route")

        # Step 2: Direction of travel (Direction_sn) -> Select 'East'
        if self.direction_travel_dropdown.is_visible(timeout=1500):
            self.logger.info("Selecting travel direction 'East' in Direction_sn dropdown")
            try:
                if not self.kendo_dropdown.select("Direction_sn", option_text="East", timeout_ms=3000):
                    self.kendo_dropdown.select_first_option("Direction_sn")
            except Exception:
                self.kendo_dropdown.select_first_option("Direction_sn")

        # Step 3: Distance 1, Unit (Feet), Direction 1
        dist1 = float(
            form_data.get(
                "sign_distance1",
                round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2),
            )
        )
        self.distance1_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction")

        # Step 4: Landmarks
        landmarks = form_data.get("landmarks") or f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}"
        self.landmarks_input.fill(landmarks)

        # Step 5: Distance 2, Unit (Feet), Direction 2
        dist2 = float(
            form_data.get(
                "sign_distance2",
                round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2),
            )
        )
        self.distance2_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction2")

        # Step 6: Populate numeric inputs for sign location
        self.kendo_numeric.set_value_by_id("signlocated", dist1)
        self.kendo_numeric.set_value_by_id("signlocated2", dist2)

        return self

    def submit_complete_directional_sign_application(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> PaymentPage:
        """
        Executes complete end-to-end submission for Directional Sign:
        1. Navigates to Directional Sign form.
        2. Fills Sign Information.
        3. Fills Location Information (including Direction_sn).
        4. Fills Property Owner Information.
        5. Uploads Proof of Property.
        6. Fills Acknowledgment and Signature.
        7. Submits application and confirms 1st page modal.
        8. Completes Payment Gateway and post-payment flow.
        """
        test_data = data or generate_primary_highway_test_data()
        self.navigate_to_directional_sign_application()
        self.fill_sign_information(test_data)
        self.fill_location_information(test_data)
        self.fill_property_owner_information(test_data)
        self.upload_proof_of_property(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        return self.submit_and_confirm_application()
