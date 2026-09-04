import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.utils.config import Config

logger = logging.getLogger(__name__)


class PrimaryHighwayPage(BasePage):
    """
    Page Object Model representing the Add Paper Application - Primary Highway
    workflow in the IDOT Outdoor Advertising Staff Portal.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Locators
        self.add_paper_button = page.get_by_role("button", name="Add Paper Application")
        self.application_list_heading = page.get_by_role("heading", name="Application List")
        self.primary_highway_button = page.locator("#btnPrimary")

        # Company Search Locators
        self.select_company_button = page.get_by_role("button", name="Select Company")
        self.company_search_dialog = page.locator(".k-window:visible").filter(has_text="Company Search")
        self.company_name_input = page.locator("#Dealer_Name")

        # Property Owner Form Locators
        self.owner_name_input = page.get_by_label("Property Owner Name")
        self.owner_address1_input = page.get_by_label("Property Owner Address 1")
        self.owner_address2_input = page.get_by_label("Property Owner Address 2")
        self.city_input = page.get_by_label("City")

        # Submission & Verification Locators
        self.save_button = page.locator("#btnSubmit, button:has-text('Save')").first
        self.partial_form = page.locator("#partial-form")
        self.tracking_number_input = page.locator(
            "#EP_Permit_Application_Tracking_No, input[name*='Tracking_No'], input[name*='Application_No']"
        ).first

    # -------------------------------------------------------------------------
    # Navigation Actions
    # -------------------------------------------------------------------------
    def navigate_to_add_paper_application(self) -> None:
        """Clicks 'Add Paper Application' button and asserts Application List displays."""
        self.logger.info("Clicking 'Add Paper Application' button")
        self._wait_for_loader()
        expect(self.add_paper_button).to_be_visible(timeout=20000)
        self.add_paper_button.click(force=True)
        self._wait_for_loader()
        expect(self.application_list_heading).to_be_visible(timeout=20000)

    def select_primary_highway_type(self) -> None:
        """Clicks '#btnPrimary' to launch Primary Highway application form."""
        self.logger.info("Selecting Primary Highway application type (#btnPrimary)")
        self._wait_for_loader()
        expect(self.primary_highway_button).to_be_visible(timeout=20000)
        self.primary_highway_button.click(force=True)
        self._wait_for_loader()
        expect(self.select_company_button).to_be_visible(timeout=25000)

    # -------------------------------------------------------------------------
    # Company Search & Selection
    # -------------------------------------------------------------------------
    def search_and_select_company(self, company_name: str = "test", preferred_company: str = "IDOTOAtest2") -> str:
        """
        Opens Company Search popup, enters company_name, searches,
        selects preferred_company if present (otherwise first row), and confirms with OK.
        """
        self.logger.info(f"Opening Company Search dialog and filtering for '{company_name}'")
        self._wait_for_loader()
        expect(self.select_company_button).to_be_visible(timeout=15000)
        self.select_company_button.click(force=True)
        self._wait_for_loader()

        modal = self.company_search_dialog.first
        expect(modal).to_be_visible(timeout=20000)
        self.company_name_input.fill(company_name)

        search_btn = modal.locator("button:has-text('Search'), input[value='Search']").first
        expect(search_btn).to_be_visible(timeout=10000)
        search_btn.click(force=True)
        self._wait_for_loader()

        # Wait for search results table to load with checkboxes
        checkboxes = modal.locator("input[type='checkbox'], #selectedChk")
        expect(checkboxes.first).to_be_visible(timeout=15000)

        # Check preferred company row if present, otherwise select first available checkbox
        preferred_row = modal.locator("tr").filter(has_text=preferred_company).first
        if preferred_row.is_visible(timeout=2000):
            self.logger.info(f"Found preferred company '{preferred_company}'. Selecting checkbox...")
            preferred_row.locator("input[type='checkbox'], #selectedChk").first.check(force=True)
            selected_name = preferred_company
        else:
            self.logger.info(f"'{preferred_company}' not found. Selecting first available row...")
            checkboxes.first.check(force=True)
            selected_name = modal.locator("tr:has(input[type='checkbox'])").first.inner_text().split("\t")[0].strip()

        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')"
        ).first
        if ok_btn.is_visible(timeout=5000):
            ok_btn.click(force=True)
        self._wait_for_loader()

        self.logger.info(f"Selected company: '{selected_name}'")
        return selected_name

    # -------------------------------------------------------------------------
    # Dropdown & Form Filling Helpers
    # -------------------------------------------------------------------------
    def _select_kendo_dropdown(self, field_id: str, option_text: Optional[str] = None, index: int = 1) -> None:
        """Selects an option from a Kendo DropDownList by element ID."""
        try:
            self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{field_id}').data('kendoDropDownList');
                    if (!ddl) return;
                    const target = '{option_text or ""}';
                    if (target) {{
                        const data = ddl.dataSource.data();
                        for (let i = 0; i < data.length; i++) {{
                            const text = (ddl.text(data[i]) || '').toLowerCase();
                            if (text.includes(target.toLowerCase())) {{
                                ddl.select(i + (ddl.options.optionLabel ? 1 : 0));
                                ddl.trigger('change');
                                return;
                            }}
                        }}
                    }}
                    if (ddl.dataSource.data().length > 0) {{
                        ddl.select({index});
                        ddl.trigger('change');
                    }}
                }})();
                """
            )
            self._wait_for_loader()
        except Exception as e:
            self.logger.warning(f"Dropdown selection for #{field_id}: {e}")

    def fill_sign_information(
        self,
        structure_type: str = "Fence Mounted",
        face_width: str = "10",
        face_height: str = "10",
        received_datetime: Optional[datetime] = None,
    ) -> None:
        """Fills Sign Information, dates, structure dropdowns, and triggers dimension calculations."""
        now = received_datetime or datetime.now()
        date_str = now.strftime("%m/%d/%Y")
        datetime_str = now.strftime("%m/%d/%Y %I:%M:%S %p")

        self.logger.info("Filling Sign Information...")
        self._wait_for_loader()

        # Dates & Numeric heights via Kendo controls
        self.page.evaluate(
            f"""
            (() => {{
                $('#ApplicationReceivedDateTime').val('{datetime_str}').trigger('change');
                const dp = $('#erectiondate_temp').data('kendoDatePicker');
                if (dp) dp.value('{date_str}');
                $('#erectiondate_temp').val('{date_str}').trigger('change');

                const bMolding = $('#HeightBottomMolding').data('kendoNumericTextBox');
                if (bMolding) bMolding.value(1.0);
                const topSign = $('#HeightToTop').data('kendoNumericTextBox');
                if (topSign) topSign.value(10.0);
            }})();
            """
        )

        # Dropdowns
        self._select_kendo_dropdown("StructureType", structure_type, index=1)
        self._select_kendo_dropdown("ConfigNumber", "1", index=1)
        self._select_kendo_dropdown("VerticalSupports", None, index=1)
        self._select_kendo_dropdown("NumOfSupports", "1", index=2)
        self._select_kendo_dropdown("SignLighting", None, index=1)

        # Face Width, Height, and execute square feet calculation functions
        self.logger.info(f"Setting Face Width={face_width}, Face Height={face_height}")
        self.page.evaluate(
            f"""
            (() => {{
                const w = {float(face_width)}, h = {float(face_height)};
                const wBox = $('#ODA_Outdoor_Face_Detail_Face_Width1').data('kendoNumericTextBox');
                if (wBox) wBox.value(w);
                $('#ODA_Outdoor_Face_Detail_Face_Width1').val(w).trigger('change');

                const hBox = $('#ODA_Outdoor_Face_Detail_Face_Height1').data('kendoNumericTextBox');
                if (hBox) hBox.value(h);
                $('#ODA_Outdoor_Face_Detail_Face_Height1').val(h).trigger('change');

                if (typeof CalculateSquareFeetSign1Face1 === 'function') CalculateSquareFeetSign1Face1();
                if (typeof CalculateSign1Total === 'function') CalculateSign1Total();
                if (typeof CalculateTotal === 'function') CalculateTotal();
            }})();
            """
        )
        self._wait_for_loader()

    def fill_location_information(
        self,
        district: str = "District 1",
        county: str = "Cook",
        route: str = "100th St",
    ) -> None:
        """Fills Location Information: airport restrictions, radios, and cascading dropdowns."""
        self.logger.info(f"Filling Location: District={district}, County={county}, Route={route}")
        self._wait_for_loader()

        # Location & Airport Restrictions Radios
        self.page.evaluate(
            """
            (() => {
                $('#TwoMileNo_No, #LocInLimitNo_No, #LocInUnzonedNo_No, #IsVisibleNo_No, #hund_two_100')
                    .prop('checked', true).trigger('change');
            })();
            """
        )

        # Cascading Dropdowns: District -> County -> Route
        self._select_kendo_dropdown("EP_Permit_Application_District", district, index=1)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        self._select_kendo_dropdown("EP_Permit_Application_County", county, index=1)
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

        self._select_kendo_dropdown("EP_Permit_Application_Route", route, index=1)
        self._wait_for_loader()

    def fill_property_owner_information(
        self,
        owner_name: str,
        address1: str,
        address2: str,
        city: str,
    ) -> None:
        """Fills Property Owner Information fields."""
        self.logger.info(f"Filling Property Owner: Name='{owner_name}', City='{city}'")
        self._wait_for_loader()

        expect(self.owner_name_input).to_be_visible(timeout=10000)
        self.owner_name_input.fill(owner_name)

        expect(self.owner_address1_input).to_be_visible(timeout=10000)
        self.owner_address1_input.fill(address1)

        if self.owner_address2_input.is_visible(timeout=2000):
            self.owner_address2_input.fill(address2)

        expect(self.city_input).to_be_visible(timeout=10000)
        self.city_input.fill(city)

    def upload_attachments(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """Uploads dummy PDF file to the starting application attachment input only."""
        dummy_pdf = Path(file_path) if file_path else (Config.PROJECT_ROOT / "testdata" / "dummy.pdf")
        if not dummy_pdf.exists():
            self.logger.warning(f"Attachment file not found at: {dummy_pdf}")
            return

        self.logger.info(f"Uploading attachment to starting input: {dummy_pdf}")
        first_input = self.page.locator("input[type='file']").first
        expect(first_input).to_be_attached(timeout=10000)
        first_input.set_input_files(str(dummy_pdf))
        self.page.wait_for_timeout(500)
        self._wait_for_loader()

    # -------------------------------------------------------------------------
    # Save & Verification
    # -------------------------------------------------------------------------
    def save_and_get_application_number(self) -> str:
        """
        Clicks Save, captures the created Application Number from the confirmation popup,
        clicks OK on popup, and returns the application number.
        """
        self.logger.info("Clicking Save button (#btnSubmit)...")
        self._wait_for_loader()
        expect(self.save_button).to_be_visible(timeout=15000)
        self.save_button.scroll_into_view_if_needed()
        self.save_button.click(force=True)

        # Wait for confirmation dialog popup
        alert_dialog = self.page.locator(
            ".k-confirm:visible, .k-dialog:visible, .modal:visible"
        ).filter(has_text=re.compile(r"Please record the", re.I)).first

        expect(alert_dialog).to_be_visible(timeout=30000)
        alert_text = alert_dialog.inner_text()
        self.logger.info(f"Save confirmation alert text: '{alert_text}'")

        # Extract application number
        match = re.search(r"Application\s*#:\s*([A-Za-z0-9-]+)|([A-Za-z0-9]+-\d+)|(\d{4,})", alert_text, re.I)
        application_number = next((g.strip() for g in match.groups() if g), "") if match else ""
        self.logger.info(f"Captured Application Number: '{application_number}'")

        # Confirm alert popup
        ok_btn = alert_dialog.locator("button:has-text('OK'), .k-button:has-text('OK'), button.k-primary").first
        expect(ok_btn).to_be_visible(timeout=10000)
        ok_btn.click(force=True)

        # Wait for redirection to cloned/details form
        try:
            self.page.wait_for_url(re.compile(r"4319PermitPaperAppNew_Cloned|Application_Id="), timeout=25000)
        except Exception:
            pass
        self._wait_for_loader()

        return application_number

    def verify_application_saved(
        self,
        expected_app_number: Optional[str] = None,
        expected_owner_name: Optional[str] = None,
        expected_city: Optional[str] = None,
    ) -> None:
        """Verifies that '#partial-form' is visible and displays saved application details."""
        self.logger.info("Verifying saved application details on '#partial-form'...")
        self._wait_for_loader()
        expect(self.partial_form).to_be_visible(timeout=30000)

        if expected_app_number:
            self.logger.info(f"Verifying created application number: '{expected_app_number}'")
            if self.tracking_number_input.is_visible(timeout=3000):
                expect(self.tracking_number_input).to_have_value(re.compile(rf"{re.escape(expected_app_number)}"))
            else:
                expect(self.partial_form).to_contain_text(expected_app_number)

        if expected_owner_name:
            self.logger.info(f"Verifying Property Owner Name: '{expected_owner_name}'")
            if self.owner_name_input.is_visible(timeout=3000):
                expect(self.owner_name_input).to_have_value(expected_owner_name)
            else:
                expect(self.partial_form).to_contain_text(expected_owner_name)

        if expected_city:
            self.logger.info(f"Verifying City: '{expected_city}'")
            if self.city_input.is_visible(timeout=3000):
                expect(self.city_input).to_have_value(expected_city)
            else:
                expect(self.partial_form).to_contain_text(expected_city)

        self.logger.info("Application saved verification completed successfully!")
