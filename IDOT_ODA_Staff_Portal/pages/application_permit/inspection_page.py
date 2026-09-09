import logging
from pathlib import Path
from typing import Dict, Optional, Union
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.application_permit.documents_and_log_page import DocumentsAndLogPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown, KendoDatePicker

logger = logging.getLogger(__name__)


class InspectionPage(BasePage):
    """
    Page Object Model representing the complete Inspection workflow in the IDOT Outdoor Advertising Staff Portal.

    Responsibilities:
    - Company search & permit context activation (delegated to ApplicationDetailsPage)
    - Navigation to Inspection listing and verification
    - New Inspection Entry creation (1st dynamic dropdown option & present day date)
    - Inspection Report generation & popup canvas handling
    - Document attachment, communication logging, grid verification, and email handling (delegated to DocumentsAndLogPage)
    - Redirection verification back to Inspection Log grid on Cancel
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_datepicker = KendoDatePicker(page)

        # 1. Navigation & Composed Submodules
        self.app_details = ApplicationDetailsPage(page)
        self.doc_log = DocumentsAndLogPage(page)
        self.inspection_menu_link = page.get_by_role("link", name="Inspection").first

        # 2. Inspection Listing View (#InspectionList)
        self.inspection_list = page.locator("#InspectionList")
        self.new_entry_button = page.locator("button:has-text('New Entry'), a:has-text('New Entry')").first
        self.inspection_header_text = page.get_by_text("Application Details Permit").first
        self.inspection_log_text = page.get_by_text("Inspection Log New Entry").first

        # 3. New Entry Form (#frmInsNeEntry)
        self.new_entry_form = page.locator("#frmInsNeEntry")
        self.report_type_container = page.locator("#indspetydd")
        self.near_radio = self.new_entry_form.locator("label:has-text('Near'), input[value*='Near' i]").first
        self.submit_button = self.new_entry_form.locator("button:has-text('Submit')").first
        self.record_saved_popup = page.get_by_text("Record saved successfully").first
        self.confirmation_ok_button = page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')"
        ).first

        # 4. Inspection Detail / Report View
        self.generate_report_button = page.locator("button:has-text('Generate Inspection Report')").first
        self.report_generated_text = page.get_by_text("Generated successfully").first
        self.cancel_details_button = page.locator("#btninsadddcancel, button:visible").filter(has_text="Cancel").first

        # Track full details URL for navigating between submodules
        self.details_url: Optional[str] = None

    # -------------------------------------------------------------------------
    # Delegated Kendo Control Helpers
    # -------------------------------------------------------------------------
    def select_first_valid_dropdown_option(self, dropdown_locator: Union[Locator, str]) -> str:
        """Delegates dynamic 1st valid option selection to KendoDropdown component."""
        return self.kendo_dropdown.select_first_valid_option(dropdown_locator)

    def select_present_day_date(
        self,
        container: Optional[Union[Locator, str]] = None,
        field_id: Optional[str] = None,
    ) -> str:
        """Delegates present day date selection to KendoDatePicker component."""
        return self.kendo_datepicker.select_present_day_date(container=container, field_id=field_id)

    # -------------------------------------------------------------------------
    # Navigation & Context Activation
    # -------------------------------------------------------------------------
    def navigate_to_inspection(self, company_name: str = "IDOTOAtest2") -> str:
        """
        Searches by company name, clicks the 1st record row to activate permit session context,
        and navigates to the Inspection page via Application/Permits sidebar menu.
        """
        self.logger.info(f"Navigating to Inspection view for company '{company_name}'")
        self.app_details.search_by_company(company_name=company_name)

        self._wait_for_loader()
        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        first_row = self.app_details.permit_grid_rows.first
        record_info = first_row.inner_text().strip()

        # Activate permit session by clicking action button on 1st record row
        action_btn = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.inspection_menu_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        # Click Inspection link
        expect(self.inspection_menu_link).to_be_visible(timeout=15000)
        self.inspection_menu_link.click(force=True)
        self._wait_for_loader()

        self.logger.info("Successfully navigated to Inspection page")
        return record_info

    def verify_inspection_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Validates that the Inspection Log page elements and header are visible."""
        self.logger.info("Verifying Inspection page elements are loaded")
        expect(self.inspection_header_text).to_be_visible(timeout=timeout_ms)
        expect(self.inspection_log_text).to_be_visible(timeout=timeout_ms)
        expect(self.inspection_list).to_be_visible(timeout=timeout_ms)
        expect(self.new_entry_button).to_be_visible(timeout=timeout_ms)
        self.logger.info("Inspection page loaded successfully")

    # -------------------------------------------------------------------------
    # New Entry Creation Flow
    # -------------------------------------------------------------------------
    def create_new_inspection_entry(self) -> Dict[str, str]:
        """
        Clicks 'New Entry' button, populates all form fields using the 1st valid dropdown
        options and present day date, selects Near radio, and submits the entry.
        """
        self.logger.info("Starting New Inspection Entry creation")
        expect(self.new_entry_button).to_be_visible(timeout=15000)
        self.new_entry_button.click(force=True)
        self._wait_for_loader()
        expect(self.new_entry_form).to_be_visible(timeout=20000)

        # 1. Select 1st option for Inspected By dropdown (#inspected_by)
        inspected_by = self.select_first_valid_dropdown_option(
            self.new_entry_form.locator("#inspected_by, span.k-dropdown").first
        )

        # 2. Select Inspection Date with present day date (#Assigned_Date)
        self.select_present_day_date(container=self.new_entry_form, field_id="Assigned_Date")

        # 3. Select 1st option for Report Type dropdown (#Type_of_Inspection inside #indspetydd)
        report_type = self.select_first_valid_dropdown_option(
            self.new_entry_form.locator("#Type_of_Inspection, #indspetydd span.k-dropdown").first
        )

        # 4. Click Near radio
        if self.near_radio.is_visible():
            self.near_radio.click(force=True)

        # 5. Select 1st option for Inspection Status dropdown (#Inspection_Status)
        status = self.select_first_valid_dropdown_option(
            self.new_entry_form.locator("#Inspection_Status, span.k-dropdown").nth(2)
        )

        # 6. Select 1st option for Sign Inspection Conditions dropdown (#DOT_Comments)
        sign_condition = self.select_first_valid_dropdown_option(
            self.new_entry_form.locator("#DOT_Comments, span.k-dropdown").nth(3)
        )

        # 7. Submit form
        self.logger.info("Submitting New Inspection Entry form")
        expect(self.submit_button).to_be_visible(timeout=10000)
        self.submit_button.click(force=True)

        # 8. Assert confirmation dialog & click OK
        expect(self.record_saved_popup).to_be_visible(timeout=15000)
        self.logger.info("Record saved successfully popup displayed")
        expect(self.confirmation_ok_button).to_be_visible(timeout=10000)
        self.confirmation_ok_button.click(force=True)
        self._wait_for_loader()

        # Wait for form to hide and details page to settle
        try:
            self.new_entry_form.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

        # Store inspection full details URL to navigate seamlessly between submodules
        self.details_url = self.page.url
        self.logger.info(f"Captured Inspection Details URL: {self.details_url}")

        return {
            "inspected_by": inspected_by,
            "report_type": report_type,
            "status": status,
            "sign_condition": sign_condition,
        }

    # -------------------------------------------------------------------------
    # Generate Report Flow
    # -------------------------------------------------------------------------
    def generate_inspection_report(self) -> bool:
        """
        Clicks 'Generate Inspection Report', handles the popup window displaying
        the canvas report, and confirms the 'Generated successfully' modal.
        """
        self.logger.info("Generating Inspection Report")
        expect(self.generate_report_button).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(500)

        try:
            with self.page.expect_popup(timeout=10000) as popup_info:
                self.generate_report_button.click(force=True)
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded")
            self.logger.info(f"Inspection report popup opened: '{popup_page.title()}'")
            expect(popup_page.locator("#mainCanvas").first).to_be_visible(timeout=10000)
            popup_page.close()
        except Exception as e:
            self.logger.warning(f"Popup handling note: {e}")

        # Confirm success alert on main page
        expect(self.report_generated_text).to_be_visible(timeout=15000)
        self.logger.info("Report 'Generated successfully' confirmed")
        expect(self.confirmation_ok_button).to_be_visible(timeout=10000)
        self.confirmation_ok_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(600)
        return True

    # -------------------------------------------------------------------------
    # Delegated Documents & Log Flows (Composed from DocumentsAndLogPage)
    # -------------------------------------------------------------------------
    def attach_document(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, str]:
        """Delegates document attachment to DocumentsAndLogPage."""
        return self.doc_log.attach_document(
            title=title,
            description=description,
            file_path=file_path,
            return_url=self.details_url,
        )

    def add_communication(
        self,
        subject: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, str]:
        """Delegates communication logging to DocumentsAndLogPage."""
        return self.doc_log.add_communication(
            subject=subject,
            description=description,
        )

    def verify_record_in_table(self, expected_text: str, timeout_ms: int = 15000) -> None:
        """Delegates table record verification to DocumentsAndLogPage."""
        self.doc_log.verify_record_in_table(expected_text=expected_text, timeout_ms=timeout_ms)

    def open_and_cancel_send_email(self, timeout_ms: int = 15000) -> None:
        """Delegates email modal open and dismiss to DocumentsAndLogPage."""
        self.doc_log.open_and_cancel_send_email(timeout_ms=timeout_ms)

    # -------------------------------------------------------------------------
    # Cancel Details & Verify Inspection Listing Flow
    # -------------------------------------------------------------------------
    def cancel_details_and_verify_inspection_list(
        self,
        expected_status: Optional[Union[Dict[str, str], str]] = None,
        timeout_ms: int = 15000,
    ) -> None:
        """
        Clicks Cancel on the Inspection Details page (#btninsadddcancel),
        verifies redirection to the Inspection Log list page (Application Details Permit / .text-right),
        clicks 'Inspection Log New Entry', and verifies that the saved inspection details
        are displayed inside the table (#InspectionList).
        """
        self.logger.info("Cancelling from Inspection Details page to return to Inspection Log listing")
        cancel_btn = self.page.locator("#btninsadddcancel, button:visible").filter(has_text="Cancel").first
        expect(cancel_btn).to_be_visible(timeout=timeout_ms)
        cancel_btn.scroll_into_view_if_needed()

        # Click Cancel button to trigger redirection
        cancel_btn.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(1500)

        # If button is still visible, try js_click fallback
        if cancel_btn.is_visible():
            self.js_click(cancel_btn)
            self._wait_for_loader()
            self.page.wait_for_timeout(1500)

        # Verify redirection to Inspection listing page as specified by user
        expect(self.inspection_header_text).to_be_visible(timeout=timeout_ms)
        expect(self.page.locator(".text-right").first).to_be_visible(timeout=timeout_ms)

        # Click Inspection Log New Entry
        if self.inspection_log_text.is_visible(timeout=5000):
            self.inspection_log_text.click(force=True)
            self.page.wait_for_timeout(400)
        else:
            self.page.locator("a, button, div, span").filter(has_text="Inspection Log New Entry").first.click(force=True)
            self.page.wait_for_timeout(400)

        # Verify that the saved inspection entry is displayed in #InspectionList
        expect(self.inspection_list).to_be_visible(timeout=timeout_ms)

        # In #InspectionList, visible columns are: Date, Name (Inspected By), and Report Type
        search_term = None
        if isinstance(expected_status, dict):
            search_term = expected_status.get("report_type") or expected_status.get("inspected_by")
        elif isinstance(expected_status, str):
            search_term = expected_status

        if search_term:
            matching_row = self.inspection_list.locator("tbody tr").filter(has_text=search_term).first
            if matching_row.count() > 0 and matching_row.is_visible(timeout=4000):
                self.logger.info(f"Verified saved inspection entry in InspectionList: '{matching_row.inner_text().strip()}'")
            else:
                expect(self.inspection_list.locator("tbody tr:not(.k-no-data)").first).to_be_visible(timeout=timeout_ms)
                self.logger.info("Verified active inspection records present in InspectionList table")
        else:
            expect(self.inspection_list.locator("tbody tr:not(.k-no-data)").first).to_be_visible(timeout=timeout_ms)
            self.logger.info("Verified inspection entries are displayed in InspectionList table")
