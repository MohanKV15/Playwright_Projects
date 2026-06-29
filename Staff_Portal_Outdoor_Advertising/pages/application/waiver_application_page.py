import re
import logging
import datetime
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class WaiverApplicationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Sidebar Link
        self.waiver_app_link = page.get_by_role("link", name="Waiver Application")
        
        # Heading/Tab Validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.waiver_app_heading = page.get_by_role("heading", name="Waiver Application", exact=True)
        self.waiver_save_date_text = page.get_by_text("Waiver Application Save Date")
        
        # Date Pickers
        self.date_picker_buttons = page.get_by_role("button", name="select")
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        
        # Checkboxes/Radio buttons (visible only)
        self.label_5 = page.locator("label").nth(5)
        self.radio_label_8 = page.locator("div:nth-child(8) > div > .k-radio-label").first
        self.radio_label_14 = page.locator("div:nth-child(14) > div > .k-radio-label").first
        
        # Comments
        self.comments_input = page.locator("#Waiver_Comments")
        
        # Action Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        
        # Kendo Confirmation Dialog
        self.confirm_dialog = page.locator("div").filter(has_text=re.compile(r"^u-njoda\.bemcorp\.net$")).first
        self.confirm_text = page.get_by_text("Are you sure you want to")
        self.ok_button = page.get_by_role("button", name="OK")
        
        # Final section validation
        self.final_section = page.locator("#partial-form > section > div > div")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_waiver_application_tab(self) -> None:
        """Navigates to the Waiver Application tab and verifies headings load."""
        logger.info("Navigating to the Waiver Application tab")
        self._expand_navigation_menu()
        self.waiver_app_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self.verify_tab_headings()

    def verify_tab_headings(self) -> None:
        """Verifies that the headings on the Waiver Application tab are visible."""
        logger.info("Verifying headings on the Waiver Application tab")
        expect(self.application_details_heading).to_be_visible(timeout=15000)
        expect(self.waiver_app_heading).to_be_visible(timeout=10000)
        expect(self.waiver_save_date_text).to_be_visible(timeout=10000)

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

        # 2nd attempt: try selecting today using Kendo class '.k-today'
        try:
            self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first.click(timeout=2000)
            logger.info("Selected today's date using k-today/k-state-today/k-state-selected selector")
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        # 3rd attempt: click by grid cell title matching today's formatted date
        try:
            now = datetime.datetime.now()
            day_str = now.strftime("%d")
            day_unpadded = str(now.day)
            
            # Format: Weekday, Month Day,
            title_padded = now.strftime(f"%A, %B {day_str},")
            title_unpadded = now.strftime(f"%A, %B {day_unpadded},")
            
            for title in [title_padded, title_unpadded]:
                match = self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link").get_by_title(re.compile(rf"^{re.escape(title)}"), exact=False)
                if match.count() > 0:
                    match.first.click(timeout=2000)
                    logger.info(f"Selected date using title '{title}'")
                    self.page.wait_for_timeout(500)
                    return
                # Also try matching on grid element itself
                match_grid = self.page.get_by_role("grid").get_by_title(re.compile(rf"^{re.escape(title)}"), exact=False)
                if match_grid.count() > 0:
                    match_grid.first.click(timeout=2000)
                    logger.info(f"Selected date via grid matching title '{title}'")
                    self.page.wait_for_timeout(500)
                    return
        except Exception:
            pass

        # 4th attempt: look for the day number link inside the visible calendar grid
        try:
            today_day = str(datetime.datetime.now().day)
            self.page.locator(".k-calendar:visible, .k-calendar-container:visible, [role='grid']:visible").get_by_role("link", name=today_day, exact=True).first.click(timeout=2000)
            logger.info(f"Selected day number '{today_day}' link")
            self.page.wait_for_timeout(500)
            return
        except Exception as e:
            logger.error(f"Failed to select current date on date picker {picker_index}: {e}")
            raise e

    def fill_waiver_application_details(self, comments_text: str = None) -> None:
        """Fills out the Waiver Application details using Faker and selecting the current date."""
        logger.info("Filling Waiver Application details")
        
        # 1. Date Picker 1 (index 0) -> Select current date
        self.select_current_date(0)
        
        # 2. Click checkbox/radio triggers
        logger.info("Clicking checkboxes and radio labels")
        self.label_5.click()
        self.radio_label_8.click()
        
        # 3. Date Picker 2 (index 1) -> Select current date
        self.select_current_date(1)
        
        # 4. Click checkbox/radio trigger
        logger.info("Clicking radio label 14")
        self.radio_label_14.click()
        
        # 5. Date Picker 3 (index 4) -> Select current date
        self.select_current_date(4)
        
        # 6. Fill comments
        if not comments_text:
            comments_text = self.fake.sentence()
        logger.info(f"Filling comments: '{comments_text}'")
        self.comments_input.click()
        self.comments_input.fill(comments_text)
        
        # 7. Click Save
        logger.info("Clicking Save button")
        self.save_button.click()
        self.page.wait_for_timeout(1000)
        
        # 8. Verify and accept confirmation dialog
        logger.info("Accepting confirmation dialog")
        expect(self.confirm_dialog).to_be_visible(timeout=10000)
        expect(self.confirm_text).to_be_visible(timeout=10000)
        self.ok_button.click()
        self.page.wait_for_timeout(2000)
        
        # 9. Verify the final section is visible
        expect(self.final_section).to_be_visible(timeout=15000)
        logger.info("Waiver Application details saved and verified successfully")
