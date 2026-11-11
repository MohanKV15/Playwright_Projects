import logging
import re
from typing import Optional
from faker import Faker
from playwright.sync_api import Locator, Page, expect
from pages.projects.project_base_page import ProjectBasePage

logger = logging.getLogger(__name__)
fake = Faker("en_US")


class ParcelInformationPage(ProjectBasePage):
    """
    Page Object Model representing the NCDOT Parcel Central - Parcel Information workflow:
      - Inherits Project search, login, and Tabstrip navigation from ProjectBasePage.
      - Navigates to Parcels tab and opens '+ Add New' parcel form.
      - Fills Parcel No *, Property Tax ID *, Deed Book/Page * with dynamic Faker data.
      - Selects Parcel Type (e.g. 'Agricultural'), County (e.g. 'Greene'), and Acquisition Status (e.g. 'Appraisal Received').
      - Saves the parcel record (#UpdateGeneralInfoBtn) and verifies persistence.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Parcel Details Form Fields
        self.parcel_no_input = page.locator(
            "input#tract_no:visible, input#Parcel_No:visible, input[name*='Parcel_No']:visible"
        ).or_(page.get_by_role("textbox", name="Parcel No *"))

        self.property_tax_id_input = page.locator(
            "input#rwr_parcelid:visible, input#Property_Tax_Id:visible, input[name*='Tax_Id']:visible"
        ).or_(page.get_by_role("textbox", name="Property Tax ID *"))

        self.deed_book_page_input = page.locator(
            "input#title_company:visible, input#Deed_Book_Page:visible, input[name*='Deed']:visible"
        ).or_(page.get_by_role("textbox", name="Deed Book/Page *"))

        # 2. Dropdowns in #ParcelDiv1 and #ParcelDiv2
        self.parcel_type_dropdown = page.locator(
            "#ParcelDiv2 span[aria-owns='prop_type_listbox'], #ParcelDiv2 .k-dropdown"
        ).first
        self.county_dropdown = page.locator(
            "#ParcelDiv1 span[aria-owns='county_Id_listbox'], #ParcelDiv1 .k-dropdown"
        ).first
        self.acquisition_status_dropdown = page.locator(
            "#ParcelDiv2 span[aria-owns='Status_listbox'], #ParcelDiv2 .k-dropdown"
        ).nth(1)

        # 3. Form Actions
        self.save_parcel_button = page.locator(
            "button#UpdateGeneralInfoBtn:visible, button:visible:has-text('Save')"
        ).first

    # =========================================================================
    # Parcel Central Actions
    # =========================================================================

    def open_add_new_parcel_form(self) -> "ParcelInformationPage":
        """Clicks '+ Add New' button on Parcels tab to open the parcel entry form."""
        self.logger.info("Parcels Tab: Clicking '+ Add New'")
        self.add_new_parcel_button.first.wait_for(state="visible", timeout=15000)
        self.add_new_parcel_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        expect(self.parcel_no_input.first).to_be_visible(timeout=15000)
        return self

    def fill_parcel_details(
        self,
        parcel_no: Optional[str] = None,
        property_tax_id: Optional[str] = None,
        deed_book_page: Optional[str] = None,
    ) -> "ParcelInformationPage":
        """Fills Parcel No *, Property Tax ID *, and Deed Book/Page * using Faker data if not provided."""
        p_no = parcel_no or str(fake.random_int(10000, 99999))
        tax_id = property_tax_id or str(fake.random_int(100000, 999999))
        book_page = deed_book_page or str(fake.random_int(1000, 9999))

        self.logger.info(f"Filling Parcel Details: No='{p_no}', TaxID='{tax_id}', Deed='{book_page}'")
        self.parcel_no_input.first.click()
        self.parcel_no_input.first.fill(p_no)

        self.property_tax_id_input.first.click()
        self.property_tax_id_input.first.fill(tax_id)

        self.deed_book_page_input.first.click()
        self.deed_book_page_input.first.fill(book_page)
        self.page.wait_for_timeout(300)
        return self

    def _select_kendo_dropdown_option(
        self,
        dropdown_locator: Locator,
        listbox_id: str,
        option_name: str,
        label: str = "Dropdown",
    ) -> None:
        """Reusable helper to select an option from a Kendo DropDownList with text matching or fallback."""
        self.logger.info(f"Selecting {label}: '{option_name}'")
        expect(dropdown_locator.first).to_be_visible(timeout=10000)
        dropdown_locator.first.click()
        self.page.wait_for_timeout(400)

        target_opt = self.page.locator(
            f"#{listbox_id} li[role='option'], .k-animation-container:visible li[role='option']"
        ).filter(has_text=re.compile(rf"^\s*{re.escape(option_name)}\s*$", re.I))

        if target_opt.count() > 0 and target_opt.first.is_visible(timeout=2000):
            target_opt.first.click()
        else:
            self.kendo_dropdown.select_first_option()

        self.page.wait_for_timeout(400)
        self._wait_for_loader()

    def select_parcel_type(self, option_name: str = "Agricultural") -> "ParcelInformationPage":
        """Selects Parcel Type in #ParcelDiv2."""
        self._select_kendo_dropdown_option(self.parcel_type_dropdown, "prop_type_listbox", option_name, "Parcel Type")
        return self

    def select_county(self, option_name: str = "Greene") -> "ParcelInformationPage":
        """Selects County in #ParcelDiv1."""
        self._select_kendo_dropdown_option(self.county_dropdown, "county_Id_listbox", option_name, "County")
        return self

    def select_acquisition_status(self, option_name: str = "Appraisal Received") -> "ParcelInformationPage":
        """Selects Acquisition Status in #ParcelDiv2."""
        self._select_kendo_dropdown_option(self.acquisition_status_dropdown, "Status_listbox", option_name, "Acquisition Status")
        return self

    def save_parcel(self) -> "ParcelInformationPage":
        """Clicks Save button and verifies persistence."""
        self.logger.info("Parcels Tab: Clicking 'Save' (#UpdateGeneralInfoBtn)")
        self.save_parcel_button.first.wait_for(state="visible", timeout=10000)
        self.save_parcel_button.first.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()
        self.logger.info("Parcel record successfully saved.")
        return self

    def create_new_parcel(
        self,
        parcel_no: Optional[str] = None,
        property_tax_id: Optional[str] = None,
        deed_book_page: Optional[str] = None,
        parcel_type: str = "Agricultural",
        county: str = "Greene",
        acquisition_status: str = "Appraisal Received",
        close_page_when_done: bool = False,
    ) -> "ParcelInformationPage":
        """
        Executes end-to-end Parcel creation workflow:
          1. Opens Add New Parcel form.
          2. Fills Parcel No, Property Tax ID, Deed Book/Page with dynamic Faker data.
          3. Selects Parcel Type.
          4. Selects County.
          5. Selects Acquisition Status.
          6. Saves parcel record.
        """
        self.open_add_new_parcel_form()
        self.fill_parcel_details(
            parcel_no=parcel_no,
            property_tax_id=property_tax_id,
            deed_book_page=deed_book_page,
        )
        self.select_parcel_type(option_name=parcel_type)
        self.select_county(option_name=county)
        self.select_acquisition_status(option_name=acquisition_status)
        self.save_parcel()

        if close_page_when_done:
            self.close_page()

        return self
