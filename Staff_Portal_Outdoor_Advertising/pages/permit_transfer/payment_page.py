import logging
import re
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PermitTransferPaymentPage(BasePage):
    """Page Object Model for the Permit Transfer Payments tab in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Tab navigation
        self.payments_tab_link = page.get_by_role("link", name="Payments")

        # Headings & Tab Content Assertions
        self.transfer_details_text = page.get_by_text("Transfer Details Permit")
        self.payment_listing_text = page.get_by_text("Payment Listing Add Paper")
        self.add_paper_check_btn = page.get_by_role("button", name=" Add Paper Check")

        # Form Elements
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.partial_form_details = page.locator("#partial-form")
        
        # Dropdowns
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --")
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select payment Status --")

        # Text inputs
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.check_number_input = page.get_by_role("textbox", name="Check #", exact=True)
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.payable_to_input = page.get_by_role("textbox", name="Payable to")
        self.refund_check_input = page.get_by_role("textbox", name="Refund Check #")

        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        self.grid_container = page.locator(".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12")

        # Date Pickers
        self.date_picker_buttons = page.get_by_role("button", name="select")

    def navigate_to_payments(self) -> None:
        """Navigates to the Payments tab and verifies the layout."""
        logger.info("Navigating to Payments tab.")
        self.payments_tab_link.wait_for(state="visible", timeout=10000)
        self.payments_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.transfer_details_text).to_be_visible(timeout=15000)
        expect(self.payment_listing_text).to_be_visible(timeout=10000)

    def click_add_paper_check(self) -> None:
        """Clicks 'Add Paper Check' button and verifies layout."""
        logger.info("Clicking Add Paper Check button.")
        self.add_paper_check_btn.wait_for(state="visible", timeout=10000)
        self.js_click(self.add_paper_check_btn)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.payment_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_details.first).to_be_visible(timeout=10000)

    def select_current_date(self, picker_index: int) -> None:
        """Opens the date picker at the given index and selects the current day."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        self.js_click(self.date_picker_buttons.nth(picker_index))
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link
        try:
            self.page.get_by_label("Current focused date is").get_by_role("link").first.click(timeout=3000)
            logger.info("Selected focused date link successfully")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 2nd attempt: try selecting today using Kendo classes
        try:
            self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first.click(timeout=2000)
            logger.info("Selected today's date using k-today/k-state-today/k-state-selected selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: look for the day number link inside the visible calendar grid
        try:
            today_day = str(datetime.datetime.now().day)
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def _select_dropdown_option_by_name(self, name: str) -> None:
        """Selects a specific option by name in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        option = self.page.locator("[role='listbox']:visible").get_by_role("option", name=name, exact=True)
        logger.info(f"Selecting option '{name}' in Kendo dropdown")
        self.js_click(option)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()


    def fill_payment_details(
        self,
        payment_type: str = "Transfer Fee",
        dealer_name: str = "vansh",
        payment_status: str = "Cancelled",
        check_number: str = None,
        comments: str = None,
        payable_to: str = None,
        refund_check_number: str = None
    ) -> None:
        """Fills out the Payment details form using Faker."""
        logger.info("Filling payment details.")

        # Select Payment Type dropdown
        self.js_click(self.payment_type_dropdown)
        self._select_dropdown_option_by_name(payment_type)

        # Fill Dealer Name
        self.js_click(self.dealer_name_input)
        self.dealer_name_input.fill(dealer_name)

        # Select Payment Status
        self.js_click(self.payment_status_dropdown)
        self._select_dropdown_option_by_name(payment_status)

        # Fill Check # (Faker)
        if not check_number:
            check_number = f"CHK-{self.fake.random_int(min=1000, max=9999)}"
        logger.info(f"Filling Check #: {check_number}")
        self.js_click(self.check_number_input)
        self.check_number_input.fill(check_number)

        # Select Check Date (nth(2))
        self.select_current_date(2)

        # Fill Comments (Faker)
        if not comments:
            comments = self.fake.sentence()
        logger.info(f"Filling Comments: {comments}")
        self.js_click(self.comments_input)
        self.comments_input.fill(comments)

        # Expect details layout is fully visible
        expect(self.page.get_by_text("Payment Details Save Back")).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("heading", name="Refund Details")).to_be_visible(timeout=10000)

        # Select Refund Check Date (nth(3))
        self.select_current_date(3)

        # Fill Payable to (Faker)
        if not payable_to:
            payable_to = self.fake.name()
        logger.info(f"Filling Payable to: {payable_to}")
        self.js_click(self.payable_to_input)
        self.payable_to_input.fill(payable_to)

        # Fill Refund Check # (Faker)
        if not refund_check_number:
            refund_check_number = str(self.fake.random_int(min=10, max=99))
        logger.info(f"Filling Refund Check #: {refund_check_number}")
        self.js_click(self.refund_check_input)
        self.refund_check_input.fill(refund_check_number)

    def save_payment(self) -> None:
        """Saves the payment details and verifies returned list grid layout."""
        logger.info("Saving payment.")
        self.js_click(self.save_button)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.grid_container).to_be_visible(timeout=15000)

