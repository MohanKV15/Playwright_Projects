import logging
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class ApplicationDetailsPage(BasePage):
    """
    Page Object Model representing the Application Details and Company Search workflow
    in the IDOT Outdoor Advertising Staff Portal.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Company Search & Grid Locators
        self.company_name_input = page.get_by_role("textbox", name="Company Name").or_(
            page.locator("#CompanyName, [name='CompanyName'], input[name*='Company' i]")
        ).first
        self.search_button = page.get_by_role("button", name=" Search").or_(
            page.locator("button:has-text('Search')")
        ).first
        self.permit_grid_rows = page.locator("#PermitListGrid tbody tr:not(.k-no-data)")

        # 2. Application / Permits Navigation Menu
        self.app_permits_menu = page.get_by_role("link", name="Application/Permits ").or_(
            page.get_by_role("link", name="Application/Permits")
        ).first
        self.app_details_menu_link = page.get_by_role("link", name="Application Details").first

        # 3. Application Details Form Elements
        self.partial_form = page.locator("#partial-form")
        self.sign_info_section = page.get_by_text("Sign Information Erection").first
        self.airport_restrictions_section = page.get_by_text("Airport Restrictions Is the").first
        self.location_info_section = page.get_by_text("Location Information Maps").first
        self.unzoned_area_info = page.get_by_text(
            "Is sign located in an unzoned area? Yes No Is the sign located within 600 feet"
        ).first
        self.sign_distance_info = page.get_by_text("Sign will be located 100-199").first
        self.property_owner_section = page.get_by_text(
            "Property Owner Information Property Owner Name Property Owner Address 1"
        ).first
        self.attachments_section = page.get_by_text("Attachments Proof of land").first

        # 4. Save & Confirmation Popups
        self.save_button = page.locator(".float-right, #btnSubmit, button:has-text('Save')").first
        self.confirmation_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), .modal:visible button:has-text('OK'), .ajs-ok, button:has-text('OK'), button:has-text('Ok')")
        ).first

    # -------------------------------------------------------------------------
    # Search Actions
    # -------------------------------------------------------------------------
    def search_by_company(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Fills the Company Name search field and initiates search.
        Reusable for all company-based search queries across staff records.
        """
        self.logger.info(f"Searching applications by company: '{company_name}'")
        self._wait_for_loader()
        expect(self.company_name_input).to_be_visible(timeout=20000)
        self.company_name_input.click()
        self.company_name_input.clear()
        self.company_name_input.fill(company_name)
        expect(self.search_button).to_be_visible(timeout=10000)
        self.search_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

    def select_first_record_and_open_details(self) -> str:
        """
        Selects the 1st record row in the search results table, clicks its action/edit button,
        and navigates to the Application Details view.
        Returns the row's text or identifier for verification.
        """
        self.logger.info("Selecting first matching record row from grid")
        self._wait_for_loader()
        expect(self.permit_grid_rows.first).to_be_visible(timeout=25000)
        first_row = self.permit_grid_rows.first
        record_info = first_row.inner_text().strip()
        self.logger.info(f"First record details: {record_info}")

        # Click the action button on the 1st record row
        action_btn = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        # Navigate via sidebar: Application/Permits -> Application Details
        self.logger.info("Navigating to Application Details view via sidebar menu")
        expect(self.app_permits_menu).to_be_visible(timeout=15000)
        self.app_permits_menu.click(force=True)
        self.page.wait_for_timeout(500)

        expect(self.app_details_menu_link).to_be_visible(timeout=15000)
        self.app_details_menu_link.click(force=True)
        self._wait_for_loader()

        # Wait until #partial-form is loaded
        expect(self.partial_form).to_be_visible(timeout=30000)
        self.logger.info("Application Details page loaded successfully")
        return record_info

    # -------------------------------------------------------------------------
    # Verification Actions
    # -------------------------------------------------------------------------
    def verify_all_application_details_sections(self, timeout_ms: int = 20000) -> None:
        """
        Validates that all core Application Details sections and informational headings are visible:
        - #partial-form container
        - Sign Information
        - Airport Restrictions (expands if accordion)
        - Location Information
        - Unzoned area notice
        - Sign distance notice (100-199)
        - Property Owner Information
        - Attachments
        """
        self.logger.info("Verifying all Application Details sections and headings")
        expect(self.partial_form).to_be_visible(timeout=timeout_ms)
        expect(self.sign_info_section).to_be_visible(timeout=timeout_ms)

        # Expand Airport Restrictions section if collapsable
        expect(self.airport_restrictions_section).to_be_visible(timeout=timeout_ms)
        self.airport_restrictions_section.click()
        self.page.wait_for_timeout(300)

        expect(self.location_info_section).to_be_visible(timeout=timeout_ms)
        expect(self.unzoned_area_info).to_be_visible(timeout=timeout_ms)
        expect(self.sign_distance_info).to_be_visible(timeout=timeout_ms)
        expect(self.property_owner_section).to_be_visible(timeout=timeout_ms)
        expect(self.attachments_section).to_be_visible(timeout=timeout_ms)
        self.logger.info("All Application Details sections validated successfully")

    # -------------------------------------------------------------------------
    # Submission / Save Actions
    # -------------------------------------------------------------------------
    def save_and_confirm_application(self, timeout_ms: int = 20000) -> None:
        """
        Clicks the Save button (.float-right), waits for the confirmation dialog,
        and clicks the modal OK button to confirm saving.
        """
        self.logger.info("Saving Application Details (.float-right button)")
        self._wait_for_loader()
        expect(self.save_button).to_be_visible(timeout=timeout_ms)

        # Attach native dialog handler in case browser alert/confirm pops up
        dialog_handled = []

        def handle_dialog(dialog):
            self.logger.info(f"Handled native dialog: '{dialog.message}'")
            dialog_handled.append(dialog.message)
            dialog.accept()

        self.page.once("dialog", handle_dialog)

        self.save_button.scroll_into_view_if_needed()
        self.save_button.click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Check for DOM modal OK button
        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), "
            ".k-alert:visible button:has-text('OK'), "
            ".k-window:visible button:has-text('OK'), "
            ".modal:visible button:has-text('OK'), "
            ".ajs-ok, .ajs-button.ajs-ok, "
            "button:has-text('OK'), button:has-text('Ok')"
        ).first

        if ok_btn.is_visible(timeout=5000):
            self.logger.info("Confirming Save on modal popup dialog (OK button)")
            ok_btn.click(force=True)
            self._wait_for_loader()
        elif dialog_handled:
            self.logger.info(f"Save confirmed via native browser dialog: '{dialog_handled[0]}'")
        else:
            self.logger.info("Save executed directly (no additional OK modal was displayed)")
        self.logger.info("Application Details saved and confirmed successfully")
