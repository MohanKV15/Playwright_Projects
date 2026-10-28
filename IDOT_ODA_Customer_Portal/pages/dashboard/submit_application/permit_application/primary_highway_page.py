import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.sync_api import Page, Locator, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata.primary_highway_data import generate_primary_highway_test_data

logger = logging.getLogger(__name__)
fake = Faker()


class PrimaryHighwayPage(BasePage):
    """
    Page Object Model representing the Customer Portal:
    Permit Application - Business Area Sign - Primary Highway workflow.

    Encapsulates form navigation, field interactions, file upload,
    acknowledgment, submission, and confirmation modal workflows.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # 1. Navigation Locators
        # -------------------------------------------------------------
        self.submit_app_dashboard_btn = page.locator("#btnSubmitApp")
        self.permit_app_btn = page.locator("#btnPermitApp")
        self.application_list_heading = page.get_by_role(
            "heading", name=re.compile(r"Application List", re.I)
        )
        self.primary_highway_btn = page.locator("#btnPrimary")
        self.primary_highway_heading = page.locator("text=Primary Highway").first

        # -------------------------------------------------------------
        # 2. Section Headers (Used for steady, professional section scrolling)
        # -------------------------------------------------------------
        self.sec_sign_info = page.locator("text=Sign Information").first
        self.sec_location_info = page.locator("text=Location Information").first
        self.sec_property_owner = page.locator("text=Property Owner Information").first
        self.sec_attachments = page.locator("text=Attachments").first
        self.sec_signature = page.locator("text=Signature").first

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

        # -------------------------------------------------------------
        # 5. Property Owner Information Locators
        # -------------------------------------------------------------
        self.owner_name_input = page.locator("#cmgenpoc_first_name, #PropOwnerName").or_(
            page.get_by_role("textbox", name=re.compile(r"Property Owner Name", re.I))
        ).first
        self.owner_address1_input = page.locator("#cmgenadd_address1, #PropOwnerAdd1").or_(
            page.get_by_role("textbox", name=re.compile(r"Property Owner Address 1", re.I))
        ).first
        self.owner_city_input = page.locator("#cmgenadd_city, #PropOwnerCity").or_(
            page.get_by_role("textbox", name=re.compile(r"City \*", re.I))
        ).first
        self.owner_zip_input = page.locator("#cmgenadd_zip_code, #PropOwnerZip").first
        self.owner_phone_input = page.locator("#cmgenpoc_com_phone, #PropOwnerPhone").first
        self.owner_email_input = page.locator("#cmgenpoc_email, #PropOwnerEmail").first
        self.prop_owner_state_dropdown = page.locator("#cmgenadd_state_d, #PropOwnerState").first
        self.ownership_lease_radio = page.locator("label[for='Lease_Lease']").first

        # -------------------------------------------------------------
        # 6. Attachment Locators
        # -------------------------------------------------------------
        self.file_input = page.locator("#uploadOwnerPermission, input[type='file']").first

        # -------------------------------------------------------------
        # 7. Acknowledgment & Signature Locators
        # -------------------------------------------------------------
        self.acknowledgment_checkbox = page.locator("label[for='ICert']").first
        self.signature_checkbox = page.locator("label[for='ICert2'], label[for='isYard']").first
        self.signer_name_input = page.locator("#SigName").or_(
            page.get_by_role("textbox", name="Name *", exact=True)
        ).first
        self.signer_title_input = page.locator("#SigTitle").or_(
            page.get_by_role("textbox", name="Title *", exact=True)
        ).first

        # -------------------------------------------------------------
        # 8. Submission & 1st Page (Confirmation Modal) Locators
        # -------------------------------------------------------------
        self.submit_button = page.locator(
            "#CompletePayment, #btnSubmit, button:has-text('Submit')"
        ).first
        self.modal_record_saved_heading = page.locator("text=Outdoor Advertising System").first
        self.modal_record_saved_text = page.locator("text=Record saved successfully").first
        self.modal_confirm_button = page.locator(
            "button:has-text('OK'), a.k-button:has-text('OK'), .k-dialog-actions button, .k-window button, [role='dialog'] button, button.k-primary"
        ).filter(has_text=re.compile(r"^OK$", re.I)).first


    # -----------------------------------------------------------------
    # Navigation Helpers & Actions
    # -----------------------------------------------------------------
    def navigate_to_permit_application_menu(self) -> None:
        """
        Navigates from Dashboard to the Permit Application card selection menu.
        Shared across all permit application types (Primary Highway, Interstate, etc.).
        """
        self._wait_for_loader(timeout=30000)
        submit_btn = self.page.locator(
            "#btnSubmitApp, a:has-text('Submit an Application'), button:has-text('Submit an Application')"
        ).first
        expect(submit_btn).to_be_visible(timeout=35000)
        submit_btn.click()
        self._wait_for_loader(timeout=30000)

        if not self.permit_app_btn.is_visible(timeout=3000):
            try:
                submit_btn.click(force=True)
                self._wait_for_loader(timeout=30000)
            except Exception:
                pass

        expect(self.permit_app_btn).to_be_visible(timeout=30000)
        self.permit_app_btn.click()
        self._wait_for_loader(timeout=30000)

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

    def fill_sign_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Sign Information step-by-step from top to bottom."""
        self.logger.info("Filling Sign Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        # Step 1: Smoothly bring Sign Information section into view
        self.scroll_to_section(self.sec_sign_info)

        # Step 2: Erection Date (always present day via KendoDatePicker)
        erect_date = form_data.get("erection_date", "")
        if erect_date:
            self.kendo_datepicker.set_first_datepicker(erect_date)

        # Step 3: Message Type (Static)
        self.static_message_radio.click()

        # Step 4: Dropdowns (1st option via KendoDropdown component)
        self.kendo_dropdown.select_first_option("StructureType")
        self.kendo_dropdown.select_first_option("ConfigNumber")
        self.kendo_dropdown.select_first_option("VerticalSupports")
        self.kendo_dropdown.select_first_option("NumOfSupports")
        self.kendo_dropdown.select_first_option("SignLighting")

        # Step 5: Dimensions via KendoNumericTextBox component
        w = float(
            form_data.get(
                "face_width",
                round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=2.0, max_value=5.0), 1),
            )
        )
        h = float(
            form_data.get(
                "face_height",
                round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1),
            )
        )
        m = float(
            form_data.get(
                "height_to_molding",
                round(fake.pyfloat(left_digits=1, right_digits=1, positive=True, min_value=1.0, max_value=3.0), 1),
            )
        )
        t = float(
            form_data.get(
                "height_to_top",
                round(fake.pyfloat(left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=15.0), 1),
            )
        )

        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Width1", w)
        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Height1", h)
        self.kendo_numeric.set_value_by_id("HeightBottomMolding", m)
        self.kendo_numeric.set_value_by_id("HeightToTop", t)

        # Step 6: Airport Restrictions (No) & Airport Name
        self.airport_no_radio.click()
        if self.airport_name_input.is_visible(timeout=300):
            airport = form_data.get("airport_name") or f"{fake.city()[:12]} Municipal Airport"
            self.airport_name_input.fill(airport)

        return self

    def fill_location_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Location Information step-by-step from top to bottom."""
        self.logger.info("Filling Location Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        # Step 1: Smoothly bring Location Information section into view
        self.scroll_to_section(self.sec_location_info)

        # Step 2: District -> County -> Route (cascading 1st options via KendoDropdown component)
        self.kendo_dropdown.select_first_option("EP_Permit_Application_District")
        self.kendo_dropdown.select_first_option("EP_Permit_Application_County")
        self.kendo_dropdown.select_first_option("EP_Permit_Application_Route")

        # Step 3: Incorporated limits -> Yes, Municipality & Zoning
        self.incorp_limits_yes_radio.click()
        municipality = form_data.get("municipality") or f"{fake.city()[:15]}"
        self.municipality_input.fill(municipality)
        if self.zoning_input.is_visible(timeout=1000):
            zoning = form_data.get("zoning") or f"Commercial C-{fake.random_int(1, 5)}"
            self.zoning_input.fill(zoning)

        # Step 4: Condition Radios (Yes)
        if self.unzoned_yes_radio.is_visible(timeout=1000):
            self.unzoned_yes_radio.click()
        if self.com600_yes_radio.is_visible(timeout=500):
            self.com600_yes_radio.click()
        if self.com_visible_yes_radio.is_visible(timeout=500):
            self.com_visible_yes_radio.click()

        # Step 5: Distance 1, Unit (Feet), Direction 1
        dist1 = float(
            form_data.get(
                "sign_distance1",
                round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2),
            )
        )
        self.distance1_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction")

        # Step 6: Landmarks
        landmarks = form_data.get("landmarks") or f"Milepost {fake.random_int(10, 80)} at Exit {fake.random_int(1, 30)}"
        self.landmarks_input.fill(landmarks)

        # Step 7: Distance 2, Unit (Feet), Direction 2
        dist2 = float(
            form_data.get(
                "sign_distance2",
                round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1.5, max_value=8.5), 2),
            )
        )
        self.distance2_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction2")

        # Step 8: Populate 'Sign will be located' numeric inputs via KendoNumericTextBox component
        self.kendo_numeric.set_value_by_id("signlocated", dist1)
        self.kendo_numeric.set_value_by_id("signlocated2", dist2)

        # Step 9: Distance range radio (100-199 ft / 500-599 ft)
        if self.sign_distance_range_radio.is_visible(timeout=1000):
            self.sign_distance_range_radio.click()
        return self

    def fill_property_owner_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Property Owner Details step-by-step using test data or Faker."""
        self.logger.info("Filling Property Owner Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        # Step 1: Smoothly bring Property Owner section into view
        self.scroll_to_section(self.sec_property_owner)

        # Step 2: Fill text fields in order using Faker
        owner_name = form_data.get("owner_name") or fake.name()
        owner_address = form_data.get("owner_address") or fake.street_address()
        owner_city = form_data.get("owner_city") or fake.city()
        owner_zip = form_data.get("owner_zip") or fake.zipcode()
        phone = (
            form_data.get("owner_phone")
            or f"{fake.random_int(200, 999)}-{fake.random_int(200, 999)}-{fake.random_int(1000, 9999)}"
        )
        owner_email = form_data.get("owner_email") or fake.email()

        self.owner_name_input.fill(owner_name)
        self.owner_address1_input.fill(owner_address)
        self.owner_city_input.fill(owner_city)

        # Select State dropdown if present (Directional Sign / Junkyard)
        if self.prop_owner_state_dropdown.is_visible(timeout=500):
            try:
                self.kendo_dropdown.select_first_option(self.prop_owner_state_dropdown)
            except Exception:
                pass

        self.owner_zip_input.fill(owner_zip)

        if self.owner_phone_input.is_visible(timeout=1000):
            try:
                self.owner_phone_input.scroll_into_view_if_needed()
                self.kendo_masked.set_value(self.owner_phone_input, phone)
            except Exception:
                self.owner_phone_input.fill(phone)

        if self.owner_email_input.is_visible(timeout=500):
            self.owner_email_input.fill(owner_email)

        # Step 3: Ownership Category (Lease)
        self.ownership_lease_radio.click()
        return self

    def upload_proof_of_property(self, file_path: Optional[str] = None) -> "PrimaryHighwayPage":
        """Uploads a dummy PDF file for Proof of Property / Land directly."""
        self.logger.info("Uploading Proof of Property attachment")
        self._wait_for_loader()

        # Step 1: Smoothly scroll to Attachments section
        self.scroll_to_section(self.sec_attachments)

        if file_path and os.path.exists(file_path):
            target_path = file_path
        else:
            default_pdf = Config.PROJECT_ROOT / "testdata" / "dummy.pdf"
            if not default_pdf.exists():
                default_pdf.write_bytes(b"%PDF-1.4 IDOT ODA Test Dummy PDF Attachment")
            target_path = str(default_pdf)

        if self.file_input.count() > 0:
            self.file_input.set_input_files(target_path)
            self.logger.info(f"File uploaded successfully: {target_path}")

        return self

    def fill_acknowledgment_and_signature(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Checks Acknowledgment and Signature checkboxes and fills Signer details."""
        self.logger.info("Filling Acknowledgment and Signature section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        # Step 1: Smoothly scroll to Signature section
        self.scroll_to_section(self.sec_signature)

        # Step 2: Checkboxes
        self.acknowledgment_checkbox.click()
        self.signature_checkbox.click()

        # Step 3: Signer Name and Title via Faker
        signer_name = form_data.get("signer_name") or f"{fake.first_name()} {fake.last_name()}"
        signer_title = form_data.get("signer_title") or f"{fake.job()[:25]}"

        self.signer_name_input.fill(signer_name)
        self.signer_title_input.fill(signer_title)

        # Step 4: Ensure date is set to present day (portal pre-fills SigDate automatically in readonly)
        present_day = form_data.get("signature_date", "") or datetime.now().strftime("%m/%d/%Y")
        current_val = self.page.evaluate(
            "() => { const el = document.getElementById('SigDate'); return el ? el.value : ''; }"
        )
        if not current_val:
            self.kendo_datepicker.set_date_by_id("SigDate", present_day)
        return self

    def submit_application(self) -> "PrimaryHighwayPage":
        """Smoothly scrolls to and clicks the application Submit button."""
        self.logger.info("Submitting application...")
        self._wait_for_loader()
        try:
            self.submit_button.evaluate(
                "el => el.scrollIntoView({ behavior: 'smooth', block: 'center' })"
            )
        except Exception:
            pass

        self.submit_button.click()
        self._wait_for_loader(timeout=25000)

        # If it redirects directly to success page (CASuccessPageFull, e.g. Junkyard), wait for it
        try:
            self.page.wait_for_url(
                re.compile(r".*(CASuccessPageFull|SuccessPage).*", re.I),
                timeout=5000,
            )
        except Exception:
            pass

        return self

    def confirm_submission_modal(self) -> PaymentPage:
        """
        1st Page: Verifies the confirmation modal ('Record saved successfully') displays,
        clicks the 'OK' button, and returns the PaymentPage instance for the 2nd page flow.
        If already redirected to CASuccessPageFull (e.g. no fee applications), transitions directly.
        """
        self.logger.info("1st Page: Checking confirmation modal or success redirection...")
        if "casuccesspagefull" in self.page.url.lower():
            self.logger.info("Already arrived at CASuccessPageFull (direct submission without modal)")
            return PaymentPage(self.page)

        try:
            self.modal_record_saved_text.wait_for(state="visible", timeout=15000)
            self.logger.info("1st Page: 'Record saved successfully' confirmation modal is displayed")
            self.logger.info("Clicking OK button on confirmation modal...")
            self.modal_confirm_button.click()
            self._wait_for_loader()
        except Exception as e:
            self.logger.info(f"Confirmation modal bypassed or already dismissed: {e}")

        return PaymentPage(self.page)

    def submit_and_confirm_application(self, timeout_ms: int = 40000) -> PaymentPage:
        """
        Executes end-to-end permit application submission:
        1. Clicks Submit on permit application.
        2. 1st Page displays with confirmation modal ('Record saved successfully') or redirects to success.
        3. User clicks on the 'OK' button (if modal present).
        4. Transitions to PaymentPage and completes full payment gateway & return home flow.
        """
        self.submit_application()
        payment_page = self.confirm_submission_modal()
        payment_page.complete_payment_flow()
        return payment_page

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
