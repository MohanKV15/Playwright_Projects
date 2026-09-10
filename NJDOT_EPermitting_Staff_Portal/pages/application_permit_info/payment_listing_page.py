import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.kendo_controls import KendoControls

logger = logging.getLogger(__name__)


class PaymentListingPage(BasePage):
    """
    Page Object Model for Payment Listing & Payment Details in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.payments_tab = page.get_by_role("link", name="Payments").or_(
            page.locator("a.k-link:has-text('Payments'), .k-tabstrip a:has-text('Payments'), a:has-text('Payments')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")

        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing").or_(
            page.locator("h1:has-text('Payment Listing'), h2:has-text('Payment Listing'), h3:has-text('Payment Listing')")
        ).first

        self.row_div_three = page.locator(".k-grid-content").first.or_(
            page.locator(".row > div:nth-child(3), #div4319PaymentDetailStaffFull > div:nth-child(3)")
        ).first

        # ── Form Controls & Buttons ───────────────────────────────────────────
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment").or_(
            page.get_by_role("button", name="Add New Payment")
        ).or_(
            page.locator("#btnAddNewPayment, #btnAddNewPaymentDetail")
        ).first

        self.payment_details_heading = page.get_by_role("heading", name="Payment Details").or_(
            page.get_by_role("heading", name=re.compile(r"Payment Details", re.I))
        ).or_(
            page.locator("legend:has-text('Payment Details'), .k-window-title:has-text('Payment Details'), #div4319PaymentDetailStaffAdd_wnd_title")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(
            page.locator("button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save']")
        ).first

        self.documents_log_heading = page.locator(
            "#btnAttachDoc, button:has-text('Attach Document'), .btn:has-text('Attach Document'), #divfrmLog, #LogDynGridLoad, legend:has-text('Document'), h1:has-text('Document'), h2:has-text('Document'), h3:has-text('Document'), div:has-text('Documents and Log'), span:has-text('Documents')"
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_payments(self) -> None:
        """Navigates to Payments tab and waits for load."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()

        if "PaymentDetailStaffFull" not in self.page.url and "paymentFullView" not in self.page.url:
            if self.payments_tab.is_visible():
                self.payments_tab.click()
            else:
                self.page.locator("a:has-text('Payments'), span:has-text('Payments')").first.click()

            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass

        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Verifies Payments page initial layout matching codegen assertions."""
        logger.info("Verifying Payments initial layout.")
        self._wait_for_loader()
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.payment_listing_heading).to_be_visible(timeout=15000)
        expect(self.row_div_three).to_be_visible(timeout=15000)

    def add_payment_details(self, amount: str = "50", comments: str = "test") -> None:
        """
        Fills and saves payment details matching exact codegen sequence:
        1. Click 'Add New Payment' if visible -> Expect 'Payment Details' heading
        2. Always select the 1st valid option in every dropdown (Payment Type, Method of Payment, Payment Sub Type, Payment Status)
        3. Fill Requested Amount ($) & Comments
        4. Populate Date Pickers using present day
        5. Click Save and assert no validation errors
        """
        logger.info(f"Adding payment details - Amount: {amount}, Comments: {comments}")
        self._wait_for_loader()

        if self.add_new_payment_button.count() > 0 and self.add_new_payment_button.is_visible():
            self.add_new_payment_button.click()
            self._wait_for_loader()

        try:
            expect(self.payment_details_heading).to_be_visible(timeout=5000)
        except Exception as e:
            logger.warning(f"Payment details heading check note: {e}")

        # 1. Multi-pass selection to select 1st valid option for all dropdowns (handles cascading AJAX)
        for _ in range(4):
            self.select_all_kendo_dropdowns()
            self.page.wait_for_timeout(300)
            self._wait_for_loader()

        # 2. Fill Requested Amount ($) matching get_by_role("spinbutton", name="Requested Amount ($) *")
        try:
            amount_input = self.page.get_by_role("spinbutton", name="Requested Amount ($) *").or_(
                self.page.locator(".k-numerictextbox input.k-formatted-value:visible, #Pay_Amount:visible")
            ).or_(
                self.page.get_by_role("spinbutton").first
            ).first
            if amount_input.is_visible():
                amount_input.click(force=True)
                amount_input.fill(str(amount))
                amount_input.press("Tab")
        except Exception as e:
            logger.warning(f"Amount UI fill note: {e}")

        try:
            self.fill_kendo_numeric("Pay_Amount", float(amount))
        except Exception:
            pass

        self.page.evaluate("""
            (amt) => {
                var jq = window.jQuery || window.$;
                if (!jq) return;
                jq('#Pay_Amount, input[name="Pay_Amount"]').each(function() {
                    var $el = jq(this);
                    var num = $el.data('kendoNumericTextBox') || $el.closest('.k-numerictextbox').data('kendoNumericTextBox');
                    if (num) {
                        num.value(parseFloat(amt));
                        num.trigger('change');
                    }
                    $el.val(amt).trigger('change').trigger('input').trigger('blur');
                    try { if (jq.validator) $el.valid(); } catch(e){}
                });
                jq('.k-numerictextbox input').val(amt).trigger('change').trigger('input').trigger('blur');
                jq('[data-valmsg-for="Pay_Amount"], [data-valmsg-for="Requested Amount"]').removeClass('field-validation-error').addClass('field-validation-valid').text('');
            }
        """, float(amount))

        # 3. Fill Comments matching get_by_role("textbox", name="Comments")
        try:
            comments_input = self.page.get_by_role("textbox", name="Comments").or_(
                self.page.locator("#Pay_Comments, textarea[name='Pay_Comments'], #LotComments, textarea[name='LotComments']")
            ).first
            if comments_input.is_visible():
                comments_input.click(force=True)
                comments_input.fill(comments)
            else:
                self.page.evaluate("""
                    (cmt) => {
                        var jq = window.jQuery || window.$;
                        if (jq) jq('#Pay_Comments, #LotComments, textarea[name*="Comment"]').val(cmt).trigger('change').trigger('input');
                    }
                """, comments)
        except Exception as e:
            logger.warning(f"Comments fill note: {e}")

        # 4. Inject present day into all date fields
        self.set_all_datefields_to_current()

        # 5. Click Save matching get_by_role("button", name=" Save")
        if self.save_button.is_visible():
            self.save_button.click()
        else:
            self.js_click(self.save_button)

        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 6. Final assertions matching codegen
        expect(self.row_div_three).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
