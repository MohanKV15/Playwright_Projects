from playwright.sync_api import Page
import re


class PaymentPage:
    def __init__(self, page: Page):
        self.page = page

    # -------------------------------
    # Helper
    # -------------------------------
    def _scroll_and_click(self, locator, timeout_ms: int = 10000):
        locator.wait_for(state="visible", timeout=timeout_ms)
        locator.scroll_into_view_if_needed()
        locator.click()

    # -------------------------------------------------------------
    # Select Credit/Debit Card (STABLE + FAST)
    # -------------------------------------------------------------
    def select_credit_debit_card(self):

        # ✅ Step 1: Wait for final payment page (Safe Regex pattern)
        self.page.wait_for_url(re.compile(r".*/Checkout/Payment", re.I), timeout=35000)

        # ✅ Step 2: Ensure DOM is ready
        self.page.wait_for_load_state("domcontentloaded")

        # ✅ Step 3: Wait for dropdown
        paytype = self.page.locator("#PayType")
        paytype.wait_for(state="attached", timeout=15000)

        try:
            # Fast path
            self.page.select_option("#PayType", "CC")
        except Exception:
            # Fallback (for hidden/JS controlled dropdown)
            self.page.evaluate("""
                () => {
                    const el = document.getElementById('PayType');
                    if (el) {
                        el.value = 'CC';
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """)

        # ✅ Step 4: Click Next
        next_btn = self.page.locator("#bntNextPayType")
        next_btn.wait_for(state="visible", timeout=15000)
        next_btn.click()

        # ✅ Step 5: Ensure next section loaded
        self.page.locator("#bntNextCustomerInfo").wait_for(state="visible", timeout=15000)

    # -------------------------------------------------------------
    # Fill customer information
    # -------------------------------------------------------------
    def fill_customer_information(self):

        self.page.fill("#CustomerInfo_FirstName", "QA")
        self.page.fill("#CustomerInfo_LastName", "Tester")
        self.page.fill("#CustomerInfo_Address1", "1 Test Street")
        self.page.fill("#CustomerInfo_City", "Testville")
        self.page.fill("#CustomerInfo_Zip", "07001")
        self.page.fill("#Phone", "5555555555")
        self.page.fill("#Email", "qa@test.com")

        self.page.locator("#bntNextCustomerInfo").click()

        self.page.locator("#bntNextPaymentInfo").wait_for(state="visible", timeout=10000)

    # -------------------------------------------------------------
    # Enter card details
    # -------------------------------------------------------------
    def fill_card_details(self):

        self.page.fill("#CCCardNumber", "4111111111111111")
        self.page.fill("#CCCardCVV", "111")
        self.page.fill("#CCNameOnCard", "QA Tester")

        self.page.select_option("#CCExpirationMonth", "03")
        self.page.select_option("#CCExpirationYear", "2029")

        self.page.locator("#bntNextPaymentInfo").click()

    # -------------------------------------------------------------
    # Submit payment
    # -------------------------------------------------------------
    def submit_payment(self):

        submit_btn = self.page.locator("#submitPayment")

        submit_btn.wait_for(state="visible", timeout=30000)
        submit_btn.scroll_into_view_if_needed()
        submit_btn.click()

        # Payment gateway can take time
        self.page.get_by_text("Payment Successful").wait_for(timeout=120000)

    # -------------------------------------------------------------
    # Verify payment success
    # -------------------------------------------------------------
    def verify_payment_success(self):

        try:
            self.page.get_by_text(re.compile("Application Reference", re.I)).wait_for(timeout=5000)
            return
        except Exception:
            pass

        try:
            self.page.get_by_text(re.compile(r"APG\d{3,}", re.I)).wait_for(timeout=5000)
            return
        except Exception:
            pass

        self.page.get_by_text(re.compile(r"Payment Successful|Return Home", re.I)).wait_for(timeout=5000)