import logging
from functools import wraps
from typing import Optional

import pytest
from playwright.sync_api import Page

from NJDOT_EPermitting_Customer_Portal.pages.base_page_handler import BasePageHandler


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

    def detect_payment_status(self) -> Optional[str]:
        for text in self.SUCCESS_INDICATORS:
            if self.element_exists(f'text="{text}"'):
                return "success"

        for text in self.FAILURE_INDICATORS:
            if self.element_exists(f'text="{text}"'):
                return "failure"

        return None

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

    def safe_fill_card_details(self) -> bool:
        try:
            self.logger.info("Filling card details")
            self.page.fill("#CCCardNumber", "4111111111111111")
            self.page.fill("#CCCardCVV", "111")
            self.page.fill("#CCNameOnCard", "QA Tester")
            self.page.select_option("#CCExpirationMonth", "03")
            self.page.select_option("#CCExpirationYear", "2026")
            self.page.click("#bntNextPaymentInfo")
            return True
        except Exception as e:
            self.logger.error(f"Card details failed: {e}")
            return False

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

    def handle_payment(self) -> bool:
        if not self.safe_select_payment_type():
            return False
        if not self.safe_fill_customer_info():
            return False
        if not self.safe_fill_card_details():
            return False
        return self.safe_submit_payment()


def ensure_valid_session(test_func):
    @wraps(test_func)
    def _wrapper(*args, **kwargs):
        page = kwargs.get("authenticated_page") or kwargs.get("page")
        if page is None:
            return test_func(*args, **kwargs)

        handler = BasePageHandler(page, script_name="ensure_valid_session")
        try:
            detected = handler.detect_error_page()
        except Exception:
            return test_func(*args, **kwargs)

        if detected != "session_expired":
            return test_func(*args, **kwargs)

        try:
            from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage

            page.goto(PermitMajorPage.DASHBOARD_URL, wait_until="commit")
            page.wait_for_load_state("networkidle", timeout=30000)
            PermitMajorPage(page, script_name="ensure_valid_session").wait_for_dashboard_to_load()
        except Exception:
            pytest.skip("Session expired and dashboard reload failed.")

        return test_func(*args, **kwargs)

    return _wrapper


def _classify_payment_issue(page: Page, exc: Exception) -> Optional[str]:
    content = ""
    try:
        content = page.content().lower()
    except Exception:
        pass

    msg = str(exc).lower()
    handler = BasePageHandler(page, script_name="handle_payment_test")
    try:
        detected = handler.detect_error_page()
    except Exception:
        detected = None

    if detected == "payment_failure":
        return "payment_failed"
    if detected == "server_error":
        return "gateway_error"
    if detected == "session_expired":
        return "administrator" if "administrator" in content else "timeout"

    if "administrator" in content or "administrator" in msg:
        return "administrator"
    if "gateway" in content or "gateway" in msg or "server error" in content:
        return "gateway_error"
    if "payment failed" in content or ("payment" in msg and ("fail" in msg or "failed" in msg)):
        return "payment_failed"
    if "timeout" in content or "timeout" in msg:
        return "timeout"
    return None


def handle_payment_test(allow_skips_for: list[str]):
    allow = set(allow_skips_for or [])

    def _decorator(test_func):
        @wraps(test_func)
        def _wrapper(*args, **kwargs):
            page = kwargs.get("authenticated_page") or kwargs.get("page")
            try:
                return test_func(*args, **kwargs)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                if page is None:
                    raise

                token = _classify_payment_issue(page, exc)
                if token == "timeout":
                    raise

                if token and token in allow:
                    pytest.skip(f"Skipping due to '{token}' ({exc.__class__.__name__}: {exc}).")
                raise

        return _wrapper

    return _decorator
