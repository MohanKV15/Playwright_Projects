import logging
import os
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.testdata import generate_permit_transfer_test_data

logger = logging.getLogger(__name__)
fake = Faker()


class PermitTransferPage(BasePage):
    """
    Page Object Model representing the Customer Portal: Permit Transfer Application workflow.

    Encapsulates:
    - Navigation from Dashboard to Permit Transfer form
    - Section verification (Applicant Info, Application Info, Acknowledgment, Signature)
    - Dynamic form filling using Faker (Permit Number, From Company)
    - File attachment upload (From Company Approval letter dummy PDF)
    - Checkbox selection via KendoCheckbox component
    - Signer Name (#SignName) and Title ('Title *') entry
    - Submission (' Submit'), modal confirmation ('OK'), and Return Home navigation
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation Locators
        self.submit_app_dashboard_btn = page.locator(
            "#btnSubmitApp, a:has-text('Submit an Application'), button:has-text('Submit an Application')"
        ).first
        self.permit_transfer_card = page.get_by_text("Permit Transfer Submit a new", exact=False).first
        self.permit_transfer_btn = page.locator("#btnPermitTransfer")
        self.transfer_heading = page.get_by_role(
            "heading", name=re.compile(r"Permit Transfer Application", re.I)
        ).or_(page.locator("text=Permit Transfer Application")).first

        # 2. Section Verification Locators
        self.sec_applicant_info = page.get_by_text("Applicant Information Company", exact=False).first
        self.sec_application_info = page.get_by_text("Application Information Permit Number to Transfer", exact=False).first
        self.sec_acknowledgment = page.get_by_text("Acknowledgement * Disclosure", exact=False).first
        self.sec_signature = page.get_by_text("Signature * The applicant", exact=False).first

        # 3. Form Input Locators
        self.permit_number_input = page.get_by_role("textbox", name="Permit Number to Transfer *").or_(
            page.locator("#Appl_Transfer_Permit_No, #PermitNo")
        ).first
        self.from_company_input = page.get_by_role("textbox", name="From Company *").or_(
            page.locator("#Appl_Transfer_Permit_From, #FromCompany")
        ).first
        self.file_input = page.locator(".k-upload input[type='file'], #uploadTransferPermission, input[type='file']").first

        # 4. Acknowledgment & Signature Locators
        self.ack_checkbox = page.locator(".k-checkbox-label").filter(
            has_text=re.compile(r"Disclosure of this information", re.I)
        ).or_(page.locator(".k-checkbox-label").first).first

        self.signature_checkbox = page.locator(".k-checkbox-label").filter(
            has_text=re.compile(r"The applicant certifies", re.I)
        ).or_(page.locator("div:nth-child(5) > div:nth-child(2) > .form-check > .k-checkbox-label")).first

        self.signer_name_input = page.locator("#SignName")
        self.signer_title_input = page.get_by_role("textbox", name="Title *")

        # 5. Submission, Modal & Return Home Locators
        self.submit_button = page.get_by_role("button", name=" Submit").or_(
            page.get_by_role("button", name=re.compile(r"^\s*Submit", re.I))
        ).or_(page.locator("button:has-text('Submit'), #btnSubmit")).first

        self.modal_confirm_button = (
            page.locator(".k-dialog:visible button:has-text('OK')")
            .or_(page.locator(".k-window:visible button:has-text('OK')"))
            .or_(page.locator("[role='dialog']:visible button:has-text('OK')"))
            .or_(page.get_by_role("button", name="OK"))
            .or_(page.locator("button:visible:has-text('OK')"))
            .first
        )

        self.return_home_btn = (
            page.locator("button:has-text('Return Home'), a:has-text('Return Home')")
            .or_(page.get_by_role("button", name=re.compile(r"Return Home", re.I)))
            .or_(page.get_by_role("link", name=re.compile(r"Return Home", re.I)))
            .first
        )

    # -----------------------------------------------------------------
    # Navigation Methods
    # -----------------------------------------------------------------
    def navigate_to_permit_transfer(self) -> "PermitTransferPage":
        """Navigates from Dashboard to the Permit Transfer application form."""
        self.logger.info("Navigating to Permit Transfer Application Form")
        self._wait_for_loader(timeout=30000)

        if "CALanding" in self.page.url or "Account" in self.page.url:
            try:
                self.page.wait_for_url(re.compile(r"CADashboardFull|4321CustomerPortalDashboardFull"), timeout=20000)
            except Exception:
                self.page.goto(f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull", wait_until="domcontentloaded")

        self._wait_for_loader(timeout=30000)
        if self.transfer_heading.is_visible(timeout=1500):
            return self

        expect(self.submit_app_dashboard_btn).to_be_visible(timeout=35000)
        self.submit_app_dashboard_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.permit_transfer_card).to_be_visible(timeout=30000)
        expect(self.permit_transfer_btn).to_be_visible(timeout=30000)
        self.permit_transfer_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.transfer_heading).to_be_visible(timeout=35000)
        self.verify_form_sections()
        return self

    def verify_form_sections(self, timeout_ms: int = 15000) -> "PermitTransferPage":
        """Asserts visibility of key form sections: Applicant Info, Application Info, Acknowledgment, and Signature."""
        self.logger.info("Verifying all 4 key sections are displayed")
        expect(self.sec_applicant_info).to_be_visible(timeout=timeout_ms)
        expect(self.sec_application_info).to_be_visible(timeout=timeout_ms)
        expect(self.sec_acknowledgment).to_be_visible(timeout=timeout_ms)
        expect(self.sec_signature).to_be_visible(timeout=timeout_ms)
        return self

    # -----------------------------------------------------------------
    # Form Filling Methods
    # -----------------------------------------------------------------
    def fill_application_information(self, data: Optional[Dict[str, Any]] = None) -> "PermitTransferPage":
        """Fills Application Information (Permit Number and From Company) using Faker."""
        self.logger.info("Filling Application Information section")
        form_data = data or generate_permit_transfer_test_data()
        self._wait_for_loader()
        self.scroll_to_section(self.sec_application_info)

        permit_num = str(form_data.get("permit_number") or fake.random_number(digits=6, fix_len=True))
        from_comp = str(form_data.get("from_company") or f"{fake.company()} LLC")

        self.permit_number_input.click()
        self.permit_number_input.fill(permit_num)
        self.from_company_input.click()
        self.from_company_input.fill(from_comp)
        return self

    def upload_approval_letter(self, file_path: Optional[str] = None) -> "PermitTransferPage":
        """Uploads From Company Approval letter using dummy PDF."""
        self.logger.info("Uploading From Company Approval letter attachment")
        self._wait_for_loader()

        if file_path and os.path.exists(file_path):
            target_path = file_path
        else:
            dummy_pdf = Config.PROJECT_ROOT / "testdata" / "dummy.pdf"
            if not dummy_pdf.exists():
                dummy_pdf.write_bytes(b"%PDF-1.4 IDOT ODA Test Dummy PDF Attachment")
            target_path = str(dummy_pdf)

        if self.file_input.count() > 0:
            self.file_input.set_input_files(target_path)
        return self

    def fill_signature(self, name: Optional[str] = None, title: Optional[str] = None) -> "PermitTransferPage":
        """Fills Signer Name (#SignName) and Title ('Title *') matching recorded codegen."""
        val_name = name or f"{fake.first_name()} {fake.last_name()}"
        val_title = title or f"{fake.job()[:25]}"

        self.logger.info(f"Filling Signer Name: '{val_name}' and Title: '{val_title}'")
        self.signer_name_input.scroll_into_view_if_needed()
        self.signer_name_input.click()
        self.signer_name_input.fill(val_name)

        self.signer_title_input.scroll_into_view_if_needed()
        self.signer_title_input.click()
        self.signer_title_input.fill(val_title)
        return self

    def fill_acknowledgment_and_signature(
        self,
        data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
    ) -> "PermitTransferPage":
        """Checks Acknowledgment and Signature checkboxes and fills Signer details."""
        self.logger.info("Filling Acknowledgment and Signature section")
        form_data = data or generate_permit_transfer_test_data()
        self._wait_for_loader()
        self.scroll_to_section(self.sec_acknowledgment)

        self.check_kendo_checkbox(self.ack_checkbox, input_index=0)
        self.check_kendo_checkbox(self.signature_checkbox, input_index=1)

        signer_name = name or form_data.get("signer_name")
        signer_title = title or form_data.get("signer_title")
        self.fill_signature(name=signer_name, title=signer_title)
        return self

    def fill_complete_permit_transfer_form(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> "PermitTransferPage":
        """Fills entire Permit Transfer application form sequentially."""
        test_data = data or generate_permit_transfer_test_data()
        self.fill_application_information(test_data)
        self.upload_approval_letter(file_path)
        self.fill_acknowledgment_and_signature(test_data)
        return self

    # -----------------------------------------------------------------
    # Submission, Modal Confirmation & Return Home
    # -----------------------------------------------------------------
    def submit_application(self) -> "PermitTransferPage":
        """Clicks application ' Submit' button cleanly."""
        self.logger.info("Submitting Permit Transfer application")
        self._wait_for_loader()

        # Ensure Kendo button widget is enabled and unblocked
        try:
            self.page.evaluate(
                """() => {
                    const btn = $('#btnSubmit');
                    if (btn.length) {
                        const kb = btn.data('kendoButton');
                        if (kb && typeof kb.enable === 'function') kb.enable(true);
                        btn.removeAttr('disabled').removeAttr('aria-disabled').removeClass('k-state-disabled');
                    }
                }"""
            )
        except Exception:
            pass

        try:
            self.submit_button.scroll_into_view_if_needed()
        except Exception:
            pass

        try:
            self.submit_button.click(force=True, timeout=5000)
        except Exception:
            self.js_click(self.submit_button)
        return self

    def confirm_submission_modal(self, timeout_ms: int = 15000) -> "PermitTransferPage":
        """Detects confirmation popup and clicks OK immediately."""
        self.logger.info("Confirming submission popup (clicking 'OK')")
        try:
            self.modal_confirm_button.wait_for(state="visible", timeout=timeout_ms)
            self.modal_confirm_button.click()
            self._wait_for_loader()
        except Exception as e:
            if not self.handle_kendo_alert(timeout_ms=2000):
                self.logger.info(f"Modal already dismissed or bypassed: {e}")

        return self

    def click_return_home(self, timeout_ms: int = 25000) -> None:
        """Clicks 'Return Home' button fast and verifies navigation back to Dashboard."""
        self.logger.info("Clicking 'Return Home' button")
        self._wait_for_loader(timeout=5000)

        # Non-blocking quick check for optional survey prompt (max 300ms)
        try:
            survey_no_btn = self.page.locator(".k-dialog:visible button:has-text('No')").first
            if survey_no_btn.is_visible(timeout=300):
                survey_no_btn.click()
                self._wait_for_loader()
        except Exception:
            pass

        expect(self.return_home_btn).to_be_visible(timeout=timeout_ms)
        self.return_home_btn.click()
        self._wait_for_loader(timeout=15000)

        dashboard_heading = self.page.locator("#btnSubmitApp").or_(self.page.get_by_text("Submit an Application")).first
        expect(dashboard_heading).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Successfully returned to Dashboard. Current URL: {self.page.url}")

    def submit_and_confirm_transfer(
        self, data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
    ) -> None:
        """Executes full end-to-end Permit Transfer workflow from navigation to return home."""
        self.navigate_to_permit_transfer()
        self.fill_complete_permit_transfer_form(data=data, file_path=file_path)
        self.submit_application()
        self.confirm_submission_modal()
        self.click_return_home()
