import logging
from typing import Dict, Optional
from playwright.sync_api import Page

from .base_page_handler import BasePageHandler


class PaymentError(Exception):
    pass


class PaymentTimeoutError(PaymentError):
    pass


class ProfessionalPaymentPageHandler(BasePageHandler):
    """Professional Payment Handler (clean + robust)."""

    PAYMENT_TYPE_DROPDOWN = "#PayType"
    PAYMENT_TYPE_CC = "CC"
    NEXT_PAYMENT_TYPE_BTN = "#bntNextPayType"
    NEXT_CUSTOMER_INFO_BTN = "#bntNextCustomerInfo"
    SUBMIT_PAYMENT_BTN = "#submitPayment"

    SUCCESS_INDICATORS = ["Payment Successful", "Success"]
    FAILURE_INDICATORS = ["Payment Failed", "Error"]

    def __init__(self, page: Page, script_name: str = "test"):
        super().__init__(page, script_name)
        self.logger = logging.getLogger(__name__)
        self.payment_status = None

    # -----------------------------
    # Detect Payment Status
    # -----------------------------
    def detect_payment_status(self) -> Optional[str]:

        for text in self.SUCCESS_INDICATORS:
            if self.element_exists(f'text="{text}"'):
                return "success"

        for text in self.FAILURE_INDICATORS:
            if self.element_exists(f'text="{text}"'):
                return "failure"

        return None

    # -----------------------------
    # Select Payment Type
    # -----------------------------
    def safe_select_payment_type(self, timeout_ms: int = 15000) -> bool:
        try:
            self.logger.info("Selecting payment type")

            if not self.wait_for_element(self.PAYMENT_TYPE_DROPDOWN, timeout_ms):
                self._select_via_js(self.PAYMENT_TYPE_DROPDOWN, self.PAYMENT_TYPE_CC)
            else:
                self.page.select_option(self.PAYMENT_TYPE_DROPDOWN, self.PAYMENT_TYPE_CC)

            return self.safe_click(self.NEXT_PAYMENT_TYPE_BTN, timeout_ms)

        except Exception as e:
            self.logger.error(f"Payment type failed: {e}")
            return False

    # -----------------------------
    # Fill Customer Info
    # -----------------------------
    def safe_fill_customer_info(self, timeout_ms: int = 15000) -> bool:
        try:
            if not self.wait_for_element(self.NEXT_CUSTOMER_INFO_BTN, timeout_ms):
                return False

            self.safe_fill("#CustomerInfo_FirstName", "QA")
            self.safe_fill("#CustomerInfo_LastName", "Tester")
            self.safe_fill("#CustomerInfo_Address1", "Test Address")
            self.safe_fill("#CustomerInfo_City", "Test City")
            self.safe_fill("#CustomerInfo_Zip", "07001")
            self.safe_fill("#Phone", "5555555555")
            self.safe_fill("#Email", "qa@test.com")

            return self.safe_click(self.NEXT_CUSTOMER_INFO_BTN, timeout_ms)

        except Exception as e:
            self.logger.error(f"Customer info failed: {e}")
            return False

    # -----------------------------
    # Fill Card Details
    # -----------------------------
    def safe_fill_card_details(self) -> bool:
        try:
            self.logger.info("Filling card details")

            self.page.fill("#CCCardNumber", "4111111111111111")
            self.page.fill("#CCCardCVV", "111")
            self.page.fill("#CCNameOnCard", "QA Tester")

            self.page.select_option("#CCExpirationMonth", "03")
            self.page.select_option("#CCExpirationYear", "2029")

            self.page.click("#bntNextPaymentInfo")

            return True

        except Exception as e:
            self.logger.error(f"Card details failed: {e}")
            return False

    # -----------------------------
    # Submit Payment
    # -----------------------------
    def safe_submit_payment(self, timeout_ms: int = 120000) -> bool:
        try:
            self.logger.info("Submitting payment")

            if not self.safe_click(self.SUBMIT_PAYMENT_BTN, timeout_ms=10000):
                return False

            self.page.wait_for_load_state("networkidle", timeout=timeout_ms)

            status = self.detect_payment_status()
            self.payment_status = status

            return status == "success"

        except Exception as e:
            self.logger.error(f"Payment failed: {e}")
            raise PaymentTimeoutError("Payment timeout")

    # -----------------------------
    # JS fallback (kept important)
    # -----------------------------
    def _select_via_js(self, selector: str, value: str):
        self.page.evaluate(
            """
            (selector, value) => {
                const el = document.querySelector(selector);
                if (!el) return;
                el.value = value;
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """,
            selector,
            value,
        )

    # -----------------------------
    # Full Flow
    # -----------------------------
    def handle_payment(self) -> bool:
        if not self.safe_select_payment_type():
            return False
        if not self.safe_fill_customer_info():
            return False
        if not self.safe_fill_card_details():
            return False
        return self.safe_submit_payment()