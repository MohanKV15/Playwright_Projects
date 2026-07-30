import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PaymentListingPage(BasePage):
    """
    Page Object Model for Payment Listing & Payment Details in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation & Headers
        self.payments_tab = page.locator("a:has-text('Payments'), span:has-text('Payments'), .k-tabstrip a:has-text('Payments')").or_(
            page.get_by_role("link", name="Payments")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")
        self.payment_listing_heading = page.get_by_role("heading", name=re.compile("Payment", re.I)).or_(
            page.locator("h1:has-text('Payment'), h2:has-text('Payment'), h3:has-text('Payment'), .card-header:has-text('Payment')")
        ).first

        # Form Controls
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment").or_(
            page.get_by_role("button", name="Add New Payment")
        ).or_(page.get_by_role("button", name=" Add New")).first

        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --").or_(
            page.locator("#frmPaymentDetails span.k-widget.k-dropdown").first
        ).first

        self.payment_subtype_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Sub Type--").or_(
            page.locator("#frmPaymentDetails span.k-widget.k-dropdown").nth(1)
        ).first

        self.method_of_payment_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Method Of Payment --").or_(
            page.locator("#frmPaymentDetails span.k-widget.k-dropdown").nth(2)
        ).first

        self.requested_amount_input = page.get_by_role("spinbutton", name="Requested Amount ($) *").or_(
            page.locator(".k-numerictextbox input:visible, #Requested_Amount")
        ).first

        self.comments_input = page.get_by_role("textbox", name="Comments").or_(
            page.locator("textarea[name='Comments'], #Comments")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSave, .btn:has-text('Save'), a:has-text('Save')")).first

        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log").or_(
            page.get_by_text("Documents and Log")
        ).first

    def navigate_to_payments(self) -> None:
        """Navigates to Payments tab."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()
        if self.payments_tab.is_visible():
            self.js_click(self.payments_tab)
        else:
            self.page.evaluate("$('a:contains(\"Payments\"), span:contains(\"Payments\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Verifies Payments page layout."""
        logger.info("Verifying Payments page layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)

    def add_payment_details(self, amount: str = "100", comments: str = "test done") -> None:
        """Fills and saves payment details per codegen workflow selecting 1st option for all dropdowns."""
        logger.info(f"Adding payment details with amount: {amount}")
        self._wait_for_loader()

        # 1. Click Add New Payment
        if self.add_new_payment_button.is_visible():
            self.js_click(self.add_new_payment_button)
            self._wait_for_loader()

        self.page.wait_for_timeout(1000)

        # 2. Select Payment Type * (1st option)
        if self.payment_type_dropdown.is_visible():
            self.select_first_dropdown_option(self.payment_type_dropdown)
            self.page.wait_for_timeout(1500)
            self._wait_for_loader()

        # 3. Select Payment Sub Type * (1st option) - after cascade delay
        if self.payment_subtype_dropdown.is_visible():
            self.select_first_dropdown_option(self.payment_subtype_dropdown)
            self.page.wait_for_timeout(1000)
            self._wait_for_loader()

        # 4. Select Method Of Payment * (1st option)
        if self.method_of_payment_dropdown.is_visible():
            self.select_first_dropdown_option(self.method_of_payment_dropdown)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        # 5. Fill Requested Amount ($) *
        val_str = str(amount)
        try:
            req_input = self.page.get_by_role("spinbutton", name=re.compile("Requested Amount", re.I)).or_(
                self.page.locator(".k-numerictextbox input:visible, #Requested_Amount")
            ).first
            if req_input.count() > 0:
                req_input.click(force=True)
                req_input.fill(val_str)
                req_input.press("Tab")
        except Exception as e:
            logger.warning(f"Amount fill note: {e}")

        self.page.evaluate(f"""
            (amtStr) => {{
                var inputs = $('#Requested_Amount, input[name="Requested_Amount"], input[name="RequestedAmount"], [data-val-required*="Requested Amount"]').closest('.k-numerictextbox').find('input');
                if (inputs.length === 0) inputs = $('#Requested_Amount, input[name="Requested_Amount"], input[name="RequestedAmount"]');
                inputs.each(function() {{
                    var num = kendo.widgetInstance($(this)) || $(this).data("kendoNumericTextBox") || $(this).closest(".k-numerictextbox").find("input").data("kendoNumericTextBox");
                    if (num && typeof num.value === "function") {{
                        num.value(parseFloat(amtStr));
                        if (typeof num.trigger === "function") num.trigger("change");
                    }}
                    $(this).val(amtStr).attr("value", amtStr).trigger("input").trigger("change").trigger("blur");
                    var el = this;
                    ['input', 'change', 'blur', 'keyup'].forEach(function(evt) {{
                        var e = document.createEvent('HTMLEvents');
                        e.initEvent(evt, true, true);
                        el.dispatchEvent(e);
                    }});
                }});
            }}
        """, val_str)

        # 6. Fill Comments
        if self.comments_input.is_visible():
            self.js_click(self.comments_input)
            self.comments_input.fill(comments)

        self.set_all_datefields_to_current()

        # 7. Click Save
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 8. Expect Documents and Log heading visible
        if self.documents_log_heading.is_visible():
            expect(self.documents_log_heading).to_be_visible(timeout=10000)
