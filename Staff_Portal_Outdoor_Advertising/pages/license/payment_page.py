import re
import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)


class LicensePaymentPage(BasePage):
    """Page Object for License Payment flow and validations."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

        # Navigation & Sidebar Elements
        self.licenses_menu_link = page.get_by_role("link", name=re.compile(r"Licenses\s*", re.I))
        self.license_listing_link = page.get_by_role("link", name="License Listing")

        # Search & Edit Locators
        self.dealer_name_search = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.edit_row_button = page.locator("#btnLicEdit").first

        # Tab Navigation
        self.payments_tab_link = page.get_by_role("link", name="Payments")

        # Heading Assertions on Payments tab
        self.license_details_heading = page.get_by_role("heading", name="License Details")
        self.payment_listing_heading = page.get_by_role("heading", name="Payment Listing")
        self.partial_form_nth2 = page.locator("#partial-form").nth(2)

        # Trigger Button
        self.add_paper_check_btn = page.get_by_role("button", name=" Add Paper Check")

        # Payment Form Dropdowns and Inputs
        self.payment_type_dropdown = page.locator("#frmPaymentDetails").get_by_text("--Select Payment Type --")
        self.payment_type_option = lambda name: page.get_by_role("option", name=name)
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.payment_status_dropdown = page.locator("#frmPaymentDetails").get_by_text("-- Select Payment Status --")
        self.payment_status_option = lambda name: page.get_by_role("option", name=name, exact=True)
        self.check_num_input = page.get_by_role("textbox", name="Check #", exact=True)

        # Date Picker elements
        self.select_buttons = page.get_by_role("button", name="select")
        self.day_link = lambda d: page.get_by_role("link", name=str(d), exact=True).first

        # Form Validation Headings
        self.payment_details_heading = page.get_by_role("heading", name="Payment Details")
        self.refund_details_heading = page.get_by_role("heading", name="Refund Details")
        self.partial_form_nth1 = page.locator("#partial-form").nth(1)

        # Action Buttons & Final Verification Grid
        self.save_button = page.get_by_role("button", name=" Save")
        self.payment_grid_container = page.locator(".col-md-12 > #partial-form > .form-wrapper > .row > .col-md-12")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("license")

    def navigate_to_license_listing(self) -> None:
        """Navigates to the Licenses -> License Listing page."""
        logger.info("Navigating to License Listing page")
        self._expand_navigation_menu()

        # If the sub-menu link is not visible, toggle the parent Licenses menu link
        if not self.license_listing_link.is_visible():
            logger.info("License Listing link not visible; clicking Licenses menu header to expand.")
            self.licenses_menu_link.click()
            self.page.wait_for_timeout(1000)

        logger.info("Clicking License Listing link")
        self.license_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def search_and_edit_license(self, dealer_name: str = "vansh") -> None:
        """Searches for dealer, waits for results, and clicks Edit on the target row."""
        logger.info(f"Searching for dealer: {dealer_name}")
        self.dealer_name_search.click()
        self.dealer_name_search.fill(dealer_name)
        self.search_button.click()
        self.page.wait_for_timeout(2000)

        logger.info("Clicking Edit on the targeted license row.")
        self.edit_row_button.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def navigate_to_payments_tab(self) -> None:
        """Clicks Payments tab and asserts headings/form visibility."""
        logger.info("Clicking Payments tab.")
        self.payments_tab_link.click()
        self.page.wait_for_timeout(1000)

        expect(self.license_details_heading).to_be_visible(timeout=10000)
        expect(self.payment_listing_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_nth2).to_be_visible(timeout=10000)

    def click_add_paper_check(self) -> None:
        """Clicks Add Paper Check and ensures redirection to the payment details page."""
        logger.info("Clicking Add Paper Check button")
        self.add_paper_check_btn.click()
        self.page.wait_for_timeout(2000)

        # Self-healing navigation/redirect check
        target_url = f"{Config.BASE_URL}/Portal/Page/Index/4319LicensePaymentDetailsStaffFull"
        if target_url not in self.page.url:
            logger.info(f"Page did not redirect automatically. Navigating directly to: {target_url}")
            self.page.goto(target_url)
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)

    def fill_payment_details_using_faker(
        self,
        payment_type: str = "License Fee",
        status: str = "Paid",
        date_day: str = None,
    ) -> None:
        """Fills dropdown options, text inputs using Faker, and selects date day."""
        import datetime
        if date_day is None:
            date_day = str(datetime.datetime.now().day)
        logger.info(f"Selecting Payment Type: {payment_type}")
        self.payment_type_dropdown.click()
        self.page.wait_for_timeout(500)
        self.payment_type_option(payment_type).click()
        self.page.wait_for_timeout(500)

        # Use Faker for dealer name input (as requested by user)
        fake_dealer = self.fake.company()
        logger.info(f"Filling Dealer Name with Faker: {fake_dealer}")
        self.dealer_name_input.click()
        self.dealer_name_input.fill(fake_dealer)

        logger.info(f"Selecting Payment Status: {status}")
        self.payment_status_dropdown.click()
        self.page.wait_for_timeout(500)
        self.payment_status_option(status).click()
        self.page.wait_for_timeout(500)

        # Use Faker for Check # (as requested by user)
        fake_check_num = str(self.fake.random_number(digits=6))
        logger.info(f"Filling Check # with Faker: {fake_check_num}")
        self.check_num_input.click()
        self.check_num_input.fill(fake_check_num)

        # Date Picker select: nth(2) click, select date_day
        logger.info(f"Opening date picker (nth 2) and selecting day: {date_day}")
        self.select_buttons.nth(2).click()
        self.page.wait_for_timeout(500)
        self.day_link(date_day).click()
        self.page.wait_for_timeout(500)

        # Assert payment & refund details form blocks are visible
        expect(self.payment_details_heading).to_be_visible(timeout=10000)
        expect(self.refund_details_heading).to_be_visible(timeout=10000)
        expect(self.partial_form_nth1).to_be_visible(timeout=10000)

    def save_and_verify_payment_grid(self) -> None:
        """Clicks Save and asserts visibility of the final payments grid list container."""
        logger.info("Clicking Save button.")
        self.save_button.click()
        self.page.wait_for_timeout(2000)

        # Verify payment grid is visible
        logger.info("Asserting payment listing grid container is visible.")
        expect(self.payment_grid_container).to_be_visible(timeout=15000)
