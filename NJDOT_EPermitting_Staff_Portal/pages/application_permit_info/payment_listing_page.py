import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.kendo_controls import KendoControls

logger = logging.getLogger(__name__)


class PaymentListingPage(BasePage):
    """
    Page Object Model for Payment Listing & Payment Details in Staff Portal E-Permitting System.
    Provides automated methods for navigating to Payments tab, creating payment records,
    and verifying layout & validation errors.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headers ──────────────────────────────────────────────
        self.payments_tab = page.get_by_role("link", name="Payments").or_(
            page.locator("a:has-text('Payments'), span:has-text('Payments'), .k-tabstrip a:has-text('Payments')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")

        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing").or_(
            page.locator("h1:has-text('Payment'), h2:has-text('Payment'), h3:has-text('Payment'), #LogAppHeader")
        ).first

        self.row_div_three = page.locator(".row > div:nth-child(3), #div4319PaymentDetailStaffFull > div:nth-child(3)").first

        # ── Form Controls & Buttons ───────────────────────────────────────────
        self.add_new_payment_button = page.get_by_role("button", name=re.compile(r"Add New", re.I)).or_(
            page.get_by_role("link", name=re.compile(r"Add New", re.I))
        ).or_(
            page.locator("#btnAddNewPayment, #btnAddNew, a:has-text('Add New'), button:has-text('Add New'), .btn:has-text('Add New')")
        ).first

        self.payment_details_heading = page.get_by_role("heading", name=re.compile(r"Payment", re.I)).or_(
            page.locator("legend:has-text('Payment'), .k-window-title:has-text('Payment'), #div4319PaymentDetailStaffAdd_wnd_title, h1:has-text('Payment'), h2:has-text('Payment'), h3:has-text('Payment'), h4:has-text('Payment'), div:has-text('Payment Details')")
        ).first

        self.save_button = page.locator(
            "button:has-text('Save'), input[type='submit'][value='Save'], input[type='button'][value='Save'], a:has-text('Save'), .btn:has-text('Save')"
        ).first

        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log").or_(
            page.get_by_text("Documents and Log")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_payments(self) -> None:
        """Navigates to Payments tab."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()
        if self.payments_tab.is_visible():
            self.js_click(self.payments_tab)
        else:
            self.page.evaluate("$('a:contains(\"Payments\"), span:contains(\"Payments\")').first().click()")

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=2000)
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
        1. Click 'Add New Payment' -> Expect 'Payment Details' heading
        2. Select Payment Type & Method of Payment
        3. Wait for Payment SubType options via Kendo AJAX and select
        4. Fill Requested Amount ($) & Comments
        5. Populate Date Pickers using present day
        6. Click Save -> Expect row div 3 & 'Documents and Log' heading
        """
        logger.info(f"Adding payment details - Amount: {amount}, Comments: {comments}")
        self._wait_for_loader()

        if self.add_new_payment_button.count() > 0 and self.add_new_payment_button.is_visible():
            self.js_click(self.add_new_payment_button)
            self._wait_for_loader()
        else:
            self.page.evaluate("""
                () => {
                    var jq = window.jQuery || window.$;
                    if (jq) jq('#btnAddNewPayment, #btnAddNew, a:contains("Add New"), button:contains("Add New")').first().click();
                }
            """)
            self._wait_for_loader()

        try:
            expect(self.payment_details_heading).to_be_visible(timeout=5000)
        except Exception as e:
            logger.warning(f"Payment details heading check note: {e}")

        # 1. Multi-pass selection to handle cascading Kendo AJAX dropdowns (Payment Type -> Method of Payment -> Payment SubType)
        self.select_all_kendo_dropdowns()
        self._wait_for_loader()
        self.page.wait_for_timeout(300)
        self.select_all_kendo_dropdowns()
        self._wait_for_loader()

        # 2. Fill Requested Amount ($)
        try:
            amount_input = self.page.get_by_role("spinbutton", name="Requested Amount ($) *").or_(
                self.page.get_by_role("spinbutton").first
            ).first
            amount_input.click()
            amount_input.fill(str(amount))
            amount_input.press("Enter")
        except Exception as e:
            logger.warning(f"Amount fill note: {e}")

        # 3. Fill Comments
        try:
            comments_input = self.page.get_by_role("textbox", name="Comments").first
            comments_input.click()
            comments_input.fill(comments)
        except Exception as e:
            logger.warning(f"Comments fill note: {e}")

        # 4. Inject present day into all date fields
        self.set_all_datefields_to_current()

        # 5. Click Save and assert no validation errors
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 6. Final assertions matching codegen
        expect(self.row_div_three).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
