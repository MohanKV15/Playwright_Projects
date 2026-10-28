import logging
import re
from typing import Optional
from playwright.sync_api import Page, Locator, expect
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class PaymentPage(BasePage):
    """
    Page Object Model representing the Payment Gateway (CollectorSolutions / Magic-UI)
    and post-payment confirmation workflow (Survey modal & Return Home).
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # -------------------------------------------------------------
        # 1. Payment Gateway Page Indicators
        # -------------------------------------------------------------
        self.gateway_heading = (
            page.get_by_text("Make A Payment", exact=False)
            .or_(page.get_by_text("Payment Notice", exact=False))
            .or_(page.get_by_text("Payment Information", exact=False))
            .first
        )
        self.payment_notice_text = page.get_by_text("Payment Notice", exact=False).first
        self.payment_info_tab = page.get_by_text("Payment Information", exact=False).first
        self.cart_info_tab = page.get_by_text("Cart Information", exact=False).first

        # -------------------------------------------------------------
        # 2. Credit Card Form Fields (Magic-UI & standard #CC IDs)
        # -------------------------------------------------------------
        self.name_on_card_input = page.locator(
            "#CCNameOnCard, #NameOnCard, input[name='NameOnCard']"
        ).first
        self.card_number_input = page.locator(
            "#CCCardNumber, #maskedCardNumber, #CardNumber, input[name='maskedCardNumber']"
        ).first
        self.exp_month_select = page.locator(
            "#CCExpirationMonth, #ExpirationMonth, select[name='ExpirationMonth']"
        ).first
        self.exp_year_select = page.locator(
            "#CCExpirationYear, #ExpirationYear, select[name='ExpirationYear']"
        ).first
        self.cvv_input = page.locator(
            "#CCCardCVV, #CVV2, #CVV, input[name='CVV2']"
        ).first
        self.card_zip_input = page.locator(
            "#CardBillingPostalCode, #CCCardZip, #CCZipCode, #CCZip, input[name='CardBillingPostalCode']"
        ).first

        # -------------------------------------------------------------
        # 3. Action Buttons on Payment Gateway
        # -------------------------------------------------------------
        self.next_step_review_btn = page.locator(
            "#bntNextPaymentInfo, button:has-text('Next Step: Review Payment'), button:has-text('Review Payment'), input[value*='Review Payment']"
        ).first
        self.submit_payment_btn = page.locator(
            "#submitPayment, button:has-text('Submit Payment'), button:has-text('Pay'), button:has-text('Confirm'), button:has-text('Make Payment'), input[value*='Submit']"
        ).first

        # -------------------------------------------------------------
        # 4. Success Page, Survey Modal & Return Home Locators
        # -------------------------------------------------------------
        self.success_heading = page.get_by_text("Successful", exact=False).first
        self.application_number_text = page.locator("text=/Your application number is/i").first

        # Survey popup modal
        self.survey_modal_heading = page.locator("text=Outdoor Advertising System").first
        self.survey_modal_text = page.locator("text=Would you like to respond to survey?").first
        self.survey_no_btn = page.locator(
            "button:has-text('No'), a.k-button:has-text('No'), .k-dialog-actions button, button.k-button"
        ).filter(has_text=re.compile(r"^No$", re.I)).first
        self.survey_yes_btn = page.locator(
            "button:has-text('Yes'), a.k-button:has-text('Yes'), .k-dialog-actions button, button.k-button"
        ).filter(has_text=re.compile(r"^Yes$", re.I)).first

        # Return Home button on CASuccessPageFull
        self.return_home_btn = (
            page.get_by_role("button", name=re.compile(r"Return Home", re.I))
            .or_(page.get_by_role("link", name=re.compile(r"Return Home", re.I)))
            .or_(page.locator("a:has-text('Return Home'), button:has-text('Return Home')"))
            .first
        )

    # -----------------------------------------------------------------
    # Payment Gateway Methods
    # -----------------------------------------------------------------
    def wait_for_payment_gateway(self, timeout_ms: int = 40000) -> "PaymentPage":
        """Waits for redirection and verifies that the Payment Gateway page is displayed."""
        self.logger.info("Waiting for Payment Gateway page to load...")
        if "casuccesspagefull" in self.page.url.lower() or self.success_heading.is_visible(timeout=2000):
            self.logger.info("Application has no fee: already on CASuccessPageFull")
            return self

        expect(self.page).to_have_url(
            re.compile(
                r".*(collectorsolutions\.com|magic-ui|Pay|Process|PaymentMethod|Checkout|Payment|CASuccessPageFull).*",
                re.I,
            ),
            timeout=timeout_ms,
        )

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

        if "casuccesspagefull" in self.page.url.lower():
            return self

        expect(self.gateway_heading).to_be_visible(timeout=25000)
        self.logger.info(f"Payment Gateway displayed successfully: {self.page.url}")
        return self

    def fill_card_details(
        self,
        card_number: str = "4111111111111111",
        cvv: str = "111",
        name: str = "QA Tester",
        exp_month: str = "03",
        exp_year: str = "2029",
        zip_code: str = "60601",
    ) -> "PaymentPage":
        """Fills payment card details on Payment Gateway form."""
        self.logger.info("Filling credit card details on Payment Gateway...")

        expect(self.name_on_card_input).to_be_visible(timeout=20000)
        self.name_on_card_input.fill(name)
        self.card_number_input.fill(card_number)
        self.exp_month_select.select_option(exp_month)
        self.exp_year_select.select_option(exp_year)
        self.cvv_input.fill(cvv)

        try:
            if self.card_zip_input.is_visible(timeout=500):
                self.card_zip_input.fill(zip_code)
        except Exception:
            pass

        return self

    def click_next_step(self) -> "PaymentPage":
        """Clicks 'Next Step: Review Payment' button to proceed to review step."""
        self.logger.info("Clicking 'Next Step: Review Payment' button...")
        expect(self.next_step_review_btn).to_be_visible(timeout=15000)
        self.next_step_review_btn.click()
        return self

    def submit_payment(self, timeout_ms: int = 120000) -> "PaymentPage":
        """
        Submits the final payment on the review step and waits for redirection
        back to the Customer Portal success page.
        """
        self.logger.info("Submitting final payment on review screen...")
        expect(self.submit_payment_btn).to_be_visible(timeout=25000)
        self.submit_payment_btn.scroll_into_view_if_needed()
        self.submit_payment_btn.click()

        self.logger.info("Payment submitted. Waiting for redirect to CASuccessPageFull...")
        self.page.wait_for_url(
            re.compile(r".*(CASuccessPageFull|Success|Return|bemcorp\.net).*", re.I),
            timeout=timeout_ms,
        )
        self.logger.info(f"Redirected back to portal: {self.page.url}")
        return self

    # -----------------------------------------------------------------
    # Post-Payment: Survey Modal & Return Home Methods
    # -----------------------------------------------------------------
    def handle_survey_modal(self, respond: bool = False, timeout_ms: int = 15000) -> "PaymentPage":
        """
        Handles the 1st post-payment modal:
        'Outdoor Advertising System' -> 'Would you like to respond to survey?'
        Clicks 'No' by default to dismiss survey.
        """
        self.logger.info("Checking for survey prompt modal ('Would you like to respond to survey?')...")
        try:
            expect(self.survey_modal_text).to_be_visible(timeout=timeout_ms)
            self.logger.info("Survey modal is displayed")

            if respond:
                self.logger.info("Clicking 'Yes' button on survey modal...")
                self.survey_yes_btn.click()
            else:
                self.logger.info("Clicking 'No' button on survey modal...")
                expect(self.survey_no_btn).to_be_visible(timeout=5000)
                self.survey_no_btn.click()

            self._wait_for_loader()
            self.logger.info("Survey modal dismissed successfully")
        except Exception as e:
            self.logger.warning(f"Survey modal not encountered or already dismissed: {e}")

        return self

    def click_return_home(self, timeout_ms: int = 30000) -> None:
        """
        In the 2nd post-payment step, clicks the orange 'Return Home' button on
        the success page and verifies navigation back to the Dashboard.
        """
        self.logger.info("Verifying Success page and clicking 'Return Home' button...")
        expect(self.success_heading).to_be_visible(timeout=15000)
        expect(self.return_home_btn).to_be_visible(timeout=10000)

        self.logger.info("Clicking 'Return Home' button...")
        self.return_home_btn.click()
        self._wait_for_loader(timeout=25000)

        # Verify landing on Dashboard
        dashboard_heading = (
            self.page.locator("#btnSubmitApp")
            .or_(self.page.get_by_text("Submit an Application"))
            .or_(self.page.get_by_text("Outdoor Advertising System"))
            .first
        )
        expect(dashboard_heading).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Successfully returned to Home/Dashboard! Current URL: {self.page.url}")

    def complete_payment_flow(
        self,
        card_number: str = "4111111111111111",
        cvv: str = "111",
        name: str = "QA Tester",
        exp_month: str = "03",
        exp_year: str = "2029",
        zip_code: str = "60601",
    ) -> None:
        """
        Executes end-to-end payment gateway and post-payment workflow:
        1. If already on CASuccessPageFull (no fee), directly dismisses survey and returns home.
        2. Otherwise, completes card details on Payment Gateway, reviews, and submits payment.
        3. Clicks 'No' on the survey modal ('Would you like to respond to survey?').
        4. Clicks 'Return Home' on the success page and verifies return to Dashboard.
        """
        if "casuccesspagefull" in self.page.url.lower() or self.success_heading.is_visible(timeout=3000):
            self.logger.info("Application has no fee: already on Success Page (CASuccessPageFull)")
            self.handle_survey_modal(respond=False)
            self.click_return_home()
            return

        self.wait_for_payment_gateway()
        self.fill_card_details(
            card_number=card_number,
            cvv=cvv,
            name=name,
            exp_month=exp_month,
            exp_year=exp_year,
            zip_code=zip_code,
        )
        self.click_next_step()
        self.submit_payment()
        self.handle_survey_modal(respond=False)
        self.click_return_home()
