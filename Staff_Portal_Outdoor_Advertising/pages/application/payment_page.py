import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PaymentsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.payments_link = page.get_by_role("link", name="Payments")
        
        # Trigger button
        self.add_paper_check_btn = page.get_by_role("button", name=" Add Paper Check")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.partial_form = page.locator("#partial-form").nth(1)
        
        # Dropdowns/Selects
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --")
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select payment Status --")
        
        # Inputs (Payment details)
        self.check_num_input = page.get_by_role("textbox", name="Check #", exact=True)
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.payable_to_input = page.locator("#Payable_To")
        
        # Refund details validation
        self.refund_details_heading = page.get_by_role("heading", name="Refund Details")
        
        # Date Pickers
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        
        # Inputs (Refund details)
        self.refund_payable_to_input = page.get_by_role("textbox", name="Payable to")
        self.refund_check_num_input = page.get_by_role("textbox", name="Refund Check #")
        
        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing")
        self.payment_grid = page.locator(".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_payments_tab(self) -> None:
        """Navigates to the Payments tab and verifies it has loaded."""
        logger.info("Navigating to the Payments tab")
        self._expand_navigation_menu()
        self.payments_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()
        expect(self.add_paper_check_btn).to_be_visible(timeout=15000)

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option']")
        self.page.wait_for_timeout(500)
        
        # The first option at index 0 might be a placeholder like '--Select--'.
        # Try to select the first valid choice at index 1, otherwise fallback to index 0.
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            options.nth(1).click()
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            options.nth(0).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        self._wait_for_loader()

    def select_current_date(self, picker_index: int) -> None:
        """Opens the date picker at the given index and selects the current day (focused/today's date)."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        self.js_click(self.date_picker_buttons.nth(picker_index))
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link
        try:
            self.js_click(self.focused_date_link.first)
            logger.info("Selected focused date link successfully")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 2nd attempt: try selecting today using Kendo class '.k-today'
        try:
            self.js_click(self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first)
            logger.info("Selected today's date using k-today/k-state-today/k-state-selected selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: look for the day number link inside the visible calendar grid
        try:
            today_day = str(datetime.datetime.now().day)
            self.js_click(self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def add_paper_check_payment(self) -> None:
        """Adds a new Paper Check payment flow using Faker details and current date."""
        logger.info("Adding a new Paper Check payment")
        
        # 1. Click Add Paper Check
        self.js_click(self.add_paper_check_btn)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        
        # 2. Verify modal elements are visible
        expect(self.application_details_heading).to_be_visible(timeout=10000)
        expect(self.payment_details_heading).to_be_visible(timeout=10000)
        expect(self.partial_form).to_be_visible(timeout=10000)
        
        # 3. Choose first dropdown in Payment Type
        logger.info("Opening Payment Type dropdown")
        self.js_click(self.payment_type_dropdown)
        self._select_first_dropdown_option()
        
        # 4. Choose first dropdown in Payment Status
        logger.info("Opening Payment Status dropdown")
        self.js_click(self.payment_status_dropdown)
        self._select_first_dropdown_option()
        
        # 5. Fill Check #, Comments, and Payable To with Faker
        logger.info("Filling Payment details inputs")
        self.js_click(self.check_num_input)
        self.check_num_input.fill(str(self.fake.random_number(digits=6)))
        
        self.js_click(self.comments_input)
        self.comments_input.fill(self.fake.sentence())
        
        self.js_click(self.payable_to_input)
        self.payable_to_input.fill(self.fake.company())
        
        # 6. Verify Refund Details
        expect(self.refund_details_heading).to_be_visible(timeout=10000)
        expect(self.date_picker_buttons.nth(3)).to_be_visible(timeout=10000)
        
        # 7. Select current day in the calendar (index 3)
        self.select_current_date(3)
        
        # 8. Fill Payable to, Refund Check #
        logger.info("Filling Refund details inputs")
        self.js_click(self.refund_payable_to_input)
        self.refund_payable_to_input.fill(self.fake.name())
        
        self.js_click(self.refund_check_num_input)
        self.refund_check_num_input.fill(str(self.fake.random_number(digits=6)))
        
        # 9. Click Save
        logger.info("Saving the payment details")
        self.js_click(self.save_button)

        self.page.wait_for_timeout(2000)
        
        # 10. Verify listing page loads and payment grid is visible
        expect(self.payment_listing_heading).to_be_visible(timeout=15000)
        expect(self.payment_grid).to_be_visible(timeout=15000)
        logger.info("Paper check payment added and verified successfully")
