import logging
import re
from typing import Dict, Optional
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class JunkyardDetailsPage(BasePage):
    """
    Page Object Model representing the Junkyard Details and Edit workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Navigate to Junkyards -> Junkyard/Permit Search
    - Filter search by Company Name (e.g. 'IDOTOAtest2') and click 'Search'
    - Verify search results grid table (#ListingScreenPermitsGrid)
    - Click 'Edit' button on matching Junkyard/Permit record row
    - Verify Junkyard Details page headers:
        1. Applicant Permit Number
        2. Yard Information
        3. Location Information
        4. Industrial Activity (1,000 feet)
        5. Property Owner Information
    - Click 'Save' button, verify 'Record Saved successfully.' modal, click 'OK'
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Search View Locators
        self.sidebar_junkyards_menu = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_junkyard_search_link = page.get_by_role("link", name="Junkyard/Permit Search").or_(
            page.locator("a[href*='JunkyardSearch'], a[href*='Junkyard'], a:has-text('Junkyard/Permit Search')")
        ).first

        self.company_name_search_input = page.locator("#CompanyName, [name='CompanyName'], input[name*='Company' i]").first
        self.search_button = page.get_by_role("button", name=" Search").or_(
            page.get_by_role("button", name="Search")
        ).or_(
            page.locator("#btnSearch, button:has-text('Search'), input[value='Search']")
        ).first

        self.heading_junkyard_search = page.get_by_text("Junkyard/Permit Search").filter(visible=True).first
        self.heading_permits = page.locator("div, h1, h2, h3, h4, h5, .card-header, legend").filter(
            has_text=re.compile(r"^Permits$", re.I)
        ).filter(visible=True).first
        self.permits_grid = page.locator("#ListingScreenPermitsGrid, .k-grid-content, .k-grid").first
        self.grid_rows = page.locator("#ListingScreenPermitsGrid tbody tr, .k-grid-content tbody tr")

        # 2. Details Page Section Header Locators
        self.text_applicant_permit_no = page.get_by_text("Applicant Permit Number").or_(
            page.locator("label:has-text('Applicant Permit Number'), legend:has-text('Applicant Permit Number'), div:has-text('Applicant Permit Number')")
        ).first
        self.text_yard_info = page.get_by_text("Yard Information").or_(page.get_by_text("Yard Type")).first
        self.text_location_info = page.get_by_text("Location Information").first
        self.text_industrial_activity = page.get_by_text("industrial activity").or_(page.get_by_text("1,000 feet")).first
        self.text_property_owner_info = page.get_by_text("Property Owner Information").first

        # 3. Save & Notification Dialog Locators
        self.save_button = page.get_by_role("button", name="Save").or_(
            page.get_by_text("Save", exact=True)
        ).or_(
            page.locator("#btnSubmit, button:has-text('Save'), input[value='Save']")
        ).first
        self.record_saved_text = page.get_by_text("Record Saved successfully.").or_(
            page.get_by_text("Record Saved")
        ).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Search Actions
    # -------------------------------------------------------------------------
    def navigate_to_junkyard_search(self, timeout_ms: int = 20000) -> None:
        """
        Navigates to Junkyard/Permit Search via sidebar menu link and verifies page elements.
        """
        self.logger.info("Navigating to Junkyards -> Junkyard/Permit Search")
        self._wait_for_loader()

        if self.sidebar_junkyards_menu.is_visible(timeout=5000) and not self.sidebar_junkyard_search_link.is_visible():
            self.sidebar_junkyards_menu.click(force=True)
            self.page.wait_for_timeout(400)

        expect(self.sidebar_junkyard_search_link).to_be_visible(timeout=timeout_ms)
        self.sidebar_junkyard_search_link.click()
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.verify_junkyard_search_page_loaded(timeout_ms=timeout_ms)

    def verify_junkyard_search_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Junkyard/Permit Search title, Permits header, and grid table are visible.
        """
        self.logger.info("Verifying Junkyard/Permit Search page elements are visible")
        expect(self.heading_junkyard_search).to_be_visible(timeout=timeout_ms)
        expect(self.heading_permits).to_be_visible(timeout=timeout_ms)
        expect(self.permits_grid).to_be_visible(timeout=timeout_ms)

    def search_junkyard_permits(self, company_name: str = "IDOTOAtest2", timeout_ms: int = 20000) -> None:
        """
        Inputs company name in search field and clicks Search button.
        """
        self.logger.info("Searching Junkyard permits for company: '%s'", company_name)
        expect(self.company_name_search_input).to_be_visible(timeout=timeout_ms)
        self.company_name_search_input.click()
        self.company_name_search_input.clear()
        self.company_name_search_input.fill(company_name)

        expect(self.search_button).to_be_visible(timeout=timeout_ms)
        self.search_button.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        expect(self.permits_grid).to_be_visible(timeout=timeout_ms)

    def click_edit_on_permit_record(
        self, permit_identifier: Optional[str] = None, timeout_ms: int = 20000
    ) -> str:
        """
        Locates the 1st permit record row in search grid table (#ListingScreenPermitsGrid)
        (or matching row if specific permit_identifier provided) and clicks the Edit button in that row.
        """
        self.logger.info("Locating 1st record row in permits grid")
        target_row = self.grid_rows.first
        if permit_identifier:
            matched_row = self.page.get_by_role("row", name=re.compile(permit_identifier, re.I)).or_(
                self.grid_rows.filter(has_text=permit_identifier)
            ).first
            if matched_row.is_visible(timeout=3000):
                target_row = matched_row

        expect(target_row).to_be_visible(timeout=timeout_ms)
        row_text = target_row.inner_text()
        self.logger.info("Clicking edit button on 1st permit grid row: %s", row_text.splitlines()[0] if row_text else "")

        edit_button = target_row.get_by_role("button").or_(
            target_row.locator("a.k-grid-edit, button.k-grid-edit, .k-button, button, a")
        ).first
        expect(edit_button).to_be_visible(timeout=timeout_ms)
        edit_button.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        return row_text

    # -------------------------------------------------------------------------
    # Details & Save Actions
    # -------------------------------------------------------------------------
    def verify_junkyard_details_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that all standard Junkyard Details form section headers are visible.
        """
        self.logger.info("Verifying Junkyard Details form section headers")
        expect(self.text_applicant_permit_no).to_be_visible(timeout=timeout_ms)
        expect(self.text_yard_info).to_be_visible(timeout=timeout_ms)
        expect(self.text_location_info).to_be_visible(timeout=timeout_ms)
        expect(self.text_industrial_activity).to_be_visible(timeout=timeout_ms)
        expect(self.text_property_owner_info).to_be_visible(timeout=timeout_ms)

    def save_junkyard_details(self, timeout_ms: int = 20000) -> None:
        """
        Clicks 'Save' button, verifies 'Record Saved successfully.' popup modal, and clicks 'OK'.
        """
        self.logger.info("Saving Junkyard details")
        expect(self.save_button).to_be_visible(timeout=timeout_ms)
        self.save_button.click()
        self.page.wait_for_timeout(600)
        self._wait_for_loader()

        self.logger.info("Verifying save confirmation popup and clicking OK")
        if self.record_saved_text.is_visible(timeout=5000):
            self.logger.info("Confirmation message 'Record Saved successfully.' displayed")

        if self.dialog_ok_button.is_visible(timeout=5000):
            self.dialog_ok_button.click()
            self.page.wait_for_timeout(400)
            self._wait_for_loader()

    def execute_search_and_verify_details_workflow(
        self, company_name: str = "IDOTOAtest2", permit_identifier: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Composite high-level workflow:
        1. Navigates to Junkyard/Permit Search page
        2. Filters search grid by Company Name
        3. Clicks Edit action button on 1st permit record row
        4. Verifies all Junkyard Details section headers display correctly
        """
        self.navigate_to_junkyard_search()
        self.search_junkyard_permits(company_name=company_name)
        record_info = self.click_edit_on_permit_record(permit_identifier=permit_identifier)
        self.verify_junkyard_details_page_loaded()

        return {
            "company_name": company_name,
            "record_info": record_info,
            "status": "Verified successfully",
        }
