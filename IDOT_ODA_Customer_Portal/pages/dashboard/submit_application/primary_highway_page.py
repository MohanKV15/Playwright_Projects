import logging
import os
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, Locator, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata.primary_highway_data import generate_primary_highway_test_data

logger = logging.getLogger(__name__)


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
        self.sign_distance_range_radio = page.locator("label[for='hund_two_100']").first

        # -------------------------------------------------------------
        # 5. Property Owner Information Locators
        # -------------------------------------------------------------
        self.owner_name_input = page.get_by_role(
            "textbox", name=re.compile(r"Property Owner Name", re.I)
        )
        self.owner_address1_input = page.get_by_role(
            "textbox", name=re.compile(r"Property Owner Address 1", re.I)
        )
        self.owner_city_input = page.get_by_role("textbox", name=re.compile(r"City \*", re.I))
        self.owner_zip_input = page.locator("#cmgenadd_zip_code")
        self.owner_phone_input = page.locator("#cmgenpoc_com_phone")
        self.owner_email_input = page.locator("#cmgenpoc_email")
        self.ownership_lease_radio = page.locator("label[for='Lease_Lease']").first

        # -------------------------------------------------------------
        # 6. Attachment Locators
        # -------------------------------------------------------------
        self.file_input = page.locator("input[type='file']").first

        # -------------------------------------------------------------
        # 7. Acknowledgment & Signature Locators
        # -------------------------------------------------------------
        self.acknowledgment_checkbox = page.locator("label[for='ICert']").first
        self.signature_checkbox = page.locator("label[for='isYard']").first
        self.signer_name_input = page.get_by_role("textbox", name="Name *", exact=True)
        self.signer_title_input = page.get_by_role("textbox", name="Title *", exact=True)

        # -------------------------------------------------------------
        # 8. Submission & 1st Page (Confirmation Modal) Locators
        # -------------------------------------------------------------
        self.submit_button = page.locator("#btnSubmit").or_(
            page.get_by_role("button", name="Submit")
        ).first
        self.modal_record_saved_heading = page.locator("text=Outdoor Advertising System").first
        self.modal_record_saved_text = page.locator("text=Record saved successfully").first
        self.modal_confirm_button = page.locator(
            "button:has-text('OK'), a.k-button:has-text('OK'), .k-dialog-actions button, .k-window button, [role='dialog'] button, button.k-primary"
        ).filter(has_text=re.compile(r"^OK$", re.I)).first

        # -------------------------------------------------------------
        # 9. 2nd Page (Payment Gateway / Global Payments) Locators
        # -------------------------------------------------------------
        self.payment_gateway_heading = (
            page.get_by_text("Make A Payment", exact=False)
            .or_(page.get_by_text("Payment Notice", exact=False))
            .or_(page.get_by_text("Payment Information", exact=False))
            .first
        )
        self.payment_notice_text = page.get_by_text("Payment Notice", exact=False).first
        self.payment_info_tab = page.get_by_text("Payment Information", exact=False).first
        self.cart_info_tab = page.get_by_text("Cart Information", exact=False).first

        # Credit Card Form fields (supports both standard #CC and portal #maskedCardNumber element IDs)
        self.cc_card_number_input = page.locator(
            "#CCCardNumber, #maskedCardNumber, #CardNumber, input[name='maskedCardNumber']"
        ).first
        self.cc_cvv_input = page.locator("#CCCardCVV, #CVV2, #CVV, input[name='CVV2']").first
        self.cc_name_input = page.locator("#CCNameOnCard, #NameOnCard, input[name='NameOnCard']").first
        self.cc_exp_month_select = page.locator(
            "#CCExpirationMonth, #ExpirationMonth, select[name='ExpirationMonth']"
        ).first
        self.cc_exp_year_select = page.locator(
            "#CCExpirationYear, #ExpirationYear, select[name='ExpirationYear']"
        ).first
        self.cc_zip_input = page.locator(
            "#CardBillingPostalCode, #CCCardZip, #CCZipCode, #CCZip, input[name='CardBillingPostalCode']"
        ).first
        self.next_step_review_btn = page.locator(
            "#bntNextPaymentInfo, button:has-text('Next Step: Review Payment'), button:has-text('Review Payment'), input[value*='Review Payment']"
        ).first
        self.submit_payment_btn = page.locator(
            "#submitPayment, button:has-text('Submit Payment'), button:has-text('Pay'), button:has-text('Confirm'), button:has-text('Make Payment'), input[value*='Submit']"
        ).first
        self.return_home_btn = page.locator(
            "button:has-text('Return Home'), a:has-text('Return Home'), text='Return Home'"
        ).first

    # -----------------------------------------------------------------
    # Helper Methods
    # -----------------------------------------------------------------
    def scroll_to_section(self, section_locator: Locator) -> None:
        """
        Scrolls smoothly to a major section heading to provide a steady,
        natural visual progression down the page without any erratic blinking.
        """
        try:
            section_locator.evaluate(
                "el => el.scrollIntoView({ behavior: 'smooth', block: 'start' })"
            )
            self.page.wait_for_timeout(200)
        except Exception:
            pass

    # -----------------------------------------------------------------
    # Workflow Actions
    # -----------------------------------------------------------------
    def navigate_to_primary_highway_application(self) -> "PrimaryHighwayPage":
        """Navigates from Dashboard to the Primary Highway permit application form."""
        self.logger.info("Navigating to Primary Highway Application Form")
        self._wait_for_loader(timeout=30000)

        if self.primary_highway_heading.is_visible(timeout=1500):
            return self

        submit_btn = self.page.locator(
            "#btnSubmitApp, a:has-text('Submit an Application'), button:has-text('Submit an Application')"
        ).first
        expect(submit_btn).to_be_visible(timeout=35000)
        self.page.wait_for_timeout(300)
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
            try:
                if self.erection_date_input.is_visible(timeout=500):
                    self.erection_date_input.fill(erect_date)
            except Exception:
                pass
            self.page.evaluate(
                f"""
                (() => {{
                    if (window.$) {{
                        const dp = $('.k-datepicker input').first().data('kendoDatePicker');
                        if (dp) dp.value('{erect_date}');
                        $('.k-datepicker input').first().val('{erect_date}').trigger('change');
                    }}
                }})();
                """
            )

        # Step 3: Message Type (Static)
        self.static_message_radio.click()

        # Step 4: Dropdowns (1st option via KendoDropdown component)
        self.kendo_dropdown.select_first_option("StructureType")
        self.kendo_dropdown.select_first_option("ConfigNumber")
        self.kendo_dropdown.select_first_option("VerticalSupports")
        self.kendo_dropdown.select_first_option("NumOfSupports")
        self.kendo_dropdown.select_first_option("SignLighting")

        # Step 5: Dimensions via KendoNumericTextBox component
        w = float(form_data.get("face_width", 2.0))
        h = float(form_data.get("face_height", 1.0))
        m = float(form_data.get("height_to_molding", 1.0))
        t = float(form_data.get("height_to_top", 10.0))

        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Width1", w)
        self.kendo_numeric.set_value_by_id("ODA_Outdoor_Face_Detail_Face_Height1", h)
        self.kendo_numeric.set_value_by_id("HeightBottomMolding", m)
        self.kendo_numeric.set_value_by_id("HeightToTop", t)

        # Step 6: Airport Restrictions (No) & Airport Name
        self.airport_no_radio.click()
        if self.airport_name_input.is_visible(timeout=300):
            self.airport_name_input.fill(form_data.get("airport_name", "Municipal Airport"))

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
        self.municipality_input.fill(form_data.get("municipality", "Chicago"))
        self.zoning_input.fill(form_data.get("zoning", "Commercial C-1"))

        # Step 4: Condition Radios (Yes)
        self.unzoned_yes_radio.click()
        self.com600_yes_radio.click()
        self.com_visible_yes_radio.click()

        # Step 5: Distance 1, Unit (Feet), Direction 1
        dist1 = float(form_data.get("sign_distance1", 2.002))
        self.distance1_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction")

        # Step 6: Landmarks
        self.landmarks_input.fill(form_data.get("landmarks", "Milepost 50 at Exit 10"))

        # Step 7: Distance 2, Unit (Feet), Direction 2
        dist2 = float(form_data.get("sign_distance2", 2.002))
        self.distance2_unit_radio.click()
        self.kendo_dropdown.select_first_option("Direction2")

        # Step 8: Populate 'Sign will be located' numeric inputs via KendoNumericTextBox component
        self.kendo_numeric.set_value_by_id("signlocated", dist1)
        self.kendo_numeric.set_value_by_id("signlocated2", dist2)

        # Step 9: Distance range radio (100-199 ft)
        self.sign_distance_range_radio.click()
        return self

    def fill_property_owner_information(self, data: Optional[Dict[str, Any]] = None) -> "PrimaryHighwayPage":
        """Fills Property Owner Details step-by-step using test data."""
        self.logger.info("Filling Property Owner Information section")
        form_data = data or generate_primary_highway_test_data()
        self._wait_for_loader()

        # Step 1: Smoothly bring Property Owner section into view
        self.scroll_to_section(self.sec_property_owner)

        # Step 2: Fill text fields in order
        self.owner_name_input.fill(form_data.get("owner_name", "Sherrill Property LLC"))
        self.owner_address1_input.fill(form_data.get("owner_address", "100 Michigan Ave"))
        self.owner_city_input.fill(form_data.get("owner_city", "Chicago"))
        self.owner_zip_input.fill(form_data.get("owner_zip", "60601"))
        phone = form_data.get("owner_phone", "999-999-9999")
        try:
            self.owner_phone_input.fill(phone)
        except Exception:
            pass
        self.page.evaluate(
            f"""
            (() => {{
                if (window.$) {{
                    const mtb = $('#cmgenpoc_com_phone').data('kendoMaskedTextBox');
                    if (mtb) {{
                        mtb.value('{phone}');
                        mtb.trigger('change');
                    }}
                    $('#cmgenpoc_com_phone').val('{phone}').trigger('change');
                }}
            }})();
            """
        )
        if self.owner_email_input.is_visible(timeout=500):
            self.owner_email_input.fill(form_data.get("owner_email", "owner@example.com"))

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

        # Step 3: Signer Name and Title
        self.signer_name_input.fill(form_data.get("signer_name", "Kent Sherrill"))
        self.signer_title_input.fill(form_data.get("signer_title", "Authorized Representative"))

        # Step 4: Ensure date is set to present day via KendoDatePicker
        present_day = form_data.get("signature_date", "")
        if present_day:
            self.page.evaluate(
                f"""
                (() => {{
                    if (window.$) {{
                        $('input[name*="Date"], input[id*="Date"]').last().each(function() {{
                            const dp = $(this).data('kendoDatePicker');
                            if (dp) dp.value('{present_day}');
                            $(this).val('{present_day}').trigger('change');
                        }});
                    }}
                }})();
                """
            )
        return self

    def submit_application(self) -> "PrimaryHighwayPage":
        """Smoothly scrolls to and clicks the application Submit button."""
        self.logger.info("Submitting application...")
        self._wait_for_loader()

        try:
            self.submit_button.evaluate(
                "el => el.scrollIntoView({ behavior: 'smooth', block: 'center' })"
            )
            self.page.wait_for_timeout(200)
        except Exception:
            pass

        self.submit_button.click()
        return self

    def confirm_submission_modal(self) -> PaymentPage:
        """
        1st Page: Verifies the confirmation modal ('Record saved successfully') displays,
        clicks the 'OK' button, and returns the PaymentPage instance for the 2nd page flow.
        """
        self.logger.info("1st Page: Waiting for confirmation modal to display...")
        expect(self.modal_record_saved_text).to_be_visible(timeout=25000)
        expect(self.modal_confirm_button).to_be_visible(timeout=10000)
        self.logger.info("1st Page: 'Record saved successfully' confirmation modal is displayed")

        self.logger.info("Clicking OK button on confirmation modal...")
        self.modal_confirm_button.click()
        return PaymentPage(self.page)

    def wait_for_second_page_payment_gateway(self, timeout_ms: int = 40000) -> PaymentPage:
        """Waits for and delegates to PaymentPage on the 2nd page (Payment Gateway)."""
        payment = PaymentPage(self.page)
        payment.wait_for_payment_gateway(timeout_ms=timeout_ms)
        return payment

    def fill_payment_card_details(
        self,
        card_number: str = "4111111111111111",
        cvv: str = "111",
        name: str = "QA Tester",
        exp_month: str = "03",
        exp_year: str = "2029",
        zip_code: str = "60601",
    ) -> PaymentPage:
        """Delegates filling card details and clicking Next Step to PaymentPage."""
        payment = PaymentPage(self.page)
        payment.fill_card_details(
            card_number=card_number,
            cvv=cvv,
            name=name,
            exp_month=exp_month,
            exp_year=exp_year,
            zip_code=zip_code,
        )
        payment.click_next_step()
        return payment

    def submit_payment_and_verify_success(self, timeout_ms: int = 120000) -> PaymentPage:
        """Delegates final payment submission, survey dismissal, and return home to PaymentPage."""
        payment = PaymentPage(self.page)
        payment.submit_payment(timeout_ms=timeout_ms)
        payment.handle_survey_modal(respond=False)
        payment.click_return_home()
        return payment

    def submit_and_confirm_application(self, timeout_ms: int = 40000) -> PaymentPage:
        """
        Executes end-to-end permit application submission:
        1. Clicks Submit on permit application.
        2. 1st Page displays with confirmation modal ('Record saved successfully').
        3. User clicks on the 'OK' button.
        4. Transitions to PaymentPage and completes full payment gateway & return home flow.
        """
        self.submit_application()
        payment_page = self.confirm_submission_modal()
        payment_page.complete_payment_flow()
        return payment_page

    def submit_complete_primary_highway_application(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> None:
        """Executes full end-to-end submission for Business Area Sign - Primary Highway."""
        test_data = data or generate_primary_highway_test_data()
        self.navigate_to_primary_highway_application()
        self.fill_sign_information(test_data)
        self.fill_location_information(test_data)
        self.fill_property_owner_information(test_data)
        self.upload_proof_of_property(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        self.submit_and_confirm_application()
