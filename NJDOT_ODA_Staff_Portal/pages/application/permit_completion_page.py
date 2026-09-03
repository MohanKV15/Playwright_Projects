import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitCompletionPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.permit_completion_link = page.get_by_role("link", name="Permit Completion")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.details_permit_text = page.get_by_text("Application Details Permit")
        self.permit_completion_heading = page.get_by_role("heading", name="Permit Completion")
        
        # Change Status Locators
        self.change_status_btn = page.locator("#btnStatus")
        self.change_status_dialog = page.get_by_label("Change Status")
        self.status_dropdown_trigger = page.get_by_label("Change Status").get_by_text("--Select--")
        self.update_button = page.get_by_role("button", name="Update")
        
        # Date picker select buttons (Kendo datepickers)
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        
        # Generate Permit popup locators
        self.generate_permit_btn = page.get_by_role("button", name=" Generate Permit")
        self.kendo_ok_button = page.get_by_role("button", name="OK")
        
        # Comments & Save
        self.comments_input = page.get_by_role("textbox", name="Comments")
        self.save_button = page.get_by_role("button", name=" Save")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_permit_completion(self) -> None:
        """Navigates to the Permit Completion tab and verifies it has loaded."""
        logger.info("Navigating to the Permit Completion tab")
        self._expand_navigation_menu()
        self.permit_completion_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings on the Permit Completion tab are visible."""
        logger.info("Verifying headings on the Permit Completion tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.details_permit_text.first).to_be_visible(timeout=10000)
        expect(self.permit_completion_heading).to_be_visible(timeout=10000)

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
        self.page.wait_for_timeout(500)

    def change_status(self) -> None:
        """Clicks Change Status, selects the first status option, and clicks Update."""
        logger.info("Clicking the Change Status button")
        self.change_status_btn.click()
        self.page.wait_for_timeout(1000)
        
        logger.info("Opening the Change Status dropdown")
        self.status_dropdown_trigger.click()
        self._select_first_dropdown_option()
        
        logger.info("Clicking the Update button")
        self.update_button.click()
        self.page.wait_for_timeout(1000)

    def select_current_date(self, picker_index: int) -> None:
        """Opens the date picker at the given index and selects the current day (focused date)."""
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

        # 2nd attempt: try selecting today using Kendo class '.k-today'
        try:
            self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a").first.click(timeout=2000)
            logger.info("Selected today's date using k-today/k-state-today selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: look for the day number link inside the visible calendar
        try:
            today_day = str(datetime.datetime.now().day)
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def generate_permit(self) -> None:
        """Clicks 'Generate Permit', handles popup close, and confirms with OK button."""
        logger.info("Clicking the Generate Permit button and expecting a popup")
        with self.page.expect_popup() as popup_info:
            self.generate_permit_btn.click()
        popup = popup_info.value
        popup.close()
        
        logger.info("Confirming dialog with OK button")
        self.kendo_ok_button.click()
        self.page.wait_for_timeout(1000)

    def enter_comments_and_save(self, comments_text: str = None) -> None:
        """Fills comments text field and saves. If no text is provided, generates a fake sentence."""
        if comments_text is None:
            comments_text = self.fake.sentence()
        logger.info(f"Entering comments: '{comments_text}'")
        self.comments_input.click()
        self.comments_input.fill(comments_text)
        
        logger.info("Saving Permit Completion details")
        self.save_button.click()
        self.page.wait_for_timeout(2000)
