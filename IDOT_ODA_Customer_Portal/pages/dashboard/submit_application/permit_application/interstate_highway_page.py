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


class InterstateHighwayPage(PrimaryHighwayPage):
    """
    Page Object Model representing the Customer Portal:
    Permit Application - Business Area Sign - Interstate Highway workflow.

    Inherits all core form filling, attachment upload, signature, submission,
    and payment gateway integration from PrimaryHighwayPage, customizing the
    Interstate Highway navigation, 1959 limits, and 'Zoning classification on' field.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # Navigation Locators for Interstate Highway
        # -------------------------------------------------------------
        self.interstate_highway_card = page.get_by_text(
            "Business Area Sign - Interstate Highway", exact=False
        )
        self.interstate_highway_btn = page.locator("#btnInterState")
        self.interstate_highway_heading = (
            page.get_by_role("heading", name=re.compile(r"Permit Application - Business", re.I))
            .or_(page.locator("text=Interstate Highway"))
            .first
        )

        # -------------------------------------------------------------
        # Interstate-Specific Field Locators
        # -------------------------------------------------------------
        self.limits_1959_no_radio = page.locator("label[for='WithinLimitsNo_No']").first
        self.limits_1959_yes_radio = page.locator("label[for='InLimitsYes_Yes']").first
        self.zoning_on_date_input = page.locator(
            "#ZoningClass1959, input[name='ZoningClass1959']"
        ).or_(
            page.get_by_role("textbox", name=re.compile(r"Zoning classification on", re.I))
        ).first
        self.interstate_distance_range_radio = page.locator(
            "label[for='three_four_30'], label[for='six_ten_600'], label[for='IntLocInfo_500_500']"
        ).first

    def navigate_to_interstate_highway_application(self) -> "InterstateHighwayPage":
        """
        Navigates from Customer Portal Dashboard to the Interstate Highway permit application form:
        1. Calls inherited navigate_to_permit_application_menu() to open permit options.
        2. Asserts 'Business Area Sign - Interstate Highway' is visible.
        3. Clicks '#btnInterState' (Interstate Highway).
        4. Asserts 'Permit Application - Business' heading is visible.
        """
        self.logger.info("Navigating to Interstate Highway Application Form")
        self._wait_for_loader(timeout=30000)

        if self.interstate_highway_heading.is_visible(timeout=1500):
            return self

        self.navigate_to_permit_application_menu()
        expect(self.interstate_highway_card).to_be_visible(timeout=30000)
        expect(self.interstate_highway_btn).to_be_visible(timeout=30000)
        self.interstate_highway_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.interstate_highway_heading).to_be_visible(timeout=35000)
        self.logger.info("Successfully navigated to Interstate Highway Permit Application")
        return self

    def fill_location_information(self, data: Optional[Dict[str, Any]] = None) -> "InterstateHighwayPage":
        """
        Fills Location Information:
        Calls parent PrimaryHighwayPage to fill common fields and handles Interstate-specific fields
        (1959 incorporated limits radio, 1959 zoning classification with Faker, and Interstate distance range).
        """
        super().fill_location_information(data)
        form_data = data or generate_primary_highway_test_data()

        # Interstate-specific 1959 limits radio -> Select Yes
        if self.limits_1959_yes_radio.is_visible(timeout=1000):
            self.logger.info("Selecting 'Yes' for 1959 incorporated limits")
            self.limits_1959_yes_radio.click()
        elif self.limits_1959_no_radio.is_visible(timeout=1000):
            self.limits_1959_no_radio.click()

        # Interstate-specific Zoning classification on September 21, 1959 -> Fill via Faker
        zoning_text = (
            form_data.get("zoning_1959")
            or form_data.get("zoning_on_date")
            or form_data.get("zoning")
            or f"Commercial C-{fake.random_int(1, 5)}"
        )
        if self.zoning_on_date_input.is_visible(timeout=2000):
            self.logger.info(f"Filling Interstate 'Zoning classification on' field: '{zoning_text}'")
            self.zoning_on_date_input.click()
            self.zoning_on_date_input.fill(zoning_text)

        # Ensure Interstate distance range radio is selected
        if self.interstate_distance_range_radio.is_visible(timeout=1000):
            self.interstate_distance_range_radio.click()

        return self

    def submit_complete_interstate_highway_application(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> PaymentPage:
        """Executes complete end-to-end submission for Business Area Sign - Interstate Highway."""
        test_data = data or generate_primary_highway_test_data()
        self.navigate_to_interstate_highway_application()
        self.fill_sign_information(test_data)
        self.fill_location_information(test_data)
        self.fill_property_owner_information(test_data)
        self.upload_proof_of_property(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        return self.submit_and_confirm_application()
