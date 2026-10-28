import logging
import os
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, Locator, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage
from IDOT_ODA_Customer_Portal.testdata import TestDataFactory

logger = logging.getLogger(__name__)
fake = Faker()


class BasePermitApplicationPage(BasePage):
    """
    Base Page Object Model representing common workflows across all IDOT ODA Permit Applications.
    Encapsulates:
    - Permit menu navigation
    - Cascading District / County / Route dropdown selections (always 1st option)
    - Property Owner details with dynamic Faker data
    - Attachment file uploads
    - Acknowledgment and signature form filling
    - Submission, record saved confirmation modals, and PaymentPage transitions
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # 1. Navigation Locators
        # -------------------------------------------------------------
        self.submit_app_dashboard_btn = page.locator(
            "#btnSubmitApp, a:has-text('Submit an Application'), button:has-text('Submit an Application')"
        ).first
        self.permit_app_btn = page.locator("#btnPermitApp")
        self.application_list_heading = page.get_by_role(
            "heading", name=re.compile(r"Application List", re.I)
        )

        # -------------------------------------------------------------
        # 2. Section Headers (Used for steady scrolling progression)
        # -------------------------------------------------------------
        self.sec_property_owner = page.locator("text=Property Owner Information").first
        self.sec_attachments = page.locator("text=Attachments").first
        self.sec_signature = page.locator("text=Signature").first

        # -------------------------------------------------------------
        # 3. Property Owner Information Locators
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
        # 4. Attachment Locators
        # -------------------------------------------------------------
        self.file_input = page.locator("#uploadOwnerPermission, input[type='file']").first

        # -------------------------------------------------------------
        # 5. Acknowledgment & Signature Locators
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
        # 6. Submission & Confirmation Modal Locators
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
    # Navigation Methods
    # -----------------------------------------------------------------
    def navigate_to_permit_application_menu(self) -> None:
        """
        Navigates from Dashboard to the Permit Application card selection menu.
        Resilient against post-login redirection delays and staging latency.
        """
        self._wait_for_loader(timeout=30000)

        # Handle post-login transitional pages (CALandingFull / AccountAccess)
        if "CALanding" in self.page.url or "Account" in self.page.url:
            try:
                self.page.wait_for_url(
                    re.compile(r"CADashboardFull|4321CustomerPortalDashboardFull"),
                    timeout=20000,
                )
            except Exception:
                self.logger.warning("Landing redirect delayed; navigating directly to CADashboardFull")
                self.page.goto(f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull", wait_until="domcontentloaded")

        self._wait_for_loader(timeout=30000)

        # Ensure dashboard card has rendered; retry navigation if page was stuck
        try:
            self.submit_app_dashboard_btn.wait_for(state="visible", timeout=15000)
        except Exception:
            self.logger.warning("Submit Application card not visible after 15s; refreshing Dashboard")
            self.page.goto(f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull", wait_until="domcontentloaded")
            self._wait_for_loader(timeout=30000)

        expect(self.submit_app_dashboard_btn).to_be_visible(timeout=35000)
        self.submit_app_dashboard_btn.click()
        self._wait_for_loader(timeout=30000)

        if not self.permit_app_btn.is_visible():
            try:
                self.submit_app_dashboard_btn.click(force=True)
                self._wait_for_loader(timeout=30000)
            except Exception:
                pass

        expect(self.permit_app_btn).to_be_visible(timeout=30000)
        self.permit_app_btn.click()
        self._wait_for_loader(timeout=30000)

    # -----------------------------------------------------------------
    # Common Cascading Location Dropdowns (Always 1st Option)
    # -----------------------------------------------------------------
    def fill_district_county_route(
        self,
        district_id: str = "EP_Permit_Application_District",
        county_id: str = "EP_Permit_Application_County",
        route_id: str = "EP_Permit_Application_Route",
    ) -> None:
        """
        Selects the 1st valid option across cascading location dropdowns:
        District -> County -> Route.
        """
        self.logger.info(f"Selecting 1st dropdown options for District ({district_id}), County ({county_id}), Route ({route_id})")
        self.kendo_dropdown.select_first_option(district_id)
        self.page.wait_for_timeout(500)
        self.kendo_dropdown.select_first_option(county_id)
        self.page.wait_for_timeout(500)
        self.kendo_dropdown.select_first_option(route_id)

    # -----------------------------------------------------------------
    # Common Property Owner Details (Dynamic Faker Data)
    # -----------------------------------------------------------------
    def fill_property_owner_information(self, data: Optional[Dict[str, Any]] = None) -> "BasePermitApplicationPage":
        """Fills Property Owner Details using dynamic Faker data with zero hardcoding."""
        self.logger.info("Filling Property Owner Information section with dynamic Faker data")
        form_data = data or {}
        self._wait_for_loader()

        self.scroll_to_section(self.sec_property_owner)

        owner_name = form_data.get("owner_name") or fake.company()
        owner_address = form_data.get("owner_address") or fake.street_address()
        owner_city = form_data.get("owner_city") or fake.city()
        owner_zip = form_data.get("owner_zip") or fake.zipcode()[:5]
        phone = form_data.get("owner_phone") or TestDataFactory.us_phone()
        owner_email = form_data.get("owner_email") or fake.email()

        self.owner_name_input.fill(owner_name)
        self.owner_address1_input.fill(owner_address)
        self.owner_city_input.fill(owner_city)

        # Select State dropdown 1st option if present
        if self.prop_owner_state_dropdown.is_visible(timeout=500):
            self.kendo_dropdown.select_first_option(self.prop_owner_state_dropdown)

        self.owner_zip_input.fill(owner_zip)

        if self.owner_phone_input.is_visible(timeout=1000):
            try:
                self.owner_phone_input.scroll_into_view_if_needed()
                self.kendo_masked.set_value(self.owner_phone_input, phone)
            except Exception:
                self.owner_phone_input.fill(phone)

        if self.owner_email_input.is_visible(timeout=500):
            self.owner_email_input.fill(owner_email)

        self.ownership_lease_radio.click()
        return self

    # -----------------------------------------------------------------
    # Common Attachments
    # -----------------------------------------------------------------
    def upload_proof_of_property(self, file_path: Optional[str] = None) -> "BasePermitApplicationPage":
        """Uploads a PDF file for Proof of Property / Land attachment."""
        self.logger.info("Uploading Proof of Property attachment")
        self._wait_for_loader()

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

    # -----------------------------------------------------------------
    # Common Acknowledgment & Signature (Dynamic Faker Data)
    # -----------------------------------------------------------------
    def fill_acknowledgment_and_signature(self, data: Optional[Dict[str, Any]] = None) -> "BasePermitApplicationPage":
        """Checks Acknowledgment and Signature checkboxes and fills Signer details using Faker."""
        self.logger.info("Filling Acknowledgment and Signature section")
        form_data = data or {}
        self._wait_for_loader()

        self.scroll_to_section(self.sec_signature)

        self.acknowledgment_checkbox.click()
        self.signature_checkbox.click()

        signer_name = form_data.get("signer_name") or f"{fake.first_name()} {fake.last_name()}"
        signer_title = form_data.get("signer_title") or f"{fake.job()[:25]}"

        self.signer_name_input.fill(signer_name)
        self.signer_title_input.fill(signer_title)

        # Ensure date is set to present day (portal pre-fills SigDate automatically in readonly)
        present_day = form_data.get("signature_date") or TestDataFactory.today()
        current_val = self.page.evaluate(
            "() => { const el = document.getElementById('SigDate'); return el ? el.value : ''; }"
        )
        if not current_val:
            self.kendo_datepicker.set_date_by_id("SigDate", present_day)

        return self

    # -----------------------------------------------------------------
    # Common Submission & Confirmation Modal
    # -----------------------------------------------------------------
    def submit_application(self) -> "BasePermitApplicationPage":
        """Smoothly scrolls to and clicks the application Submit button."""
        self.logger.info("Submitting application...")
        self._wait_for_loader()
        try:
            self.submit_button.evaluate("el => el.scrollIntoView({ behavior: 'smooth', block: 'center' })")
        except Exception:
            pass

        self.submit_button.click()
        self._wait_for_loader(timeout=25000)

        # Direct success page redirect check (e.g. CASuccessPageFull)
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
        clicks the 'OK' button, and returns the PaymentPage instance.
        If already redirected to CASuccessPageFull, transitions directly.
        """
        self.logger.info("Checking confirmation modal or success redirection...")
        if "casuccesspagefull" in self.page.url.lower():
            self.logger.info("Already arrived at CASuccessPageFull (direct submission without modal)")
            return PaymentPage(self.page)

        try:
            self.modal_record_saved_text.wait_for(state="visible", timeout=15000)
            self.logger.info("Confirmation modal ('Record saved successfully') displayed. Clicking OK...")
            self.modal_confirm_button.click()
            self._wait_for_loader()
        except Exception as e:
            self.logger.info(f"Confirmation modal bypassed or already dismissed: {e}")

        return PaymentPage(self.page)

    def submit_and_confirm_application(self, timeout_ms: int = 40000) -> PaymentPage:
        """
        Executes end-to-end permit application submission:
        1. Clicks Submit on permit application.
        2. Confirms 'Record saved successfully' modal if displayed.
        3. Completes PaymentPage flow.
        """
        self.submit_application()
        payment_page = self.confirm_submission_modal()
        payment_page.complete_payment_flow()
        return payment_page

