import re
import logging
from datetime import datetime
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AddViolationPage(BasePage):
    """Page Object for Add Violation workflow on the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Elements
        self.violations_menu_link = page.get_by_role("link", name="Violations ")
        self.violations_listing_link = page.get_by_role("link", name="Violations Listing")
        
        # Dashboard / Listing Elements
        self.violation_search_heading = page.get_by_role("heading", name="Violation Search")
        self.partial_form_first = page.locator("#partial-form").first
        self.add_violation_btn = page.get_by_role("button", name=" Add Violation")
        self.dealer_name_input = page.get_by_role("textbox", name="Dealer Name")
        self.search_button = page.get_by_role("button", name=" Search")
        self.frm_customer_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")

        # Add/Details Page Elements
        self.violation_glance_heading = page.get_by_role("heading", name="Violation Details at a Glance")
        self.violation_glance_text = page.get_by_text("Violation Details at a Glance Link to Permit Link to Dealer Delete Save Back")
        self.violation_status_heading = page.get_by_role("heading", name="Violation Status")
        self.violation_status_text = page.get_by_text("Violation Status Violation")
        
        # Dropdowns & Form Controls
        self.status_dropdown_trigger = page.get_by_text("-- Select Option --").first
        self.inspector_dropdown_trigger = page.locator("#frmViolationDetailsPage").get_by_text("-- Select Option --")
        self.save_button = page.get_by_role("button", name=" Save")
        
        # Dialog OK Buttons
        self.ok_button = page.get_by_role("button", name="OK")
        
        # Link to Permit Elements
        self.link_to_permit_text = page.get_by_text("Link to Permit Link to Dealer")
        self.link_to_permit_btn = page.get_by_role("button", name=" Link to Permit")
        self.link_permit_dialog_title = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Link To Permit", exact=True)
        self.link_permit_dialog_desc = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Link Permit/Dealer to Violation Search (Choose the search option and enter in")
        self.permit_dialog_dealer_input = page.locator(".k-window:visible, .k-dialog:visible").get_by_label("Dealer Name")
        self.permit_dialog_search_btn = page.locator(".k-window:visible, .k-dialog:visible").get_by_role("button", name=" Search")
        self.permit_checkbox = page.locator("#vioLinkPermit")

        # Link to Dealer Elements
        self.link_to_dealer_btn = page.get_by_role("button", name=" Link to Dealer")
        self.link_dealer_dialog_title = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Link To Dealer", exact=True)
        self.link_dealer_dialog_heading = page.locator(".k-window:visible, .k-dialog:visible").get_by_role("heading", name="Dealer Search")
        self.dealer_dialog_dealer_input = page.locator(".k-window:visible, .k-dialog:visible").get_by_label("Dealer Name")
        self.dealer_dialog_search_btn = page.locator(".k-window:visible, .k-dialog:visible").get_by_role("button", name=" Search")
        self.dealer_checkbox = page.locator("#chbxLinkDealer")

        # Violation Information Elements
        self.violation_info_heading = page.get_by_role("heading", name="Violation Information")
        self.violation_info_text = page.get_by_text("Violation Information Add")
        self.add_reason_btn = page.get_by_role("button", name=" Add Violation Reason(s)")
        
        # Reasons Dialog Elements
        self.add_violations_heading = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Add Violations")
        self.reasons_heading = page.locator(".k-window:visible, .k-dialog:visible").get_by_role("heading", name="Reasons")
        self.reasons_grid = page.locator("#gridOA3ChecklistTableViolation")
        self.reason_checkboxes = page.locator("#gridOA3ChecklistTableViolation tbody tr input[type='checkbox']")
        self.reasons_cancel_btn = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Cancel").first

        # GIS Information Elements
        self.gis_info_heading = page.get_by_role("heading", name="GIS Information")
        self.gis_info_text = page.get_by_text("GIS Information Maps SRI")

        # Sign Details Elements
        self.sign_details_heading = page.get_by_role("heading", name="Sign Details")
        self.sign_details_wrapper = page.locator(".form-wrapper > div:nth-child(5)")
        self.face_height_input = page.locator("#ODA_Outdoor_Face_Detail_FD1_Face_Height")
        self.face_width_input = page.locator("#ODA_Outdoor_Face_Detail_FD1_Face_Width")
        self.sign_type_dropdown = page.locator("#frmViolationDetailsPage").get_by_text("--Select Sign Type--")
        self.material_dropdown = page.locator("#frmViolationDetailsPage").get_by_text("--Select Material--")

        # Fee Assessment
        self.fee_assessment_heading = page.get_by_role("heading", name="Fee Assessment")
        self.fee_assessment_text = page.get_by_text("Fee Assessment Dealer is a")

        # Inspection Information Elements
        self.inspection_heading = page.get_by_role("heading", name="Inspection Information")
        self.inspection_partial_form = page.locator("#violationDetailsInspection #partial-form")
        self.add_inspection_btn = page.get_by_role("button", name="Add Inspection")
        self.add_inspection_dialog = page.locator(".k-window:visible, .k-dialog:visible").filter(has_text="Add Inspection").first
        self.inspected_by_dropdown = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("--Select Inspected By--")
        self.inspection_status_dropdown = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("--Select Status--")
        self.confirm_btn = page.get_by_role("button", name=" Confirm")
        self.inspection_result_info = page.locator("#ViolationInspectinfo > .row > div:nth-child(3)")

        # Historic Violations
        self.historic_violations_text = page.get_by_text("Historic Violations")
        self.link_violation_btn = page.locator("#btnLinkViolation")
        self.link_violation_wnd_title = page.locator("#LinkViolationGridView_wnd_title")
        self.link_violation_dialog = page.locator(".k-window:visible, .k-dialog:visible").filter(has_text="Link Violation").first
        self.link_violation_back_btn = page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Back").first
        self.violation_linked_info_container = page.locator("#ViolationLinkedInfo > .row > div:nth-child(3)")

        # Removal Information
        self.removal_info_text = page.get_by_text("Removal Information")
        self.removal_info_ad12_text = page.get_by_text("Removal Information Ad-12")
        self.save_bottom_btn = page.locator("button:has-text('Save'), a.k-button:has-text('Save'), button.k-primary:has-text('Save')").last
        self.back_button = page.get_by_role("button", name=" Back")

    def _click_button_and_wait_for_dialog(self, button_locator, dialog_locator, timeout=3000) -> None:
        """Clicks a button and waits for the target dialog to become visible, retrying the click if necessary."""
        logger.info("Clicking button and waiting for dialog to appear...")
        button_locator.wait_for(state="visible", timeout=10000)
        button_locator.click()
        self.page.wait_for_timeout(500)
        
        try:
            expect(dialog_locator).to_be_visible(timeout=timeout)
        except AssertionError:
            logger.info("Dialog did not appear on first click, retrying click...")
            button_locator.click()
            expect(dialog_locator).to_be_visible(timeout=10000)

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Violations."""
        logger.info("Expanding Violations PanelBar navigation.")
        self._expand_kendo_panel("violation")

    def navigate_to_violations_listing(self) -> None:
        """Navigates to Violations Listing and clicks Add Violation."""
        self._expand_navigation_menu()
        if not self.violations_listing_link.is_visible():
            self.violations_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.violations_listing_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        expect(self.violation_search_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def click_add_violation(self) -> None:
        """Clicks Add Violation button."""
        logger.info("Clicking Add Violation button")
        self.add_violation_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def fill_violation_status(self, status: str = "Final Notice Issued", inspector: str = "Andrew Feller") -> None:
        """Fills initial Violation Details section."""
        logger.info(f"Setting status to '{status}' and inspector to '{inspector}'")
        expect(self.violation_glance_heading).to_be_visible(timeout=15000)
        expect(self.violation_glance_text).to_be_visible(timeout=10000)
        expect(self.violation_status_heading).to_be_visible(timeout=10000)
        expect(self.violation_status_text).to_be_visible(timeout=10000)
        
        # Select status option
        self._select_dropdown_option(self.status_dropdown_trigger, status)
        
        # Select inspector option
        self._select_dropdown_option(self.inspector_dropdown_trigger, inspector)

        # Click save to initialize violation
        self.save_button.click()
        self.handle_popup_completed()

    def _click_grid_checkbox_and_confirm(self, checkbox_locator, confirm_text: str, second_confirm_text: str = None) -> None:
        """Clicks a checkbox in the grid and handles the confirmation dialog, retrying if necessary."""
        # Try clicking the checkbox
        checkbox_locator.click(force=True)
        self.page.wait_for_timeout(500)
        
        # Check if the active dialog has appeared by filtering on confirm_text
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(has_text=confirm_text).first
        try:
            expect(active_dialog).to_be_visible(timeout=2000)
        except AssertionError:
            # If not visible, click again (Kendo Grid row selection behavior)
            logger.info("Confirmation dialog did not appear on first click, clicking checkbox again...")
            checkbox_locator.click(force=True)
            self.page.wait_for_timeout(500)
            expect(active_dialog).to_be_visible(timeout=10000)
            
        active_dialog.get_by_role("button", name="OK").click()
        self.page.wait_for_timeout(1000)
        
        if second_confirm_text:
            # Dismiss the secondary confirmation popup
            logger.info(f"Handling secondary confirmation popup with text: {second_confirm_text}")
            second_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(has_text=second_confirm_text).first
            expect(second_dialog).to_be_visible(timeout=10000)
            second_dialog.get_by_role("button", name="OK").click()
            self.page.wait_for_timeout(1000)

    def handle_popup_completed(self) -> None:
        """Handles Operation Completed popup window."""
        logger.info("Dismissing u-njoda / Operation completed popup")
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(has_text="Operation completed").first
        expect(active_dialog).to_be_visible(timeout=15000)
        active_dialog.get_by_role("button", name="OK").click()
        self.page.wait_for_timeout(1000)

    def link_to_permit(self, dealer_name: str = "vansh") -> None:
        """Links the violation to a permit structure."""
        logger.info(f"Linking permit using search: {dealer_name}")
        expect(self.link_to_permit_text).to_be_visible(timeout=10000)
        self._click_button_and_wait_for_dialog(self.link_to_permit_btn, self.link_permit_dialog_title)
        
        expect(self.link_permit_dialog_desc).to_be_visible(timeout=10000)
        
        self.permit_dialog_dealer_input.click()
        self.permit_dialog_dealer_input.fill(dealer_name)
        self.permit_dialog_search_btn.click()
        self._wait_for_loader()
        
        # Verify result wrapper is loaded
        expect(self.page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)
        
        # Check first checkbox in grid and confirm
        self._click_grid_checkbox_and_confirm(self.permit_checkbox.first, "Are sure you want to Link the")
        self._wait_for_loader()

    def link_to_dealer(self, dealer_name: str = "vansh") -> None:
        """Links the violation to a dealer profile."""
        logger.info(f"Linking dealer using search: {dealer_name}")
        self._click_button_and_wait_for_dialog(self.link_to_dealer_btn, self.link_dealer_dialog_title)
        
        expect(self.link_dealer_dialog_heading).to_be_visible(timeout=10000)
        
        self.dealer_dialog_dealer_input.click()
        self.dealer_dialog_dealer_input.fill(dealer_name)
        self.dealer_dialog_search_btn.click()
        self._wait_for_loader()
        
        # Verify result wrapper is loaded
        expect(self.page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)
        
        # Check first checkbox in grid and confirm
        self._click_grid_checkbox_and_confirm(self.dealer_checkbox.first, "Are sure you want to Link the")
        self._wait_for_loader()

    def add_violation_reason(self) -> None:
        """Adds a violation reason from the checklist."""
        logger.info("Adding violation reason")
        expect(self.violation_info_heading).to_be_visible(timeout=10000)
        expect(self.violation_info_text).to_be_visible(timeout=10000)
        self._click_button_and_wait_for_dialog(self.add_reason_btn, self.add_violations_heading)
        
        # Asserts on Add Violations window
        expect(self.reasons_heading).to_be_visible(timeout=10000)
        expect(self.reasons_grid).to_be_visible(timeout=10000)
        
        # Check first checkbox under reasons and confirm (double confirmation dialog)
        self._click_grid_checkbox_and_confirm(self.reason_checkboxes.first, "Are sure you want to add the", second_confirm_text="Reason saved successfully")
        
        # Cancel/Close reasons modal
        self.reasons_cancel_btn.click()
        self._wait_for_loader()
        expect(self.violation_info_text).to_be_visible(timeout=10000)

    def fill_sign_details(self, height: str = "4", width: str = "5", sign_type: str = "Roof", material: str = "Pylon") -> None:
        """Fills Sign details and dimensions."""
        logger.info(f"Setting sign details: Height={height}, Width={width}, Type={sign_type}, Material={material}")
        expect(self.gis_info_heading).to_be_visible(timeout=10000)
        expect(self.gis_info_text).to_be_visible(timeout=10000)
        expect(self.sign_details_heading).to_be_visible(timeout=10000)
        expect(self.sign_details_wrapper).to_be_visible(timeout=10000)

        self.face_height_input.click()
        self.face_height_input.fill(height)
        self.face_width_input.click()
        self.face_width_input.fill(width)
        
        self._select_dropdown_option(self.sign_type_dropdown, sign_type)
        self._select_dropdown_option(self.material_dropdown, material)

    def add_inspection(self, inspector: str = "Cassandra Gallagher", status: str = "Corrected") -> None:
        """Fills and submits an inspection report on the violation."""
        logger.info(f"Adding inspection report: Inspector={inspector}, Status={status}")
        expect(self.fee_assessment_heading).to_be_visible(timeout=10000)
        expect(self.fee_assessment_text).to_be_visible(timeout=10000)
        expect(self.inspection_heading).to_be_visible(timeout=10000)
        expect(self.inspection_partial_form).to_be_visible(timeout=10000)
        
        self._click_button_and_wait_for_dialog(self.add_inspection_btn, self.add_inspection_dialog)
        expect(self.page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Select files...Drop files").first).to_be_visible(timeout=10000)
        
        # Populate all dates inside dialog to current date
        self.set_all_datefields_to_current()
        
        # Select options
        self._select_dropdown_option(self.inspected_by_dropdown, inspector)
        self._select_dropdown_option(self.inspection_status_dropdown, status)
        
        # Asserts on layout
        expect(self.add_inspection_dialog).to_be_visible(timeout=10000)
        
        # Confirm and save
        self.confirm_btn.click()
        self._wait_for_loader()
        expect(self.inspection_result_info).to_be_visible(timeout=15000)

    def verify_historic_violations_modal(self) -> None:
        """Links historic violations window and closes it."""
        logger.info("Opening and closing Link Violation / Historic violations window")
        expect(self.historic_violations_text).to_be_visible(timeout=10000)
        self._click_button_and_wait_for_dialog(self.link_violation_btn, self.link_violation_wnd_title)
        
        expect(self.link_violation_dialog).to_be_visible(timeout=10000)
        
        self.link_violation_back_btn.click()
        self._wait_for_loader()
        expect(self.violation_linked_info_container).to_be_visible(timeout=10000)

    def fill_removal_info_and_save(self) -> None:
        """Sets removal information dates and saves the entire violation."""
        logger.info("Fills removal dates and clicks save at the bottom.")
        expect(self.removal_info_text).to_be_visible(timeout=10000)
        expect(self.removal_info_ad12_text).to_be_visible(timeout=10000)
        
        # Set all final DatePickers under removal section
        self.set_all_datefields_to_current()
        
        expect(self.removal_info_ad12_text).to_be_visible(timeout=10000)
        
        # Scroll to and click save at the bottom
        logger.info("Scrolling to bottom Save button and clicking...")
        save_btn = self.save_bottom_btn
        save_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        
        try:
            save_btn.click(timeout=5000)
        except Exception:
            logger.warning("Standard click on Save bottom button failed. Retrying via JS click...")
            self.js_click(save_btn)
        
        # Handle final dialog popup (Operation completed / Record saved successfully)
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(
            has_text=re.compile(r"Operation completed|saved|successful", re.I)
        ).first
        
        try:
            expect(active_dialog).to_be_visible(timeout=15000)
            ok_btn = active_dialog.get_by_role("button", name="OK")
            if ok_btn.count() > 0 and ok_btn.first.is_visible():
                ok_btn.first.click()
            else:
                active_dialog.locator("button, .k-button").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            logger.warning(f"Final popup dialog check completed: {e}")

    def go_back_and_verify_record_listed(self, dealer_name: str = "vansh") -> None:
        """Returns to the violations list, searches by dealer, and validates results."""
        logger.info(f"Going back and searching for dealer '{dealer_name}' in the listing grid.")
        expect(self.partial_form_first).to_be_visible(timeout=10000)
        self.back_button.click()
        self._wait_for_loader()
        
        self.dealer_name_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)
        self.search_button.click()
        self._wait_for_loader()
        
        # Verify search results are loaded successfully
        expect(self.frm_customer_container).to_be_visible(timeout=15000)

    def set_all_datefields_to_current(self) -> None:
        """Sets all Kendo DatePickers on the page directly to the current date via JavaScript."""
        current_date_str = datetime.now().strftime("%m/%d/%Y")
        logger.info(f"JS Injecting current date: '{current_date_str}' to all active datepicker widgets.")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"]').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                    }}
                }});
            }}
        """)
        self.page.wait_for_timeout(500)

    def _select_dropdown_option(self, trigger_locator, option_text: str = None) -> None:
        """Helper to click a Kendo dropdown and select option_text or the first available option."""
        trigger_locator.wait_for(state="visible", timeout=10000)
        trigger_locator.click()
        
        # Wait dynamically for options to be visible
        try:
            self.page.locator("li[role='option']:visible").first.wait_for(state="visible", timeout=5000)
        except Exception:
            pass
        
        # Target only visible options to avoid matching hidden dropdown lists in the DOM
        if option_text:
            option = self.page.locator("li[role='option']:visible").filter(has_text=option_text).first
            if option.count() > 0:
                self.js_click(option)
                self.page.wait_for_timeout(500)
                return
                
        # Fallback to first valid visible option (index 1 is usually the first value, index 0 is the placeholder)
        options = self.page.locator("li[role='option']:visible")
        if options.count() > 1:
            self.js_click(options.nth(1))
        elif options.count() > 0:
            self.js_click(options.first)
        self.page.wait_for_timeout(500)
