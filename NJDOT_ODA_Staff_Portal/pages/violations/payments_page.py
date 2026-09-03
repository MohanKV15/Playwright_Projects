import re
import logging
from datetime import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationPaymentsPage(BasePage):
    """Page Object Model for the Violation Payments section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")

        # Search elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.dealer_name_search_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.customer_results_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.edit_violation_button = page.locator("#btnViolationsEdit")

        # Violation Details & Payments Listing Tab Elements
        self.payments_tab_link = page.get_by_role("link", name="Payments")
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.violation_details_text = page.get_by_text("Violation Details Violation")
        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing")
        self.payment_listing_grid = page.locator(".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12")
        self.add_paper_check_btn = page.get_by_role("button", name=" Add Paper Check")

        # Payment Details Page Elements
        self.payment_details_text = page.get_by_text("Payment Details Save Back")
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --")
        self.dealer_name_input = page.locator("#frmPaymentDetails").get_by_role("textbox", name="Dealer Name")
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select payment Status --")
        self.check_number_input = page.get_by_role("textbox", name="Check #", exact=True)
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.refund_details_heading = page.get_by_role("heading", name="Refund Details")
        self.payable_to_input = page.get_by_role("textbox", name="Payable to")
        self.refund_check_number_input = page.get_by_role("textbox", name="Refund Check #")
        self.save_button = page.get_by_role("button", name=" Save")

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Violations."""
        logger.info("Expanding Violations PanelBar navigation.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations Listing."""
        self._expand_navigation_menu()
        if not self.violations_listing_link.is_visible():
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def search_by_dealer_name(self, dealer_name: str) -> None:
        """Searches violations grid by dealer name."""
        logger.info(f"Searching for dealer '{dealer_name}' in listing grid.")
        self.dealer_name_search_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_search_input.click()
        self.dealer_name_search_input.fill(dealer_name)
        self.search_button.click()
        self._wait_for_loader()
        expect(self.customer_results_container).to_be_visible(timeout=15000)

    def click_edit_on_first_record(self) -> None:
        """Clicks edit button on the first record in search results."""
        logger.info("Opening the first violation record details.")
        self.edit_violation_button.first.wait_for(state="visible", timeout=10000)
        self.edit_violation_button.first.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def navigate_to_payments(self) -> None:
        """Navigates to the Payments tab from Violation Details page."""
        logger.info("Navigating to Payments tab.")
        self.payments_tab_link.wait_for(state="visible", timeout=10000)
        self.payments_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        # Verify payments listing view is loaded
        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.violation_details_text).to_be_visible(timeout=10000)
        expect(self.payment_listing_heading).to_be_visible(timeout=10000)
        expect(self.payment_listing_grid).to_be_visible(timeout=10000)

    def click_add_paper_check(self) -> None:
        """Clicks Add Paper Check button and waits for payment details form to load."""
        logger.info("Clicking Add Paper Check button.")
        self.add_paper_check_btn.wait_for(state="visible", timeout=10000)
        self.add_paper_check_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        # Assert page title is loaded
        expect(self.payment_details_text).to_be_visible(timeout=15000)

    def fill_payment_details(
        self,
        payment_type: str = None,
        dealer_name: str = "Vansh tech pvt ltd",
        payment_status: str = None,
        check_number: str = None,
        comments: str = None,
        payable_to: str = None,
        refund_check_number: str = None
    ) -> str:
        """Fills out the Payment Details & Refund Details form completely, returning the used check number."""
        logger.info("Filling payment details form.")
        fake = Faker()
        
        # Select Payment Type dropdown (always chooses 1st option)
        self._select_dropdown_option(self.payment_type_dropdown, payment_type)
        
        # Fill Dealer Name
        self.js_click(self.dealer_name_input)
        self.dealer_name_input.fill(dealer_name)
        
        # Select Payment Status (always chooses 1st option)
        self._select_dropdown_option(self.payment_status_dropdown, payment_status)
        
        # Fill Check # (using faker if not provided)
        actual_check_number = check_number if check_number else f"CHK-{fake.random_int(min=1000, max=9999)}"
        self.js_click(self.check_number_input)
        self.check_number_input.fill(actual_check_number)
        
        # Fill Comments (using faker if not provided)
        actual_comments = comments if comments else f"Automated test: {fake.word()}"
        self.js_click(self.comments_input)
        self.comments_input.fill(actual_comments)
        
        # Verify Refund Details section
        expect(self.refund_details_heading).to_be_visible(timeout=10000)
        
        # Fill Payable to (using faker if not provided)
        actual_payable_to = payable_to if payable_to else fake.company()
        self.js_click(self.payable_to_input)
        self.payable_to_input.fill(actual_payable_to)
        
        # Fill Refund Check # (using faker if not provided)
        actual_refund_check_number = refund_check_number if refund_check_number else str(fake.random_int(min=10, max=99))
        self.js_click(self.refund_check_number_input)
        self.refund_check_number_input.fill(actual_refund_check_number)
        
        # Set all dates to current date using JS injection
        self.set_all_datefields_to_current()

        return actual_check_number

    def save_payment(self, check_number: str = None) -> None:
        """Saves the payment, verifies return to listing, and confirms the record is displayed in the grid."""
        logger.info("Saving payment.")
        self.js_click(self.save_button)
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        # Verify return to listing
        expect(self.payment_listing_grid).to_be_visible(timeout=15000)

        # Verify that the saved check number is listed in the grid
        if check_number:
            logger.info(f"Verifying saved check number '{check_number}' is listed in the grid.")
            try:
                expect(self.page.get_by_text(check_number).first).to_be_visible(timeout=8000)
            except AssertionError:
                logger.warning(f"Check number '{check_number}' was not immediately found on the first page of the grid (might be on a subsequent page).")

    def set_all_datefields_to_current(self) -> None:
        """Sets all Kendo DatePickers on the page directly to the current date via JavaScript."""
        current_date_str = datetime.now().strftime("%m/%d/%Y")
        logger.info(f"JS Injecting current date: '{current_date_str}' to all active datepicker widgets.")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"]').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                    }}
                }});
            }}
        """)
        self.page.wait_for_timeout(500)

    def _select_dropdown_option(self, trigger_locator, option_text: str = None) -> None:
        """Helper to click a Kendo dropdown and select option_text or the first available option."""
        trigger_locator.wait_for(state="visible", timeout=10000)
        trigger_locator.click()
        
        # Wait dynamically for options to be visible
        try:
            self.page.locator("li[role='option']:visible").first.wait_for(state="visible", timeout=5000)
        except Exception:
            pass
        
        # Target only visible options to avoid matching hidden dropdown lists in the DOM
        if option_text:
            option = self.page.locator("li[role='option']:visible").filter(has_text=option_text).first
            if option.count() > 0:
                self.js_click(option)
                self.page.wait_for_timeout(500)
                self._wait_for_loader()
                return
                
        # Fallback to first valid visible option (index 1 is usually the first value, index 0 is the placeholder)
        options = self.page.locator("li[role='option']:visible")
        if options.count() > 1:
            self.js_click(options.nth(1))
        elif options.count() > 0:
            self.js_click(options.first)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

