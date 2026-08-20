import re
import logging
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitApplicationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Button to start the Permit Application submission
        self.permit_app_button = page.locator("#btnPermitApp")
        
        # Dialog notification message checking domain validation
        self.domain_dialog = page.locator("div").filter(has_text=re.compile(r"^u-njcp\.bemcorp\.net$"))
        
        # OK confirmation button inside the popup/dialog
        self.ok_button = page.get_by_role("button", name="OK")

        # --- Form Container & Fields ---
        self.partial_form = page.locator("#partial-form").first
        
        # Dimensions
        self.face_height = page.locator("#ODA_Outdoor_Face_Detail_Face_Height1")
        self.face_width = page.locator("#ODA_Outdoor_Face_Detail_Face_Width1")
        
        # Dropdowns (IDs for Kendo UI widgets used in JS evaluation)
        self.sign_type_dropdown = "#ODA_Outdoor_Structure_SignType"
        self.material_dropdown = "#ODA_Outdoor_Structure_SignMaterial"
        self.county_dropdown = "#EP_Permit_Application_County"
        self.state_dropdown = "#cmgenadd_state_d"
        
        # Radios & Checkboxes
        self.first_radio_label = page.locator(".k-radio-label").first
        self.first_checkbox_label = page.locator(".k-checkbox-label").first
        
        # Certification & Acknowledgment Checkboxes
        self.ack_checkbox_1 = page.locator(".col-md-12 > .form-check > .k-checkbox-label").first
        self.ack_checkbox_2 = page.locator("div:nth-child(3) > .form-check > .k-checkbox-label")
        self.ack_checkbox_3 = page.locator("div:nth-child(6) > .col-md-12.huddleUp > .form-check > .k-checkbox-label")
        
        # Text Inputs
        self.sign_location_input = page.get_by_role("textbox", name="Location of Sign *")
        self.block_input = page.get_by_role("textbox", name="Block (NA if not known or not")
        self.lot_input = page.get_by_role("textbox", name="Lot (NA if not known or not")
        self.property_owner_name = page.get_by_role("textbox", name="Property Owner Name *")
        self.property_owner_address = page.get_by_role("textbox", name="Property Owner Address 1 *")
        self.city_input = page.get_by_role("textbox", name="City *")
        self.zip_code_input = page.get_by_role("textbox", name="Zip Code *")
        
        # Certification Signer Details
        self.cert_name_input = page.get_by_role("textbox", name="Name *", exact=True)
        self.cert_title_input = page.get_by_role("textbox", name="Title *")
        
        # Date Picker Trigger
        self.date_picker_button = page.get_by_role("button", name="select")
        
        # Complete Payment Submit Button
        self.complete_payment_button = page.get_by_role("button", name=" Complete Payment")

    def click_permit_application(self) -> None:
        """Clicks the 'Permit Application' button to begin submission."""
        logger.info("Clicking '#btnPermitApp' button to start permit application")
        self.permit_app_button.click()

    def verify_domain_dialog_visible(self) -> None:
        """Verifies that the domain validation dialog is visible on the page."""
        logger.info("Asserting domain validation dialog visibility with regex pattern matching")
        expect(self.domain_dialog).to_be_visible()

    def dismiss_dialog(self) -> None:
        """Dismisses the modal warning dialog by clicking the OK button."""
        logger.info("Clicking the dialog confirmation OK button")
        self.ok_button.click()

    def _select_first_valid_option(self, element_id: str, value_text: str = None) -> None:
        """
        Selects a Kendo DropDownList option using JavaScript.
        If value_text is provided, matches and selects that option.
        Otherwise, selects the first valid (non-placeholder) option.
        """
        print(f"\n[DROPDOWN] Selecting '{value_text or 'first valid'}' for Kendo widget: {element_id}")
        
        # Bypassed scrolling hidden element into view to improve execution speed.
        # Kendo dropdown selection via JavaScript evaluation works directly without scrolling.
            
        # 2. Wait up to 15 seconds for the data source to be populated (critical for AJAX)
        self.page.wait_for_function(f"""() => {{
            var el = jQuery("{element_id}");
            if (el.length === 0) return false;
            var dropdown = el.data("kendoDropDownList");
            return dropdown && dropdown.dataSource && dropdown.dataSource.data().length > 0;
        }}""", timeout=15000)
        
        # 3. Select option via Kendo API and trigger 'change'
        result = self.page.evaluate(f"""([sel, valText]) => {{
            var el = jQuery(sel);
            var dropdown = el.data("kendoDropDownList");
            if (!dropdown) return null;
            
            var index = -1;
            if (valText) {{
                var data = dropdown.dataSource.data();
                var textProp = dropdown.options.dataTextField;
                for (var i = 0; i < data.length; i++) {{
                    var itemText = data[i][textProp];
                    if (itemText && itemText.toString().trim() === valText) {{
                        index = i;
                        break;
                    }}
                }}
            }}
            
            var selectIndex = -1;
            if (index !== -1) {{
                selectIndex = dropdown.options.optionLabel ? index + 1 : index;
            }} else {{
                selectIndex = dropdown.options.optionLabel ? 1 : 0;
            }}
            
            dropdown.select(selectIndex);
            dropdown.trigger("change");
            return dropdown.text();
        }}""", [element_id, value_text])
        
        if result:
            print(f"[DROPDOWN] Successfully selected '{result}' in {element_id}")
        else:
            print(f"[DROPDOWN] Failed to select option in {element_id}")

    def fill_permit_application_form(self, file_path: str | None = None) -> None:
        """Fills the permit application form with dynamic Faker test data and uploads documents."""
        import os
        from utils.config import Config
        if not file_path or not os.path.exists(file_path):
            file_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")

        from faker import Faker
        fake = Faker()
        
        # 1. Verify partial form container is visible
        logger.info("Verifying partial form visibility")
        expect(self.partial_form).to_be_visible(timeout=15000)
        
        # 2. Dimensions (Face Height / Face Width)
        logger.info("Entering face dimensions via Kendo Numeric API")
        self._set_kendo_numeric_value("ODA_Outdoor_Face_Detail_Face_Height1", 20)
        self._set_kendo_numeric_value("ODA_Outdoor_Face_Detail_Face_Width1", 50)
        
        # 3. Select Sign Type (Kendo Dropdown - 1st valid option)
        logger.info("Selecting Sign Type: 1st valid option")
        self._select_first_valid_option(self.sign_type_dropdown)
        
        # 4. Select Material (Kendo Dropdown - 1st valid option)
        logger.info("Selecting Material: 1st valid option")
        self._select_first_valid_option(self.material_dropdown)
        
        # 5. Message Option selection (using force=True to bypass actionability/layout checks under zoom)
        logger.info("Selecting message option radios and checkboxes")
        self.first_radio_label.click(force=True)
        self.first_checkbox_label.click(force=True)
        
        # 6. Select County (Kendo Dropdown - Atlantic)
        logger.info("Selecting County: Atlantic")
        self._select_first_valid_option(self.county_dropdown, "Atlantic")
        
        # 7. Sign Location Details
        logger.info("Entering sign location description")
        self.sign_location_input.fill(fake.street_address())
        self.block_input.fill("NA")
        self.lot_input.fill("NA")
        
        # 8. Upload Sketch of Location (First upload dropzone)
        logger.info(f"Uploading Sketch of Location using file: {file_path}")
        self.page.locator(".k-upload").nth(0).locator("input[type='file']").first.set_input_files(file_path)
            
        # 9. Property Owner Contact Info
        logger.info("Entering property owner details")
        self.property_owner_name.fill(fake.name())
        self.property_owner_address.fill(fake.street_address())
        self.city_input.fill(fake.city())
        
        # 10. Select State: New Jersey (Kendo Dropdown - New Jersey)
        logger.info("Selecting State: New Jersey")
        self._select_first_valid_option(self.state_dropdown, "New Jersey")
        
        # 11. Zip Code
        self.zip_code_input.fill("08401")
        
        # 12. Upload Property Owner Consent (Second upload dropzone)
        logger.info("Uploading Property Owner Consent Document")
        self.page.locator(".k-upload").nth(1).locator("input[type='file']").first.set_input_files(file_path)
        
        # 13. Acknowledgment Checkboxes (using force=True to bypass actionability/layout checks under zoom)
        logger.info("Checking certification acknowledgment checkboxes")
        self.ack_checkbox_1.click(force=True)
        self.ack_checkbox_2.click(force=True)
        self.ack_checkbox_3.click(force=True)
        
        # 14. Certification Signer Name & Title
        logger.info("Entering certification signature values")
        self.cert_name_input.fill(fake.name())
        self.cert_title_input.fill(fake.job())
        
        # 15. Date Selection
        logger.info("Filling current date directly")
        from datetime import datetime
        current_date = datetime.now().strftime("%m/%d/%Y")
        self.page.locator("#Date").fill(current_date)
                
        # 16. Click Complete Payment
        # This triggers a Kendo DOM popup: "Record saved successfully. Please use the
        # application number for your reference: [SUB-XXXXX]"
        logger.info("Clicking Complete Payment button")
        self.complete_payment_button.click()

        # 17. Wait for the Kendo "Record saved successfully" DOM popup and click OK.
        # This popup confirms the application was saved and provides the SUB reference number.
        logger.info("Waiting for Record saved successfully popup")
        ok_button = self.page.get_by_role("button", name="OK")
        ok_button.wait_for(state="visible", timeout=30000)
        logger.info("Record saved popup appeared -- registering native dialog handler and clicking OK")
        self.page.once("dialog", lambda dialog: dialog.accept())
        ok_button.click()
        logger.info("Clicked OK -- navigating to payment gateway page")
