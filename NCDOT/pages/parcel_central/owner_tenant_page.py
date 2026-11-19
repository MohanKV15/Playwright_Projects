import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker("en_US")


class OwnerTenantPage(ProjectBasePage):
    """
    Page Object Model representing NCDOT Parcel Central - Owner/Tenant workflow:
      - Inherits Project search, login, Tabstrip navigation, and Parcel Central entry from ProjectBasePage.
      - Navigates to 'Owner/Tenant' sub-menu in left sidebar.
      - Opens '+ Add New' Owner/Tenant entry form.
      - Selects Type (non-first option, e.g. 'Mortgagee' or 2nd available option via KendoDropdown component).
      - Selects Gender ('Male' or 1st available option via KendoDropdown component).
      - Fills 'Name for Signature Line *' with dynamic Faker data.
      - Saves the owner/tenant record.
      - Navigates Back and verifies listing container visibility.
    """

    DEFAULT_TYPE = "Mortgagee"
    DEFAULT_GENDER = "Male"

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Content Containers
        self.owner_tenant_nav_link = page.locator(
            "#navigationMenu2, #navigationMenu, nav, ul, .k-panelbar, body"
        ).get_by_text("Owner/Tenant", exact=True)

        self.listing_container = page.locator("#partialForm #partial-form, #partial-form")
        self.owner_detail_form = page.locator("#ownerDetail #partial-form, #ownerDetail")

        # 2. Action Buttons
        self.add_new_button = page.get_by_role("button", name=re.compile(r"Add New", re.I)).or_(
            page.locator("button, a").filter(has_text=re.compile(r"Add New", re.I))
        )

        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("button, a").filter(has_text=re.compile(r"Save", re.I))
        )

        self.back_button = page.locator("#OwnerBackBtn:visible, button#OwnerBackBtn, button#btnBack:visible").or_(
            page.get_by_role("button", name=re.compile(r"Back", re.I))
        ).or_(
            page.locator("button:visible, a:visible").filter(has_text=re.compile(r"Back", re.I))
        )

        # 3. Form Input & Dropdown Elements
        self.owner_type_dropdown = page.locator(
            "#divOwnerDetails .k-dropdown, #divOwnerDetails span[aria-owns*='listbox']"
        ).first

        self.gender_dropdown = page.locator(
            "#DivGender .k-dropdown, #DivGender span[aria-owns*='listbox']"
        ).first

        self.signature_name_input = page.get_by_role("textbox", name=re.compile(r"Name for Signature Line", re.I)).or_(
            page.locator("input#SignLineName, input[name*='SignLineName'], input[name*='Signature']")
        )

        self.error_alerts = page.locator(".alert-danger:visible, .field-validation-error:visible, .k-alert-error:visible")

    # =========================================================================
    # Owner/Tenant Navigation Actions
    # =========================================================================

    def navigate_to_owner_tenant(self) -> "OwnerTenantPage":
        """Clicks 'Owner/Tenant' in Parcel Central left navigation and verifies view container."""
        self.logger.info("Navigating to Owner/Tenant sub-menu")
        self._wait_for_loader()
        self.owner_tenant_nav_link.first.wait_for(state="visible", timeout=15000)
        self.owner_tenant_nav_link.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.listing_container.first).to_be_visible(timeout=15000)
        return self

    def open_add_new_owner_tenant_form(self) -> "OwnerTenantPage":
        """Clicks '+ Add New' button and verifies Owner Detail form visibility."""
        self.logger.info("Opening Add New Owner/Tenant form")
        self.add_new_button.first.wait_for(state="visible", timeout=10000)
        self.add_new_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.owner_detail_form.first).to_be_visible(timeout=15000)
        return self

    # =========================================================================
    # Form Field Operations
    # =========================================================================

    def select_type(self, type_name: Optional[str] = DEFAULT_TYPE) -> "OwnerTenantPage":
        """
        Selects Owner/Tenant Type dropdown.
        As requested, avoids the 1st option ('Landowner Attorney') and selects another option
        (defaults to 'Mortgagee' or 2nd available option).
        """
        target_type = type_name or self.DEFAULT_TYPE
        self.logger.info(f"Selecting Owner/Tenant Type: '{target_type}' (non-first option)")
        success = self.kendo_dropdown.select_option(self.owner_type_dropdown, target_type)
        if not success:
            self.kendo_dropdown.select_second_option(self.owner_type_dropdown)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        return self

    def select_gender(self, gender: Optional[str] = DEFAULT_GENDER) -> "OwnerTenantPage":
        """Selects Gender dropdown (e.g. 'Male' or 1st valid option)."""
        target_gender = gender or self.DEFAULT_GENDER
        self.logger.info(f"Selecting Gender: '{target_gender}'")
        self.kendo_dropdown.select_option(self.gender_dropdown, target_gender)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()
        return self

    def fill_signature_name(self, name: Optional[str] = None) -> "OwnerTenantPage":
        """Fills 'Name for Signature Line *' using Faker data if not provided."""
        signature_name = name or fake.name()
        self.logger.info(f"Filling Signature Name: '{signature_name}'")
        self.signature_name_input.first.wait_for(state="visible", timeout=10000)
        self.signature_name_input.first.scroll_into_view_if_needed()
        self.signature_name_input.first.click()
        self.signature_name_input.first.fill(signature_name)
        self.page.wait_for_timeout(300)
        return self

    def click_save(self) -> "OwnerTenantPage":
        """Clicks 'Save' button and handles any confirmation/alert dialogs."""
        self.logger.info("Owner/Tenant Form: Clicking 'Save'")
        self.save_button.first.wait_for(state="visible", timeout=10000)
        self.save_button.first.scroll_into_view_if_needed()
        self.save_button.first.click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

        # Handle any alert or popup if present
        self.kendo_dialog.handle_alert(pattern=r"already|alert|success", button_text="OK")
        self._wait_for_loader()
        self.verify_no_errors()
        self.logger.info("Owner/Tenant record successfully saved without errors.")
        return self

    def click_back(self) -> "OwnerTenantPage":
        """Clicks 'Back' button and verifies return to listing view."""
        self.logger.info("Owner/Tenant Form: Clicking 'Back'")
        self.back_button.first.wait_for(state="visible", timeout=15000)
        self.back_button.first.click(force=True)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.listing_container.first).to_be_visible(timeout=15000)
        self.logger.info("Returned to Owner/Tenant listing view successfully.")
        return self

    def verify_no_errors(self) -> "OwnerTenantPage":
        """Verifies that no error alerts or validation error messages are displayed."""
        expect(self.error_alerts).to_have_count(0, timeout=5000)
        return self

    def add_new_owner_tenant(
        self,
        type_name: Optional[str] = DEFAULT_TYPE,
        gender: Optional[str] = DEFAULT_GENDER,
        signature_name: Optional[str] = None,
    ) -> "OwnerTenantPage":
        """
        Executes end-to-end add owner/tenant flow:
          1. Opens Add New form.
          2. Selects Type (non-first option, e.g. 'Mortgagee').
          3. Selects Gender ('Male').
          4. Fills Signature Name with dynamic Faker data.
          5. Saves record.
          6. Clicks Back.
          7. Verifies return to listing view.
        """
        return (
            self.open_add_new_owner_tenant_form()
            .select_type(type_name=type_name)
            .select_gender(gender=gender)
            .fill_signature_name(name=signature_name)
            .click_save()
            .click_back()
        )
