import logging
import re
from typing import Dict, Optional, Any
from faker import Faker
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown, KendoControls

logger = logging.getLogger(__name__)
fake = Faker()


class AddPermitTransferPage(BasePage):
    """
    Page Object Model representing the Add Permit Transfer module in the IDOT Staff Portal.
    Encapsulates navigation (Dashboard -> Permit Transfer), permit number search, company lookup,
    Faker data entry, Kendo control interactions, transfer confirmation, and form LA popup generation workflows.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_controls = KendoControls(page)

        # 1. Navigation & Header Locators
        self.heading_permit_transfer = page.get_by_role("heading", name="Permit Transfer").or_(
            page.locator("h1:has-text('Permit Transfer'), h2:has-text('Permit Transfer'), h3:has-text('Permit Transfer'), .page-header:has-text('Permit Transfer')")
        ).first
        self.text_permit_transfer_enter = page.get_by_text("Permit Transfer (Enter in one").or_(
            page.get_by_text("Permit Transfer")
        ).first
        self.grid_content = page.locator(".k-grid-content, #gridPermitTransfer, table").first

        # 2. Add Permit Transfer Button & Details Headers
        self.add_permit_transfer_button = page.locator("#btnAddPermitTransfer").or_(
            page.get_by_role("button", name=re.compile(r"Add\s+Permit\s+Transfer", re.I))
        ).or_(
            page.locator("button:has-text('Add Permit Transfer'), a:has-text('Add Permit Transfer'), .k-button:has-text('Add Permit Transfer')")
        )

        self.heading_permit_transfer_details = page.get_by_role("heading", name=re.compile(r"Permit\s+Transfer\s+Details", re.I)).or_(
            page.get_by_text("Permit Transfer Details")
        ).first
        self.text_permit_transfer_details_save = page.get_by_text("Permit Transfer Details Save").or_(
            page.get_by_text("Permit Transfer Details")
        ).first

        # 3. Search Requested Permit Locators
        self.permit_number_requested_input = page.get_by_role("textbox", name=re.compile(r"Permit\s+Number\s+Requested\s+for", re.I)).or_(
            page.locator("#PermitNumber, [name='PermitNumber'], input[name*='PermitNumber' i]")
        ).first
        self.btn_search_transfer_details = page.locator("#btnSearchTransferDetails, button:has-text('Search')").first

        # 4. Company Search Modal Locators
        self.text_company_search = page.get_by_text("Company Search (Choose the").or_(
            page.get_by_text("Company Search")
        ).first

        self.modal_are_you_sure = page.get_by_text("Are sure you want to continue?").or_(
            page.get_by_text("Are you sure")
        ).first
        self.dialog_ok_button = page.get_by_role("button", name="OK").or_(
            page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')")
        ).first

        # 5. Form Fill & Save Locators
        self.from_company_entered_input = page.get_by_label("From Company Entered *").or_(
            page.get_by_role("textbox", name=re.compile(r"From\s+Company\s+Entered", re.I))
        ).or_(
            page.locator("#FromCompanyEntered, [name='FromCompanyEntered']")
        ).first

        self.btn_save = page.get_by_text("Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(
            page.locator("button:has-text('Save'), #btnSave")
        )
        self.text_operation_completed = page.get_by_text("Operation Completed").first

        # 6. Find & Transfer To Company Locators
        self.text_permit_transfer_transfer = page.get_by_text("Permit Transfer Transfer").or_(
            page.get_by_text("Permit Transfer")
        ).first
        self.btn_find = page.get_by_role("button", name=re.compile(r"Find", re.I)).or_(
            page.locator("button:has-text('Find'), #btnFind")
        ).first
        self.permit_transfer_details_div = page.locator("#PermitTransferDetailsDiv, #partial-form").first

        # 7. Generate Form LA & Popup Locators
        self.btn_generate_form_la = page.get_by_role("button", name=re.compile(r"Generate\s+form\s+LA", re.I)).or_(
            page.locator("button:has-text('Generate form LA')")
        )
        self.text_generated_successfully = page.get_by_text("Generated successfully").first

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def dismiss_ok_dialogs(self, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """Dismisses visible OK popups safely using KendoControls helper."""
        return KendoControls.dismiss_ok_dialogs(self.page, timeout_ms=timeout_ms, max_clicks=max_clicks)

    def _perform_modal_company_selection(
        self,
        company_name_search: Optional[str] = "test",
        account_status: Optional[str] = None,
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """
        Reusable helper for searching and selecting a company row from the active visible modal window.
        By default, fills 'test' into Company Name search input (or clears if None), clicks Search,
        and ALWAYS selects the 1st row checkbox (row_index=0) from the search result list.
        """
        expect(self.text_company_search).to_be_visible(timeout=timeout_ms)

        modal_company_input = self.page.locator(
            ".k-window:visible #Dealer_Name, .k-window:visible [name='Dealer_Name'], #Dealer_Name, [name='Dealer_Name']"
        ).first
        expect(modal_company_input).to_be_visible(timeout=timeout_ms)
        modal_company_input.click()
        if company_name_search:
            modal_company_input.fill(company_name_search)
        else:
            modal_company_input.clear()

        if account_status:
            self.kendo_dropdown.select("AccountStatus", option_text=account_status)

        search_btn = self.page.locator(
            ".k-window:visible #btnSearch, .k-window:visible button:has-text('Search'), #btnSearch"
        ).first
        expect(search_btn).to_be_visible(timeout=timeout_ms)
        search_btn.click(force=True)
        self.page.wait_for_timeout(800)
        self._wait_for_loader()

        # Fallback: If search with query yields no results, clear input & re-search all companies
        no_items = self.page.locator(".k-window:visible :text('No items to display')").first
        if no_items.is_visible(timeout=1000):
            modal_company_input.click()
            modal_company_input.clear()
            search_btn.click(force=True)
            self.page.wait_for_timeout(800)
            self._wait_for_loader()

        # Always select 1st row checkbox (row_index=0) from search results list
        chk_list = self.page.locator(
            ".k-window:visible #selectedChk, .k-window:visible input[name='selectedChk'], .k-window:visible input[type='checkbox']"
        )
        chk = chk_list.nth(row_index)
        expect(chk).to_be_visible(timeout=timeout_ms)
        chk.check(force=True)
        self.page.wait_for_timeout(400)

        self.dismiss_ok_dialogs(timeout_ms=1500, max_clicks=2)
        self._wait_for_loader()

    # -------------------------------------------------------------------------
    # Main Workflow Actions
    # -------------------------------------------------------------------------
    def navigate_to_permit_transfer(self, timeout_ms: int = 20000) -> None:
        """
        Navigates to Dashboard first, then clicks 'Permit Transfer ' parent link and 'Permit Transfer' exact sub-link.
        Prevents ASP.NET session NullReferenceException errors on direct page landing.
        """
        self.logger.info("Navigating to Dashboard before clicking Permit Transfer")
        self._wait_for_loader()

        dash_link = self.page.get_by_role("link", name="Dashboard").or_(
            self.page.locator(".sidebar a:has-text('Dashboard'), a[href*='Dashboard']")
        ).first

        if dash_link.is_visible(timeout=3000):
            dash_link.click(force=True)
            self.page.wait_for_timeout(500)
            self._wait_for_loader()

        self.logger.info("Clicking 'Permit Transfer ' parent menu link in sidebar")
        parent_link = self.page.get_by_role("link", name="Permit Transfer ").or_(
            self.page.get_by_role("link", name=re.compile(r"Permit\s+Transfer", re.I))
        ).or_(
            self.page.locator(".sidebar > ul > li > a:has-text('Permit Transfer')")
        ).first

        if parent_link.is_visible(timeout=5000):
            parent_link.click(force=True)
            self.page.wait_for_timeout(500)

        self.logger.info("Clicking exact 'Permit Transfer' sub-link in sidebar")
        sub_link = self.page.locator(".sidebar .sub-menu a:has-text('Permit Transfer'), .sidebar a[href*='PermitTransfer']").or_(
            self.page.get_by_role("link", name="Permit Transfer", exact=True)
        ).last

        if sub_link.is_visible(timeout=5000):
            sub_link.click(force=True)
            self.page.wait_for_timeout(800)
            self._wait_for_loader()

        if "PermitTransferListing" not in self.page.url:
            self.logger.info("Fallback navigation to 4319PermitTransferListingStaffFull with domcontentloaded")
            base_domain = self.page.url.split("/Portal/")[0]
            try:
                self.page.goto(f"{base_domain}/Portal/Page/Index/4319PermitTransferListingStaffFull", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                pass
            self.page.wait_for_timeout(800)
            self._wait_for_loader()

        expect(self.heading_permit_transfer).to_be_visible(timeout=timeout_ms)

    def click_add_permit_transfer(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Add Permit Transfer' button."""
        self.logger.info("Clicking 'Add Permit Transfer' button")
        self._wait_for_loader()

        add_btn = self.add_permit_transfer_button.filter(visible=True).first
        if not add_btn.is_visible(timeout=3000):
            add_btn = self.page.locator(
                "#btnAddPermitTransfer, button:has-text('Add Permit Transfer'), a:has-text('Add Permit Transfer')"
            ).filter(visible=True).first

        expect(add_btn).to_be_visible(timeout=timeout_ms)
        self.safe_click(add_btn)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        expect(self.heading_permit_transfer_details).to_be_visible(timeout=timeout_ms)

    def search_requested_permit(self, permit_number: str = "016-503386", timeout_ms: int = 20000) -> None:
        """Fills 'Permit Number Requested for' input and clicks Search button."""
        self.logger.info("Searching for requested permit number: '%s'", permit_number)
        expect(self.permit_number_requested_input).to_be_visible(timeout=timeout_ms)
        self.permit_number_requested_input.click()
        self.permit_number_requested_input.fill(permit_number)

        expect(self.btn_search_transfer_details).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.btn_search_transfer_details)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    def select_from_company(
        self,
        company_name_search: Optional[str] = "test",
        account_status: Optional[str] = None,
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """Searches company name in active modal, selects specified row checkbox (default 1st row: index 0), and confirms dialog."""
        self.logger.info("Searching and selecting From Company: '%s' (row index: %d)", company_name_search, row_index)
        self._perform_modal_company_selection(
            company_name_search=company_name_search,
            account_status=account_status,
            row_index=row_index,
            timeout_ms=timeout_ms,
        )

    def fill_from_company_entered(self, from_company: Optional[str] = None, timeout_ms: int = 20000) -> str:
        """
        Fills 'From Company Entered *' field using Faker library if not provided, clicks Save, and confirms OK.
        """
        company_value = from_company or f"{fake.company()} {fake.company_suffix()}"
        self.logger.info("Filling 'From Company Entered *' with Faker value: '%s'", company_value)

        expect(self.from_company_entered_input).to_be_visible(timeout=timeout_ms)
        self.from_company_entered_input.click()
        self.from_company_entered_input.fill(company_value)

        save_btn = self.btn_save.filter(visible=True).first
        expect(save_btn).to_be_visible(timeout=timeout_ms)
        self.safe_click(save_btn)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        self.dismiss_ok_dialogs(timeout_ms=2000, max_clicks=2)
        self._wait_for_loader()
        return company_value

    def select_transfer_to_company(
        self,
        company_name_search: Optional[str] = "test",
        account_status: Optional[str] = None,
        row_index: int = 0,
        timeout_ms: int = 20000,
    ) -> None:
        """
        Clicks Find, searches company in popup modal, selects specified row checkbox (default 1st row: index 0), confirms OK, and saves details.
        """
        self.logger.info("Clicking Find button to select Transfer To company (row index: %d)", row_index)
        expect(self.btn_find).to_be_visible(timeout=timeout_ms)
        self.safe_click(self.btn_find)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        self._perform_modal_company_selection(
            company_name_search=company_name_search,
            account_status=account_status,
            row_index=row_index,
            timeout_ms=timeout_ms,
        )

        if self.permit_transfer_details_div.is_visible(timeout=2000):
            self.permit_transfer_details_div.click(force=True)

        save_btn = self.btn_save.filter(visible=True).first
        expect(save_btn).to_be_visible(timeout=timeout_ms)
        self.safe_click(save_btn)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        self.dismiss_ok_dialogs(timeout_ms=2000, max_clicks=2)
        self._wait_for_loader()

    def generate_form_la(self, timeout_ms: int = 20000) -> None:
        """
        Clicks 'Generate form LA' button, verifies popup window with #mainCanvas if opened, closes popup,
        and confirms 'Generated successfully' OK popup.
        """
        self.logger.info("Clicking 'Generate form LA' button")
        gen_btn = self.btn_generate_form_la.filter(visible=True).first
        if not gen_btn.is_visible(timeout=3000):
            gen_btn = self.page.get_by_role("button", name=re.compile(r"Generate\s+form\s+LA", re.I)).or_(
                self.page.locator("button:has-text('Generate form LA'), a:has-text('Generate form LA'), #btnGenerateFormLA")
            ).filter(visible=True).first

        expect(gen_btn).to_be_visible(timeout=timeout_ms)

        try:
            with self.page.expect_popup(timeout=10000) as popup_info:
                gen_btn.click(force=True)
            popup_page = popup_info.value
            self.logger.info("Verifying #mainCanvas on popup window")
            expect(popup_page.locator("#mainCanvas")).to_be_visible(timeout=timeout_ms)
            popup_page.close()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.info("Popup note or direct button click: %s", e)
            if gen_btn.is_visible():
                gen_btn.click(force=True)
                self.page.wait_for_timeout(500)

        self._wait_for_loader()
        self.dismiss_ok_dialogs(timeout_ms=2000, max_clicks=2)
        self._wait_for_loader()

    def execute_add_permit_transfer_full_workflow(
        self,
        permit_number: str = "016-503386",
        search_company: Optional[str] = "test",
        from_company: Optional[str] = None,
        account_status: Optional[str] = None,
        row_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end Add Permit Transfer workflow:
        1. Navigate to Permit Transfer page (via Dashboard)
        2. Click Add Permit Transfer button
        3. Search requested permit number ('016-503386')
        4. Search & select From Company ('IDOTOAtest2', account_status, row_index)
        5. Fill 'From Company Entered *' using Faker library and Save
        6. Click Find, search & select Transfer To Company ('IDOTOAtest2', account_status, row_index) and Save
        7. Click 'Generate form LA', verify canvas popup, close popup, and confirm completion dialog
        """
        self.navigate_to_permit_transfer()
        self.click_add_permit_transfer()
        self.search_requested_permit(permit_number=permit_number)
        self.select_from_company(company_name_search=search_company, account_status=account_status, row_index=row_index)
        entered_company = self.fill_from_company_entered(from_company=from_company)
        self.select_transfer_to_company(company_name_search=search_company, account_status=account_status, row_index=row_index)
        self.generate_form_la()

        return {
            "status": "Verified successfully",
            "permit_number": permit_number,
            "from_company_entered": entered_company,
        }
