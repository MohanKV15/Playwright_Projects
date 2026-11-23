import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker()


class AppraisalRequestPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Appraisal Request:
      - Inherits Project search, authentication, and Parcel Central navigation from ProjectBasePage.
      - Navigates to 'Appraisal Request' via #navigationMenu2 sidebar menu.
      - Land Tab: Edits Engineering Parcel options (radio toggles) and saves.
      - Improvements Tab: Adds a new Improvement form (Name, Owner dropdown) and saves.
      - Documents Tab: Navigates to Documents subtab and verifies container visibility.
      - Log Tab: Navigates to Log subtab and verifies log table display without error.
      - Verifies clean state without errors across all subtabs.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Content Containers
        self.appraisal_nav_link = (
            page.locator("#navigationMenu2").get_by_text("Appraisal Request", exact=True)
            .or_(page.locator("#navigationMenu2, #navigationMenu").get_by_text("Appraisal Request"))
            .or_(page.get_by_text("Appraisal Request", exact=True))
        )
        self.appraisal_content_container = (
            page.locator("#partial-form").nth(1)
            .or_(page.locator("#partialForm #partial-form, #partial-form"))
        )

        # 2. Parcel Central Sub-Tabs Strip
        self.parcel_central_tabs = page.locator("#ParcelCentralTab")

        # 3. Land Tab Locators
        self.edit_eng_parcel_button = page.locator("#EditEngParcel")
        self.radio_option_1 = page.locator(".col-md-1 > .form-check > .k-radio-label").first
        self.radio_option_2 = page.locator("div:nth-child(2) > .row > .col-md-1.p-0 > .form-check > .k-radio-label").first
        self.save_eng_parcel_button = (
            page.locator("#UpdateEngParcel:visible")
            .or_(page.locator("button:visible:has-text('Save')"))
            .or_(page.get_by_role("button", name=re.compile(r"^\s*Save\s*$", re.I)))
        )

        # 4. Improvements Tab Locators
        self.improvements_add_button = page.locator(
            "button#btnImproReqaddnewform:visible, button:visible:has-text('Add New')"
        )
        self.improvement_name_input = page.locator(
            ".k-window:visible input#ImprovementName, input#ImprovementName:visible"
        )
        self.improvement_owner_dropdown = page.locator(
            ".k-window:visible span.k-dropdown-wrap, span.k-widget.k-dropdown:has(#OwnerofImprovement)"
        )
        self.save_improvement_button = page.locator(
            ".k-window:visible button#impSave, button#impSave:visible, .k-window:visible button:has-text('Save')"
        )

        # 5. Documents Tab Locators
        self.documents_container = page.locator(
            "#ParcelCentralTab-9, div[id*='ParcelCentralTab']:visible, #partial-form:visible"
        )

        # 6. Log Tab Locators
        self.log_container = page.locator(
            "#divLogTable:visible, #divLgTable:visible, button#btnAddCallData:visible, .k-grid:visible"
        )

        # 7. Error / Validation Alerts
        self.error_alerts = page.locator(
            ".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible"
        )

    # =========================================================================
    # Navigation & Subtab Switching
    # =========================================================================

    def navigate_to_appraisal_request(self) -> "AppraisalRequestPage":
        """Clicks 'Appraisal Request' in #navigationMenu2 sidebar and verifies container."""
        self.logger.info("Navigating to Appraisal Request sub-menu via #navigationMenu2")
        self._wait_for_loader()
        self.appraisal_nav_link.first.wait_for(state="visible", timeout=15000)
        self.appraisal_nav_link.first.click()
        self._wait_for_loader()
        expect(self.appraisal_content_container.first).to_be_visible(timeout=15000)
        return self

    def switch_subtab(self, tab_name: str) -> "AppraisalRequestPage":
        """Delegates subtab switching to the KendoTabStrip component and synchronizes loaders."""
        self.logger.info(f"Switching to subtab '{tab_name}' via KendoTabStrip component")
        self._wait_for_loader()
        self.kendo_tabstrip.select_tab(self.parcel_central_tabs, tab_name)
        self.page.wait_for_timeout(300)
        self._wait_for_loader()
        return self

    # =========================================================================
    # Section 1: Land Tab Operations
    # =========================================================================

    def edit_engineering_parcel_options(self) -> "AppraisalRequestPage":
        """Clicks '#EditEngParcel', selects radio options, and clicks Save button."""
        self.logger.info("Land Tab: Editing Engineering Parcel options")
        self._wait_for_loader()

        self.edit_eng_parcel_button.first.wait_for(state="visible", timeout=15000)
        self.edit_eng_parcel_button.first.scroll_into_view_if_needed()
        self.edit_eng_parcel_button.first.click()
        self.page.wait_for_timeout(300)

        if self.radio_option_1.is_visible(timeout=3000):
            self.radio_option_1.click(force=True)

        if self.radio_option_2.is_visible(timeout=3000):
            self.radio_option_2.click(force=True)

        save_btn = self.save_eng_parcel_button.first
        save_btn.wait_for(state="visible", timeout=10000)
        save_btn.click(force=True)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        self.logger.info("Land Tab: Engineering Parcel options saved successfully.")
        return self

    # =========================================================================
    # Section 2: Improvements Tab Operations
    # =========================================================================

    def navigate_to_improvements_and_add_record(
        self,
        improvement_name: Optional[str] = None,
        owner_name: Optional[str] = None,
    ) -> "AppraisalRequestPage":
        """
        Navigates to Improvements subtab, clicks 'Add New', fills the improvement
        name, selects the 1st available owner from the dropdown using KendoDropdown,
        and clicks Save.
        """
        imp_name = improvement_name or f"Imp {fake.word().capitalize()} {fake.random_int(100, 999)}"
        self.logger.info(f"Improvements Tab: Adding record '{imp_name}'")

        self.switch_subtab("Improvements")

        add_btn = self.improvements_add_button.first
        add_btn.wait_for(state="visible", timeout=10000)
        add_btn.click()
        self.page.wait_for_timeout(300)
        self._wait_for_loader()

        # Fill Improvement Name
        name_input = self.improvement_name_input.first
        name_input.wait_for(state="visible", timeout=10000)
        name_input.fill(imp_name)

        # Select Owner using separated KendoDropdown component (defaults to 1st option)
        if owner_name:
            self.kendo_dropdown.select_option(self.improvement_owner_dropdown, owner_name)
        else:
            self.kendo_dropdown.select_first_option(self.improvement_owner_dropdown)

        # Click Save (#impSave)
        save_btn = self.save_improvement_button.first
        save_btn.wait_for(state="visible", timeout=10000)
        save_btn.click(force=True)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success|saved", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        self.logger.info(f"Improvements Tab: Record '{imp_name}' saved successfully.")
        return self

    # =========================================================================
    # Section 3: Documents Tab Operations
    # =========================================================================

    def navigate_to_documents_tab(self) -> "AppraisalRequestPage":
        """Clicks 'Documents' tab and verifies view container visibility."""
        self.logger.info("Documents Tab: Navigating and verifying container")
        self.switch_subtab("Documents")
        expect(self.documents_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Documents Tab: Verified successfully.")
        return self

    # =========================================================================
    # Section 4: Log Tab Operations
    # =========================================================================

    def navigate_to_log_tab(self) -> "AppraisalRequestPage":
        """
        Navigates to Log tab, verifies log table is displayed, and checks for zero errors.
        """
        self.logger.info("Log Tab: Navigating to Log tab and verifying table display")
        self.switch_subtab("Log")
        expect(self.log_container.first).to_be_visible(timeout=15000)
        self.verify_no_errors()
        self.logger.info("Log Tab: Verified table displayed cleanly without errors.")
        return self

    # =========================================================================
    # Error Verification
    # =========================================================================

    def verify_no_errors(self) -> "AppraisalRequestPage":
        """Verifies that no error alerts or validation errors are displayed."""
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self
