import re
from typing import List, Optional
from playwright.sync_api import Page, Locator, expect
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object Model representing the IDOT Outdoor Advertising Staff Portal Dashboard
    and Application/Permit Search page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Staff Portal Landing & Navigation
        self.staff_heading = page.locator("h3:has-text('Outdoor Advertising System')").or_(
            page.get_by_role("heading", name=re.compile(r"Outdoor\s+Advertising\s+System", re.I))
        ).or_(
            page.locator("text='**TEST** Outdoor Advertising System - Staff Portal **TEST**'")
        ).first
        self.adtrak_container = page.locator("div").filter(has_text="ADTrak")
        self.adtrak_button = self.adtrak_container.get_by_role("button")

        # 2. Search View Elements
        self.permits_heading = page.locator("h4:has-text('Permits')").or_(
            page.get_by_role("heading", name="Permits")
        ).or_(
            page.locator("text='Permits'")
        ).first
        self.permit_number_input = page.get_by_role("textbox", name="Application/Permit #").or_(
            page.locator("#ApplicationPermitNumber, [name='ApplicationPermitNumber'], #filterViewDiv input.form-control")
        ).first
        self.search_button = page.get_by_role("button", name=" Search").or_(
            page.locator("#filterViewDiv button:has-text('Search'), button:has-text('Search')")
        ).first

        # 3. Application Details Form Elements
        self.details_partial_form = page.locator("#partial-form")
        self.details_application_number = page.locator("#EP_Permit_Application_Tracking_No").or_(
            page.get_by_role("textbox", name="Application Number")
        ).or_(page.get_by_label("Application Number")).first
        self.section_sign_info = page.get_by_role("heading", name="Sign Information").or_(
            page.locator("h4:has-text('Sign Information')")
        ).first
        self.section_airport = page.get_by_role("heading", name="Airport Restrictions").or_(
            page.locator("h4:has-text('Airport Restrictions')")
        ).first
        self.section_location = page.get_by_role("heading", name="Location Information").or_(
            page.locator("h4:has-text('Location Information')")
        ).first
        self.section_property_owner = page.get_by_role("heading", name="Property Owner Information").or_(
            page.locator("h4:has-text('Property Owner Information')")
        ).first
        self.section_attachments = page.get_by_role("heading", name="Attachments").or_(
            page.locator("h4:has-text('Attachments')")
        ).first

        # 4. Logout Elements
        self.logout_link = page.locator("a[href*='Logout'], a:has-text('Logout')").first
        self.logout_confirm_button = page.locator("#Redirect-to-login, button:has-text('Log Out')").first

    # -------------------------------------------------------------------------
    # Landing & Navigation
    # -------------------------------------------------------------------------
    def verify_dashboard_loaded(self, timeout_ms: int = 30000) -> None:
        """Asserts that the staff portal dashboard is loaded and key branding is visible."""
        self.logger.info("Verifying staff portal dashboard is loaded")
        self._wait_for_loader()
        dashboard_indicator = self.staff_heading.or_(self.logout_link).or_(self.permits_heading).first
        expect(dashboard_indicator).to_be_visible(timeout=timeout_ms)

    def open_adtrak_module(self) -> None:
        """Opens ADTrak navigation module by clicking the menu button."""
        self.logger.info("Opening ADTrak navigation module")
        if self.adtrak_button.count() > 0:
            self.adtrak_button.first.click()
            self._wait_for_loader()
            if not self.permits_heading.is_visible(timeout=2000):
                self.adtrak_button.first.click()
                self._wait_for_loader()

    def navigate_to_search(self) -> None:
        """Navigates into Application/Permit Search view."""
        self._wait_for_loader()
        self.verify_dashboard_loaded(timeout_ms=30000)

        if not self.permits_heading.is_visible(timeout=2000):
            self.logger.info("Opening ADTrak module to reveal Application/Permit Search...")
            self.open_adtrak_module()

            if not self.permits_heading.is_visible(timeout=2000):
                sidebar_link = self.page.get_by_role("link", name="Application/Permit Search")
                if sidebar_link.is_visible(timeout=2000):
                    sidebar_link.click()
                    self._wait_for_loader()

        expect(self.permits_heading).to_be_visible(timeout=25000)

    def verify_search_page_elements(self) -> None:
        """Asserts key branding and search page components are visible."""
        self.logger.info("Verifying Application/Permit Search page elements")
        expect(self.permits_heading).to_be_visible(timeout=20000)
        expect(self.search_button).to_be_visible(timeout=10000)

    # -------------------------------------------------------------------------
    # Dialogs & Error Handling
    # -------------------------------------------------------------------------
    def dismiss_error_modal_if_present(self) -> bool:
        """Dismisses 'Error occured. Contact Administrator' alert modal if displayed."""
        try:
            ok_btn = self.page.locator(
                ".k-dialog:visible button:has-text('OK'), .k-alert:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), .modal:visible button:has-text('OK')"
            ).or_(
                self.page.get_by_role("button", name="OK")
            ).first
            if ok_btn.is_visible(timeout=800):
                self.logger.warning("Detected error alert modal; clicking OK to dismiss.")
                ok_btn.click(force=True)
                self.page.wait_for_timeout(400)
                self._wait_for_loader()
                return True
        except Exception:
            pass
        return False

    # -------------------------------------------------------------------------
    # Search & Dynamic Status Iteration
    # -------------------------------------------------------------------------
    def click_search(self) -> None:
        """Clicks the Search button, handles any alert popups, and waits for grid update."""
        self.logger.info("Clicking Search button")
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        self.search_button.click(force=True)
        self.page.wait_for_timeout(800)
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        self.page.wait_for_timeout(1000)

    def get_data_rows(self) -> List[Locator]:
        """Returns list of valid permit data rows (excluding header and no-data rows)."""
        self._wait_for_loader()
        rows = self.page.locator("#PermitListGrid tbody tr:not(.k-no-data)").all()
        return [r for r in rows if r.locator("td").count() >= 3 and "no items" not in r.inner_text().lower()]

    def get_data_rows_count(self) -> int:
        """Returns the number of valid permit data rows currently displayed in the grid."""
        return len(self.get_data_rows())

    def open_status_dropdown(self) -> bool:
        """Opens the Application Status dropdown listbox."""
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        trigger = self.page.locator("#filterViewDiv span.k-input, #filterViewDiv .k-dropdown").first
        if trigger.is_visible(timeout=2000):
            trigger.click(force=True)
            self.page.wait_for_timeout(400)
            return True
        return False

    def select_application_status(self, status_name: str) -> bool:
        """Selects an Application Status option from the dropdown."""
        self.logger.info(f"Selecting Application Status: '{status_name}'")
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        try:
            if not self.open_status_dropdown():
                return False

            option = self.page.get_by_role("option", name=status_name).or_(
                self.page.locator(".k-animation-container:visible li, #ApplicationStatus_listbox li").filter(has_text=status_name)
            ).first

            if option.is_visible(timeout=3000):
                option.click(force=True)
                self._wait_for_loader()
                self.page.wait_for_timeout(500)
                return True
            else:
                self.page.keyboard.press("Escape")
        except Exception as e:
            self.logger.warning(f"Could not select status '{status_name}': {e}")
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass
        return False

    def search_until_records_found(self, candidate_statuses: Optional[List[str]] = None) -> bool:
        """
        Dynamically iterates through Application Statuses until records appear in Permits table.
        Avoids searching with '-- Select --' to prevent server-side exceptions.
        """
        self.dismiss_error_modal_if_present()

        if self.get_data_rows_count() > 0:
            self.logger.info(f"Records already present: {self.get_data_rows_count()}")
            return True

        if not candidate_statuses:
            candidate_statuses = [
                "Amended Permit",
                "Original Permit",
                "Permit",
                "Application",
                "Approved",
                "Pending",
                "Active",
            ]

        self.logger.info("Iterating through application statuses to locate permits data...")
        for index, status in enumerate(candidate_statuses, start=1):
            self.dismiss_error_modal_if_present()
            self.logger.info(f"Trying Status #{index}: '{status}'...")
            if self.select_application_status(status):
                self.click_search()
                self.dismiss_error_modal_if_present()
                count = self.get_data_rows_count()
                if count > 0:
                    self.logger.info(f"Status '{status}' returned {count} records in Permits table.")
                    return True

        self.logger.warning("No records found across all candidate application statuses.")
        return False

    # -------------------------------------------------------------------------
    # Record Extraction & Application Details Verification
    # -------------------------------------------------------------------------
    def is_application_details_visible(self) -> bool:
        """Returns True if currently viewing the Application Details / Update form."""
        try:
            if "PermitPaperApp" in self.page.url or "AppInfo" in self.page.url:
                return True
            return self.details_partial_form.is_visible(timeout=2000)
        except Exception:
            return False

    def get_first_record_permit_number(self) -> str:
        """Retrieves the Permit # from the first cell of the first row in the grid."""
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        first_row = self.page.locator("#PermitListGrid tbody tr:not(.k-no-data)").first
        expect(first_row).to_be_visible(timeout=15000)
        permit_cell = first_row.locator("td").first
        permit_number = re.sub(r"\s+", "", permit_cell.inner_text().strip())
        self.logger.info(f"Retrieved 1st record Permit Number: '{permit_number}'")
        return permit_number

    def search_by_permit_number(self, permit_number: str) -> None:
        """
        Fills the target Permit Number into search field and clicks Search.
        Note: The portal automatically redirects to Application Details view when exactly 1 match is found.
        """
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        cleaned = re.sub(r"\s+", "", permit_number)
        self.logger.info(f"Filtering specifically by Permit #: '{cleaned}'")
        self.permit_number_input.click(force=True)
        self.permit_number_input.clear()
        self.permit_number_input.fill(cleaned)
        self.click_search()
        self.dismiss_error_modal_if_present()
        self.page.wait_for_timeout(2000)
        self._wait_for_loader()

        if self.is_application_details_visible():
            self.logger.info("Single-record search automatically opened Application Details view.")
            return

        if self.permits_heading.is_visible(timeout=2000) and self.get_data_rows_count() == 0:
            self.logger.info("No records found; clearing search field to restore permits table.")
            self.permit_number_input.click(force=True)
            self.permit_number_input.clear()
            self.click_search()
            self._wait_for_loader()

    def click_first_record_action_button(self) -> None:
        """
        Clicks the Action/Edit button on the matching first record.
        If the portal already auto-redirected to the Application Details form, this step succeeds immediately.
        """
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()

        if self.is_application_details_visible():
            self.logger.info("Application details already open (auto-redirected from search).")
            return

        self.logger.info("Clicking Action/Edit button on first record in Permits grid...")
        first_row = self.page.locator("#PermitListGrid tbody tr:not(.k-no-data)").first
        expect(first_row).to_be_visible(timeout=20000)

        action_button = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_button).to_be_visible(timeout=15000)
        action_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(2000)

    def verify_application_details_sections(self) -> None:
        """
        Verifies that the Application Details form (#partial-form) and all core sections:
        - Application Number textbox
        - Sign Information
        - Airport Restrictions
        - Location Information
        - Property Owner Information
        - Attachments
        are visible.
        """
        self.logger.info("Observing and verifying Application Details sections...")
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()

        sections = [
            self.details_partial_form,
            self.details_application_number,
            self.section_sign_info,
            self.section_airport,
            self.section_location,
            self.section_property_owner,
            self.section_attachments,
        ]
        for section in sections:
            expect(section).to_be_visible(timeout=20000)

        self.logger.info("All Application Details sections verified successfully!")

    # -------------------------------------------------------------------------
    # Logout Handling
    # -------------------------------------------------------------------------
    def logout(self) -> None:
        """Clicks Logout link and confirms modal dialog."""
        self.logger.info("Clicking Logout link")
        self.dismiss_error_modal_if_present()
        self._wait_for_loader()
        self.logout_link.click(force=True)
        self.page.wait_for_timeout(500)

        try:
            if self.logout_confirm_button.is_visible(timeout=3000):
                self.logger.info("Confirming logout modal...")
                self.logout_confirm_button.click(force=True)
        except Exception:
            pass

        self._wait_for_loader()
