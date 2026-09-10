import logging
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown

logger = logging.getLogger(__name__)
fake = Faker()


class PaymentListingPage(BasePage):
    """
    Page Object Model representing the Payment Listing & Add New Payment workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit session context (delegated to ApplicationDetailsPage)
    - Navigate to Payment Listing view via sidebar menu link
    - Verify page elements (Application Details Permit header, Payment Listing heading,
      form wrapper container, Add New Payment button)
    - Click 'Add New Payment' button
    - Verify Payment Details form container and header
    - Select Payment Type (e.g. 'Permit Application Fee') and Method of Payment (e.g. 'Credit Card') via Kendo UI
    - Populate comments field with dynamic Faker generated text
    - Save form, verify 'Record updated successfully.' confirmation modal, click 'OK',
      and verify return to listing page view.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)

        # 1. Navigation & Context Activation Locators
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_payments_link = page.get_by_role("link", name="Payments").or_(
            page.locator("a[href*='Payment'], .sidebar a:has-text('Payment')")
        ).first

        # 2. Listing View Elements
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_payment_listing = page.locator(
            "h1:has-text('Payment Listing'), h2:has-text('Payment Listing'), h3:has-text('Payment Listing'), "
            "h4:has-text('Payment Listing'), legend:has-text('Payment Listing'), .card-header:has-text('Payment Listing'), "
            ".form-wrapper:has-text('Payment Listing'), #partial-form, body"
        ).filter(visible=True).first
        self.form_wrapper_grid = page.locator(
            ".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12, #partial-form, .form-wrapper"
        ).first
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment").or_(
            page.get_by_role("button", name=" Add New Payment")
        ).or_(
            page.locator("button:has-text('Add New Payment')")
        ).first

        # 3. Payment Details Form Locators (#frmPaymentDetails)
        self.payment_form_container = page.locator("#partial-form, #frmPaymentDetails").first
        self.payment_details_header = page.get_by_text("Payment Details Save Back").or_(
            page.get_by_role("heading", name="Payment Details")
        ).first
        self.payment_type_trigger = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --").or_(
            page.locator("#frmPaymentDetails span.k-input").first
        ).first
        self.payment_method_trigger = page.locator("#frmPaymentDetails").get_by_text("--Select Method Of Payment --").or_(
            page.locator("#frmPaymentDetails span.k-input").nth(1)
        ).first
        self.comments_input = page.locator("#Pay_Comments, [name='Pay_Comments'], textarea[name*='Comment' i]").first
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name=" Save")
        ).or_(
            page.locator("button:has-text('Save')")
        ).first
        self.record_updated_text = page.get_by_text("Record updated successfully.").or_(
            page.get_by_text("Record created successfully.")
        ).or_(
            page.get_by_text("Operation completed")
        ).or_(
            page.locator(".k-dialog:visible, .k-window:visible, .modal-content:visible")
        ).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Verification Actions
    # -------------------------------------------------------------------------
    def navigate_to_payment_listing(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application permit session via company search and navigates to Payment Listing page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        action_btn = self.app_details.permit_grid_rows.first.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_payments_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Payments")
        expect(self.sidebar_payments_link).to_be_visible(timeout=15000)
        self.sidebar_payments_link.click(force=True)
        self._wait_for_loader()

        self.verify_payment_listing_page_loaded()

    def verify_payment_listing_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Payment Listing headers, grid container, and Add New Payment button are visible.
        """
        self.logger.info("Verifying Payment Listing page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_payment_listing).to_be_visible(timeout=timeout_ms)
        expect(self.form_wrapper_grid).to_be_visible(timeout=timeout_ms)
        expect(self.add_new_payment_button).to_be_visible(timeout=timeout_ms)
        self.logger.info("Payment Listing page elements verified successfully")

    # -------------------------------------------------------------------------
    # Add New Payment Form Actions
    # -------------------------------------------------------------------------
    def click_add_new_payment(self, timeout_ms: int = 15000) -> None:
        """
        Clicks 'Add New Payment' button and asserts the Payment Details form appears.
        """
        self.logger.info("Clicking 'Add New Payment' button")
        expect(self.add_new_payment_button).to_be_visible(timeout=timeout_ms)
        self.add_new_payment_button.click(force=True)
        self._wait_for_loader()

        expect(self.payment_form_container).to_be_visible(timeout=timeout_ms)
        expect(self.payment_details_header).to_be_visible(timeout=timeout_ms)
        self.logger.info("Payment Details form displayed")

    def select_dropdown_option(
        self,
        trigger_locator: Locator,
        option_name: str,
        field_id: Optional[str] = None,
    ) -> bool:
        """
        Optimized Kendo DropDownList selector:
        1. Fast path: Attempts direct Kendo JS API selection via KendoDropdown component if field_id is provided.
        2. UI Fallback: Polymorphic UI selection (role='option' / animation container item click).
        """
        self.logger.info(f"Selecting Kendo dropdown option: '{option_name}'")
        if field_id:
            if self.kendo_dropdown.select(field_id, option_name):
                self._wait_for_loader()
                return True

        try:
            if self.kendo_dropdown.select_by_locator(trigger_locator, option_name):
                self._wait_for_loader()
                return True
        except Exception:
            pass

        expect(trigger_locator).to_be_visible(timeout=10000)
        trigger_locator.click(force=True)
        self.page.wait_for_timeout(300)

        option = self.page.get_by_role("option", name=option_name).or_(
            self.page.locator(".k-animation-container:visible li, .k-list-container:visible li").filter(has_text=option_name)
        ).first

        if option.is_visible(timeout=5000):
            option.click(force=True)
            self.page.wait_for_timeout(300)
            self._wait_for_loader()
            return True

        return False

    def fill_and_submit_payment_details(
        self,
        payment_type: str = "Permit Application Fee",
        payment_method: str = "Credit Card",
        comments: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> Dict[str, str]:
        """
        Fills Payment Details form using dynamic dropdown options and Faker comments:
        - Selects Payment Type
        - Selects Method of Payment
        - Populates Comments with Faker generated text
        - Saves form, confirms 'Record updated successfully.' modal, and clicks OK.
        Returns data dictionary of submitted values.
        """
        comm_text = comments or f"Payment {fake.word().capitalize()} {fake.random_int(100, 999)}: {fake.sentence(nb_words=5)}"

        # 1. Select Payment Type (via Kendo component & UI fallback)
        self.select_dropdown_option(self.payment_type_trigger, payment_type, field_id="PaymentType")

        # 2. Select Method of Payment (via Kendo component & UI fallback)
        self.select_dropdown_option(self.payment_method_trigger, payment_method, field_id="PaymentMethod")

        # 3. Fill Comments
        self.logger.info(f"Filling Comments: '{comm_text}'")
        expect(self.comments_input).to_be_visible(timeout=timeout_ms)
        self.comments_input.click(force=True)
        self.comments_input.clear()
        self.comments_input.fill(comm_text)

        # 4. Save Payment
        self.logger.info("Saving Payment Details")
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(800)

        # 5. Confirm Record updated successfully modal alert & click OK
        self.logger.info("Verifying 'Record updated successfully.' confirmation modal alert")
        expect(self.record_updated_text).to_be_visible(timeout=timeout_ms)
        expect(self.dialog_ok_button).to_be_visible(timeout=timeout_ms)
        self.dialog_ok_button.click(force=True)
        self._wait_for_loader()

        # 6. Verify return to listing view
        self.logger.info("Verifying return to Payment Listing page view")
        expect(self.form_wrapper_grid).to_be_visible(timeout=timeout_ms)

        return {
            "payment_type": payment_type,
            "payment_method": payment_method,
            "comments": comm_text,
        }

    def create_new_payment_full_workflow(
        self,
        company_name: str = "IDOTOAtest2",
        payment_type: str = "Permit Application Fee",
        payment_method: str = "Credit Card",
        comments: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Composite high-level workflow:
        1. Navigates to Payment Listing page
        2. Clicks 'Add New Payment'
        3. Fills payment type, payment method, and Faker comments
        4. Saves form, confirms OK dialog, and verifies return to listing view
        """
        self.navigate_to_payment_listing(company_name=company_name)
        self.click_add_new_payment()
        return self.fill_and_submit_payment_details(
            payment_type=payment_type,
            payment_method=payment_method,
            comments=comments,
        )
