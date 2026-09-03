import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class AppealPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.appeal_link = page.get_by_role("link", name="Appeal")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.details_permit_text = page.get_by_text("Application Details Permit")
        self.appeal_heading = page.get_by_role("heading", name="Appeal", exact=True)
        # Form container
        self.container = page.locator("#partial-form").nth(2)
        
        # Dropdowns/Selects (Kendo dropdown wrappers - visible only)
        self.dropdown_triggers = page.locator(".k-dropdown:visible, .k-dropdownlist:visible")
        
        # Checkboxes/Radio labels (visible only)
        self.form_check_label_1 = page.locator(".col-md-2 > .form-check > label:nth-child(5):visible")
        self.form_check_label_2 = page.locator("div:nth-child(15) > .form-check > label:nth-child(5):visible")
        self.yes_no_toggle = page.locator("label:has-text('Yes'), label:has-text('No')") # Fallback to more robust yes/no selector
        self.yes_no_text_click = page.get_by_text("Yes No")
        
        # Date pickers
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        
        # Comments & Save
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_appeal_tab(self) -> None:
        """Navigates to the Appeal tab and verifies the page headings are loaded."""
        logger.info("Navigating to the Appeal tab")
        self._expand_navigation_menu()
        self.appeal_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings on the Appeal tab are visible."""
        logger.info("Verifying headings on the Appeal tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.details_permit_text.first).to_be_visible(timeout=10000)
        expect(self.appeal_heading).to_be_visible(timeout=10000)
        expect(self.container).to_be_visible(timeout=10000)

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option']")
        self.page.wait_for_timeout(500)
        
        # The first option at index 0 might be a placeholder like '--Select--'.
        # Try to select the first valid choice at index 1, otherwise fallback to index 0.
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            target = options.nth(1)
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            target = options.nth(0)
            
        self.js_click(target)
        self.page.wait_for_timeout(500)

    def _select_dropdown_option_by_name(self, name: str) -> None:
        """Selects a specific option by name in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        # Scope the option locator to the visible listbox to avoid matching hidden elements
        option = self.page.locator("[role='listbox']:visible").get_by_role("option", name=name, exact=True)
        logger.info(f"Selecting option '{name}' in Kendo dropdown")
        self.js_click(option)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def select_current_date(self, picker_index: int) -> None:
        """Opens the date picker at the given index and selects the current day (focused/today's date)."""
        logger.info(f"Selecting current date for date picker index {picker_index}")
        self.date_picker_buttons.nth(picker_index).click()
        self.page.wait_for_timeout(500)
        
        # 1st attempt: click the currently focused date link (Kendo focused date label is 'Current focused date is')
        try:
            self.focused_date_link.first.click(timeout=3000)
            logger.info("Selected focused date link successfully")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 2nd attempt: try selecting today using Kendo class '.k-today' or general class
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
            # Find in active/visible calendar container
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

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
        logger.info("Clicking form-check labels")
        self.form_check_label_1.first.click()
        self.form_check_label_2.click()
        self.yes_no_text_click.first.click()
        
        # 6. First date picker (nth(4)) -> Select current date
        self.select_current_date(4)
        
        # 7. Second date picker (nth(2)) -> Select current date
        self.select_current_date(2)
        
        # 8. Assignee dropdown (index 2)
        logger.info(f"Selecting Assignee: {assignee_name}")
        self.js_click(self.dropdown_triggers.nth(2))
        if assignee_name:
            self._select_dropdown_option_by_name(assignee_name)
        else:
            self._select_first_dropdown_option()
            
        # 9. Comments
        if not comments_text:
            comments_text = self.fake.sentence()
        logger.info(f"Filling comments: '{comments_text}'")
        self.comments_input.click()
        self.comments_input.fill(comments_text)
        
        # 10. Click Save
        logger.info("Clicking Save button")
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        
        # 11. Verify the form is still visible or saved
        expect(self.container).to_be_visible(timeout=10000)
        logger.info("Appeal details filled and saved successfully")
