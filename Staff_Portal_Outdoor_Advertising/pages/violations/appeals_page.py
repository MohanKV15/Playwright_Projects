import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ViolationAppealsPage(BasePage):
    """Page Object Model for the Violation Appeals section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()

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

        # Tab Navigation
        self.appeals_tab_link = page.get_by_role("link", name="Appeals")

        # Headings / Layout validation on Appeals tab
        self.violation_details_heading = page.get_by_role("heading", name="Violation Details")
        self.appeal_heading = page.get_by_role("heading", name="Appeal")
        self.appeal_form_container = page.locator("#partial-form").nth(2)

        # Dropdowns/Selects (Kendo dropdown wrappers - visible only)
        self.dropdown_triggers = page.locator(".k-dropdown:visible, .k-dropdownlist:visible")

        # Checkboxes / Radio labels
        self.form_check_label_1 = page.locator(".col-md-2 > .form-check > label").first
        self.form_check_label_2 = page.locator("div:nth-child(15) > .form-check > label").first
        self.radio_label = page.locator(".k-radio-label").first

        # Date pickers
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")

        # Comments & Save
        self.comments_input = page.get_by_role("textbox", name="Comments")
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

    def navigate_to_appeals(self) -> None:
        """Navigates to the Appeals tab from Violation Details page."""
        logger.info("Navigating to Appeals tab.")
        self.appeals_tab_link.wait_for(state="visible", timeout=10000)
        self.appeals_tab_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Validate Appeals tab headings & form structure
        expect(self.violation_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        expect(self.appeal_heading).to_be_visible(timeout=10000)
        expect(self.appeal_form_container).to_be_visible(timeout=10000)

    def select_current_date(self, picker_index: int) -> None:
        """Opens the date picker at the given index and selects the current day (focused/today's date)."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        self.date_picker_buttons.nth(picker_index).click()
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link
        try:
            self.focused_date_link.first.click(timeout=3000)
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

    def fill_appeal_details(self, assignee_name: str = "Andrew Feller", comments_text: str = None) -> None:
        """Fills out the Appeal form details using Faker and selecting the current date."""
        logger.info("Filling Appeal details")

        # 1. First dropdown (index 0) -> Select "Yes"
        logger.info("Selecting first Yes/No dropdown")
        self.js_click(self.dropdown_triggers.nth(0))
        self._select_dropdown_option_by_name("Yes")

        # 2. Second dropdown (index 1) -> Select "Yes"
        logger.info("Selecting second Yes/No dropdown")
        self.js_click(self.dropdown_triggers.nth(1))
        self._select_dropdown_option_by_name("Yes")

        # 3. Third dropdown (index 3) -> Select "Yes"
        logger.info("Selecting third Yes/No dropdown")
        self.js_click(self.dropdown_triggers.nth(3))
        self._select_dropdown_option_by_name("Yes")

        # 4. Fourth dropdown (index 4) -> Select "Yes"
        logger.info("Selecting fourth Yes/No dropdown")
        self.js_click(self.dropdown_triggers.nth(4))
        self._select_dropdown_option_by_name("Yes")

        # 5. Checkboxes/Radio buttons
        logger.info("Clicking form-check labels & radio labels")
        self.form_check_label_1.click()
        self.page.wait_for_timeout(300)
        self.form_check_label_2.click()
        self.page.wait_for_timeout(300)
        self.radio_label.click()
        self.page.wait_for_timeout(300)

        # 6. First date picker (nth(4)) -> Select current date
        self.select_current_date(4)

        # 7. Second date picker (nth(2)) -> Select current date
        self.select_current_date(2)

        # 8. Assignee dropdown (index 2) -> Select assignee name
        logger.info(f"Selecting Assignee: {assignee_name}")
        self.js_click(self.dropdown_triggers.nth(2))
        self._select_dropdown_option_by_name(assignee_name)

        # 9. Comments
        if not comments_text:
            comments_text = self.fake.sentence()
        logger.info(f"Filling comments: '{comments_text}'")
        self.comments_input.click()
        self.comments_input.fill(comments_text)

    def save_appeal(self) -> None:
        """Saves the appeal form. Clicks the Save button twice sequentially as per codegen flow."""
        logger.info("Clicking Save button (1st time)")
        self.save_button.click()
        self.page.wait_for_timeout(1000)

        logger.info("Clicking Save button (2nd time)")
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Validate that the Appeal form is still loaded/visible after saving
        expect(self.appeal_form_container).to_be_visible(timeout=15000)
        logger.info("Appeal saved and verified successfully.")
