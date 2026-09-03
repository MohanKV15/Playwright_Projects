import logging
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class InspectionPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation/Sidebar Link
        self.inspection_menu_link = page.get_by_role("link", name="Inspection")
        
        # Validation locators
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.partial_form = page.locator("#partial-form").first
        self.partial_form_section_div = page.locator("#partial-form > section > div > div").first
        
        # Action Buttons
        self.add_new_button = page.get_by_role("button", name=" Add New")
        
        # Form inputs
        self.dropdown_triggers = page.get_by_text("--Select--")
        self.date_picker_button = page.get_by_role("button", name="select").first
        self.focused_date_link = page.get_by_label("Current focused date is").get_by_role("link")
        
        self.raa_reason_input = page.get_by_role("textbox", name="RAA Reason")
        self.zoning_comments_input = page.get_by_role("textbox", name="Zoning Comments")
        self.njdot_comments_input = page.get_by_role("textbox", name="NJDOT Comments")
        
        # Kendo UI Modals & Buttons
        self.save_button = page.get_by_role("button", name=" Save")
        self.kendo_ok_button = page.get_by_role("button", name="OK")
        self.inspection_grid_div = page.locator("#inspectionGridDiv > div:nth-child(3)")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_inspection_tab(self) -> None:
        """Navigates to the Inspection tab by clicking the sidebar link."""
        logger.info("Navigating to the Inspection tab")
        
        # Ensure navigation menu is expanded so that sidebar submenus are visible
        self._expand_navigation_menu()
        
        self.inspection_menu_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        expect(self.application_details_heading).to_be_visible(timeout=15000)

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option']")
        self.page.wait_for_timeout(500)
        
        # Typically the first option (index 0) might be '--Select--' placeholder or empty.
        # We try to click the first real option (index 1), if not available click index 0.
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            options.nth(1).click()
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            options.nth(0).click()
        self.page.wait_for_timeout(500)

    def select_date(self) -> None:
        """Opens date picker and selects the focused date."""
        logger.info("Opening date picker")
        self.date_picker_button.click()
        self.page.wait_for_timeout(500)
        
        try:
            self.focused_date_link.first.click(timeout=3000)
            logger.info("Selected focused/first available date in date picker")
        except Exception:
            # Fallback to date link with name "4"
            logger.warning("Could not click focused date, trying fallback date link '4'")
            self.page.get_by_label("Current focused date is").get_by_role("link", name="4").click()
        self.page.wait_for_timeout(500)

    def upload_inspection_document(self, file_path: str | None = None) -> None:
        """Uploads a file to the Kendo Upload element if present."""
        import os
        from utils.config import Config
        if not file_path or not os.path.exists(file_path):
            file_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")

        logger.info(f"Attempting to upload file: {file_path}")
        try:
            file_input = self.page.locator("input[type='file']").first
            # Wait a brief moment for it to attach
            file_input.wait_for(state="attached", timeout=3000)
            file_input.set_input_files(file_path)
            self.page.wait_for_timeout(2000)
            logger.info("File upload successfully triggered")
        except Exception as e:
            logger.warning(f"File upload element not found or upload bypassed: {e}")

    def add_new_inspection(self, file_path: str = None) -> None:
        """Clicks 'Add New' to open the inspection form and fill it."""
        logger.info("Adding a new inspection record")
        
        # Verify form elements are loaded before click
        expect(self.partial_form).to_be_visible(timeout=10000)
        expect(self.partial_form_section_div).to_be_visible(timeout=10000)
        
        self.add_new_button.click()
        self.page.wait_for_timeout(1000)
        
        # 1. Inspector Dropdown
        logger.info("Selecting Inspector dropdown")
        self.dropdown_triggers.first.click()
        self._select_first_dropdown_option()
        
        # 2. Select Date
        self.select_date()
        
        # Click outer element to dismiss calendar (if applicable)
        try:
            self.page.locator(".col-md-3 > div:nth-child(3)").first.click(timeout=1000)
        except Exception:
            pass
        
        # 3. RAA Reason
        logger.info("Filling RAA Reason")
        self.raa_reason_input.click()
        self.raa_reason_input.fill(self.fake.sentence())
        
        # 4. Zoning / Inspection Type Dropdowns
        logger.info("Selecting Zoning type dropdown")
        self.page.locator("#tcInspectionfrm").get_by_text("--Select--").click()
        self._select_first_dropdown_option()

        logger.info("Selecting Type of Inspection dropdown")
        self.page.locator("#tcInspectionfrm").get_by_text("----Select type of Inspection----").click()
        self._select_first_dropdown_option()
        
        # 5. Comments
        logger.info("Filling Zoning and NJDOT Comments")
        self.zoning_comments_input.click()
        self.zoning_comments_input.fill(self.fake.sentence())
        
        self.njdot_comments_input.click()
        self.njdot_comments_input.fill(self.fake.sentence())
        
        # 6. File upload (optional)
        if file_path:
            self.upload_inspection_document(file_path)

        # 7. Save the modal form
        logger.info("Saving the inspection entry modal form")
        self.save_button.click()
        
        # Expect confirmation modal
        expect(self.page.get_by_text("Record saved successfully")).to_be_visible(timeout=15000)
        self.kendo_ok_button.click()
        self.page.wait_for_timeout(1000)

        # 8. Save the page level changes
        logger.info("Saving the page level changes")
        self.save_button.click()
        self.kendo_ok_button.click()
        self.page.wait_for_timeout(1000)

    def verify_inspection_record_in_grid(self) -> None:
        """Clicks the Inspection tab/link and verifies that the grid displays the record."""
        logger.info("Verifying the inspection record is visible in the grid")
        self.inspection_menu_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        expect(self.inspection_grid_div).to_be_visible(timeout=15000)
