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
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment").or_(
            page.get_by_role("button", name="Add New Payment")
        ).first

        self.payment_details_heading = page.get_by_role("heading", name="Payment Details").first

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
        self.payments_tab.click()
        self.page.wait_for_load_state("domcontentloaded")
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

        if self.add_new_payment_button.is_visible():
            self.js_click(self.add_new_payment_button)
            self._wait_for_loader()

        expect(self.payment_details_heading).to_be_visible(timeout=15000)

        # 1. Select initial dropdowns (Payment Type & Method of Payment)
        self.select_all_kendo_dropdowns()
        self.page.wait_for_timeout(500)

        # 2. Select Payment SubType explicitly
        sub_type_loc = self.page.locator("#payment_SubType, #Payment_SubType, [name='payment_SubType']").first
        KendoControls.select_first_dropdown_option(self.page, sub_type_loc)
        self.page.wait_for_timeout(300)

        # 3. Universal safety pass for any remaining unselected dropdowns
        self.select_all_kendo_dropdowns()
        self.page.wait_for_timeout(500)

        # 4. Fill Requested Amount ($)
        try:
            amount_input = self.page.get_by_role("spinbutton", name="Requested Amount ($) *").or_(
                self.page.get_by_role("spinbutton").first
            ).first
            amount_input.click()
            amount_input.fill(str(amount))
            amount_input.press("Enter")
        except Exception as e:
            logger.warning(f"Amount fill note: {e}")

        # 5. Fill Comments
        try:
            comments_input = self.page.get_by_role("textbox", name="Comments").first
            comments_input.click()
            comments_input.fill(comments)
        except Exception as e:
            logger.warning(f"Comments fill note: {e}")

        # 6. Inject present day into all date fields
        self.set_all_datefields_to_current()

        # 7. Click Save and assert no validation errors
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

        # 8. Final assertions matching codegen
        expect(self.row_div_three).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
