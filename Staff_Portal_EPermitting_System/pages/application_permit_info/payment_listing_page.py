import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PaymentListingPage(BasePage):
    """
    Page Object Model for Payments tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation / Tabs
        self.payments_tab = page.get_by_role("link", name="Payments")

        # Page Headers & Containers
        self.log_app_header = page.locator("#LogAppHeader")
        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing")
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.refund_details_heading = page.get_by_role("heading", name="Refund Details")
        self.documents_log_heading = page.locator("#divfrmLog, #LogDynGridLoad, h1, h2, h3, h4, h5, h6").get_by_text("Documents and Log").first

        # Action Buttons
        self.add_new_payment_button = page.get_by_role("button", name=" Add New Payment")
        self.save_button = page.get_by_role("button", name=" Save")
        self.edit_payment_button = page.locator("#btnPaymentDetailsEdit, a.k-grid-edit").first

        # Dropdown Triggers
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --").first
        self.payment_method_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Method Of Payment --").first
        self.payment_subtype_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Sub Type--").first
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select payment Status --").first

        # Inputs
        self.amount_input = page.get_by_role("spinbutton", name="Requested Amount ($) *").first
        self.comments_input = page.get_by_role("textbox", name="Comments")

    def navigate_to_payments(self) -> None:
        """Transitions to the Payments tab."""
        logger.info("Navigating to Payments tab.")
        self._wait_for_loader()
        self.js_click(self.payments_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates headers exist on the Payment Listing page."""
        logger.info("Verifying Payment Listing page initial layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.payment_listing_heading).to_be_visible(timeout=10000)

    def fill_and_save_payment(self, amount: str = "500", comments: str = "") -> None:
        """Adds and saves a payment record."""
        logger.info(f"Adding new payment record for amount ${amount}.")
        if self.add_new_payment_button.is_visible():
            self.js_click(self.add_new_payment_button)
            self._wait_for_loader()

        for trigger in [
            self.payment_type_dropdown,
            self.payment_method_dropdown,
            self.payment_subtype_dropdown,
            self.payment_status_dropdown,
        ]:
            if trigger.is_visible():
                self.select_first_dropdown_option(trigger)

        if self.amount_input.is_visible():
            self.js_click(self.amount_input)
            self.amount_input.fill(amount)

        if comments and self.comments_input.is_visible():
            self.comments_input.fill(comments)

        self.set_all_datefields_to_current()

        if self.save_button.is_visible():
            self.js_click(self.save_button)
            self._wait_for_loader()
        logger.info("Payment details saved successfully.")

    def add_payment_details(self, amount: str = "500", comments: str = "") -> None:
        """Alias for fill_and_save_payment."""
        self.fill_and_save_payment(amount=amount, comments=comments)

    def edit_payment_record(self) -> None:
        """Edits existing payment entry."""
        logger.info("Editing payment details.")
        if self.edit_payment_button.is_visible():
            self.js_click(self.edit_payment_button)
            self._wait_for_loader()
            if self.save_button.is_visible():
                self.js_click(self.save_button)
                self._wait_for_loader()
