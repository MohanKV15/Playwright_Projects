import logging
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AccountManagementPage(BasePage):
    """
    Page Object Model for Account Management in Staff Portal E-Permitting System.
    Handles searching company/designer/engineer firms, adding new applicants with fake data,
    and editing existing records from the applicant table.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Headings ──────────────────────────────────────────────
        self.account_management_link = page.get_by_role("link", name="Account Management").or_(
            page.locator("a:has-text('Account Management')")
        ).first

        self.page_heading = page.get_by_role("heading", name="Company/Designer/Engineer").or_(
            page.locator("h1:has-text('Company/Designer/Engineer'), h2:has-text('Company/Designer/Engineer'), h3:has-text('Company/Designer/Engineer')")
        ).first

        self.form_wrapper = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12, #frmCustomer, .form-wrapper").first

        # ── Search Controls ───────────────────────────────────────────────────
        self.firm_search_input = page.get_by_role("textbox", name="Company/Designer/Engineer Firm").or_(
            page.locator("input[placeholder*='Company/Designer/Engineer Firm'], #FirmName, input[name*='Firm']")
        ).first

        self.search_button = page.get_by_role("button", name="Search").or_(
            page.locator("button:has-text('Search'), input[type='submit'][value='Search']")
        ).first

        # ── Add Applicant Controls ────────────────────────────────────────────
        self.add_applicant_button = page.get_by_role("button", name=" Add Applicant").or_(
            page.get_by_role("button", name="Add Applicant")
        ).or_(
            page.locator("button:has-text('Add Applicant'), a:has-text('Add Applicant')")
        ).first

        self.company_input = page.get_by_role("textbox", name="Company/Designer/Engineer").or_(
            page.locator("input[name*='Company'], #CompanyName")
        ).first

        self.modal_details_text = page.get_by_text("Company/Designer/Engineer Firm Details Save Cancel Company/Designer/Engineer").or_(
            page.get_by_role("heading", name="Company/Designer/Engineer Firm Details")
        ).or_(
            page.locator("form:visible, .form-wrapper:visible")
        ).first

        self.city_input = page.get_by_role("textbox", name="City").or_(
            page.locator("input[name*='City'], #City")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(
            page.locator("button:has-text('Save')")
        ).first

        # ── Table Locators ────────────────────────────────────────────────────
        self.table_rows = page.locator("#frmCustomer table tbody tr, .k-grid table tbody tr, table tbody tr")

    # ── Actions & Workflows ───────────────────────────────────────────────────

    def navigate_to_account_management(self) -> None:
        """Navigates to the Account Management page."""
        logger.info("Navigating to Account Management section.")
        self._wait_for_loader()
        self.safe_click(self.account_management_link)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_account_management_loaded(self) -> None:
        """Validates that the Account Management page header and form wrapper are visible."""
        logger.info("Verifying Account Management layout.")
        expect(self.page_heading).to_be_visible(timeout=15000)
        expect(self.form_wrapper).to_be_visible(timeout=15000)

    def search_firm(self, firm_name: str) -> None:
        """Searches for a firm by name."""
        logger.info(f"Searching for firm: '{firm_name}'")
        if not self.firm_search_input.is_visible():
            logger.info("Search input not visible. Returning to Account Management main page.")
            self.navigate_to_account_management()

        self._wait_for_loader()
        self.firm_search_input.click()
        self.firm_search_input.fill(firm_name)
        self.js_click(self.search_button)
        self._wait_for_loader()
        expect(self.form_wrapper).to_be_visible(timeout=15000)

    def clear_search(self) -> None:
        """Clears search input and refreshes search results."""
        logger.info("Clearing search filter.")
        if not self.firm_search_input.is_visible():
            self.navigate_to_account_management()

        self._wait_for_loader()
        self.firm_search_input.click()
        self.firm_search_input.fill("")
        self.js_click(self.search_button)
        self._wait_for_loader()
        expect(self.form_wrapper).to_be_visible(timeout=15000)

    def click_add_applicant(self) -> None:
        """Clicks the 'Add Applicant' button."""
        logger.info("Clicking 'Add Applicant' button.")
        self._wait_for_loader()
        self.safe_click(self.add_applicant_button)
        self._wait_for_loader()

    def fill_and_save_applicant(self, company_name: str, city: str) -> None:
        """
        Fills the applicant form with company name and city, verifies details container, and saves.
        """
        logger.info(f"Filling applicant form - Company: '{company_name}', City: '{city}'")
        self.company_input.click()
        self.company_input.fill(company_name)
        expect(self.modal_details_text).to_be_visible(timeout=10000)
        self.city_input.click()
        self.city_input.fill(city)

        logger.info("Saving applicant details.")
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.page.wait_for_load_state("domcontentloaded")
        if self.form_wrapper.is_visible():
            expect(self.form_wrapper).to_be_visible(timeout=15000)

    def get_first_row_name(self) -> str:
        """Dynamically extracts the name of the first record in the table grid."""
        if not self.firm_search_input.is_visible():
            self.navigate_to_account_management()

        self._wait_for_loader()
        first_row = self.table_rows.first
        first_row.wait_for(state="visible", timeout=10000)
        first_cell = first_row.locator("td").first
        if first_cell.is_visible():
            name = first_cell.inner_text().strip()
        else:
            name = first_row.inner_text().strip()

        logger.info(f"Extracted 1st record name from table: '{name}'")
        return name

    def edit_first_record(self) -> None:
        """Edits the first record in the applicant table using #btnDelearListEdit."""
        logger.info("Editing the first record in the table.")
        if not self.firm_search_input.is_visible():
            self.navigate_to_account_management()

        self._wait_for_loader()
        first_edit_btn = self.page.locator("#btnDelearListEdit").first
        self.js_click(first_edit_btn)
        self._wait_for_loader()

    def search_first_record_refresh_and_edit(self) -> None:
        """
        Dynamically extracts the 1st record's name from table, searches for it in search box,
        clears search (refreshes), and edits the 1st record.
        """
        first_name = self.get_first_row_name()
        self.search_firm(first_name)
        self.clear_search()
        self.edit_first_record()
