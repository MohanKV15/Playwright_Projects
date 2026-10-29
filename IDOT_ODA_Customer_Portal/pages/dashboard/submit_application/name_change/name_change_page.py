import logging
import re
from typing import Dict, Any, Optional
from playwright.sync_api import Page, expect
from faker import Faker
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Customer_Portal.testdata import generate_name_change_test_data

logger = logging.getLogger(__name__)
fake = Faker()


class NameChangePage(BasePage):
    """
    Page Object Model representing the Customer Portal: Name Change Application workflow.

    Encapsulates:
    - Navigation from Dashboard to Name Change form
    - Section verification (partial form, Application Details, Signature)
    - Dynamic form filling using Faker (#NewName, #SignName, #SignTitle)
    - Kendo checkbox certification and Kendo button submission
    - Modal confirmation and post-submission return home navigation
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation Locators
        self.submit_app_dashboard_btn = page.locator("#btnSubmitApp").first
        self.name_change_card = page.get_by_text("Name Change Submit a new", exact=False).first
        self.name_change_btn = page.locator("#btnNameChange")
        self.name_change_heading = page.get_by_role(
            "heading", name=re.compile(r"Name Change Application", re.I)
        ).or_(page.locator("text=Name Change Application")).first

        # 2. Section Verification Locators
        self.partial_form = page.locator("#partial-form")
        self.sec_application_details = page.get_by_text("Application Details Current", exact=False).first
        self.sec_signature = page.get_by_text("Signature * I certify all the", exact=False).first

        # 3. Form Input Locators
        self.new_name_input = page.locator("#NewName")
        self.signature_checkbox = page.locator(".k-checkbox-label").first
        self.signer_name_input = page.locator("#SignName")
        self.signer_title_input = page.locator("#SignTitle")

        # 4. Action & Post-submission Locators
        self.submit_button = page.get_by_role("button", name=re.compile(r"Submit", re.I))
        self.modal_operation_completed = page.get_by_text("Operation Completed", exact=False).first
        self.modal_ok_btn = page.get_by_role("button", name=re.compile(r"^OK$", re.I)).first
        self.modal_survey_prompt = page.get_by_text("Would you like to respond to", exact=False).first
        self.modal_survey_no_btn = page.get_by_role("button", name=re.compile(r"^No$", re.I)).first
        self.success_container = page.locator("div").filter(has_text="Successful Application has").first
        self.return_home_btn = page.get_by_role("button", name=re.compile(r"Return Home", re.I)).first
        self.dashboard_marker = page.locator("#btnSubmitApp").first

    # -----------------------------------------------------------------
    # Navigation Methods
    # -----------------------------------------------------------------
    def navigate_to_name_change(self) -> "NameChangePage":
        """Navigates from Dashboard to the Name Change application form."""
        self.logger.info("Navigating to Name Change Application Form")
        self._wait_for_loader(timeout=30000)

        if "CALanding" in self.page.url or "Account" in self.page.url:
            try:
                self.page.wait_for_url(
                    re.compile(r"CADashboardFull|4321CustomerPortalDashboardFull"),
                    timeout=20000,
                )
            except Exception:
                self.page.goto(f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull", wait_until="domcontentloaded")

        self._wait_for_loader(timeout=30000)
        if self.name_change_heading.is_visible(timeout=1500):
            return self

        expect(self.submit_app_dashboard_btn).to_be_visible(timeout=35000)
        self.submit_app_dashboard_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.name_change_card).to_be_visible(timeout=30000)
        expect(self.name_change_btn).to_be_visible(timeout=30000)
        self.name_change_btn.click()
        self._wait_for_loader(timeout=30000)

        expect(self.name_change_heading).to_be_visible(timeout=35000)
        self.verify_form_sections()
        self.logger.info("Successfully navigated to Name Change Application Form")
        return self

    def verify_form_sections(self, timeout_ms: int = 15000) -> "NameChangePage":
        """Asserts visibility of key form sections: partial-form, Application Details, and Signature."""
        self.logger.info("Verifying all key sections are displayed on Name Change form")
        expect(self.partial_form).to_be_visible(timeout=timeout_ms)
        expect(self.sec_application_details).to_be_visible(timeout=timeout_ms)
        expect(self.sec_signature).to_be_visible(timeout=timeout_ms)
        return self

    # -----------------------------------------------------------------
    # Form Filling Methods
    # -----------------------------------------------------------------
    def fill_new_company_name(self, new_name: Optional[str] = None) -> "NameChangePage":
        """Fills New Company Name (#NewName) using dynamic Faker data."""
        val_name = new_name or f"{fake.company()[:20]} LLC"
        self.logger.info(f"Filling New Company Name: '{val_name}' via #NewName")
        self._wait_for_loader()
        self.new_name_input.scroll_into_view_if_needed()
        self.new_name_input.click()
        self.new_name_input.fill(val_name)
        return self

    def check_signature_certification(self) -> "NameChangePage":
        """Checks the Signature certification checkbox."""
        self.logger.info("Checking Signature certification checkbox")
        self.scroll_to_section(self.sec_signature)
        try:
            self.signature_checkbox.scroll_into_view_if_needed()
            self.signature_checkbox.click()
        except Exception:
            self.check_kendo_checkbox(self.signature_checkbox)
        return self

    def fill_signature(self, name: Optional[str] = None, title: Optional[str] = None) -> "NameChangePage":
        """Fills Signer Name (#SignName) and Title (#SignTitle) matching recorded codegen."""
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

    def fill_complete_name_change_form(self, data: Optional[Dict[str, Any]] = None) -> "NameChangePage":
        """Fills entire Name Change application form sequentially."""
        form_data = data or generate_name_change_test_data()
        self.fill_new_company_name(form_data.get("new_name"))
        self.check_signature_certification()
        self.fill_signature(name=form_data.get("signer_name"), title=form_data.get("signer_title"))
        return self

    # -----------------------------------------------------------------
    # Submission, Confirmation Modals & Return Home
    # -----------------------------------------------------------------
    def submit_application(self) -> "NameChangePage":
        """Submits application by clicking ' Submit' button."""
        self.logger.info("Submitting Name Change application")
        self.submit_button.scroll_into_view_if_needed()
        self.submit_button.click()
        return self

    def confirm_operation_completed_modal(self, timeout_ms: int = 15000) -> "NameChangePage":
        """Asserts 'Operation Completed' modal is visible and clicks 'OK'."""
        self.logger.info("Verifying 'Operation Completed' modal and clicking 'OK'")
        expect(self.modal_operation_completed).to_be_visible(timeout=timeout_ms)
        self.modal_ok_btn.click()
        return self

    def dismiss_survey_modal(self, timeout_ms: int = 15000) -> "NameChangePage":
        """Asserts survey modal ('Would you like to respond to...') is visible and clicks 'No'."""
        self.logger.info("Verifying survey modal and clicking 'No'")
        expect(self.modal_survey_prompt).to_be_visible(timeout=timeout_ms)
        self.modal_survey_no_btn.click()
        return self

    def click_return_home(self, timeout_ms: int = 20000) -> None:
        """Asserts success message and clicks ' Return Home' back to Dashboard."""
        self.logger.info("Verifying Successful page and clicking 'Return Home'")
        expect(self.success_container).to_be_visible(timeout=timeout_ms)
        self.return_home_btn.click()
        expect(self.dashboard_marker).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Successfully returned to Dashboard. Current URL: {self.page.url}")

    def submit_and_confirm_name_change(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Executes full end-to-end Name Change workflow from navigation to return home."""
        self.navigate_to_name_change()
        self.fill_complete_name_change_form(data=data)
        self.submit_application()
        self.confirm_operation_completed_modal()
        self.dismiss_survey_modal()
        self.click_return_home()
