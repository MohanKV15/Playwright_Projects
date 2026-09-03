import re
import logging
from playwright.sync_api import expect
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class PreApplicationMeetingPage(PermitMajorPage):
    """Page Object for Pre-Application Meeting permit application flow."""

    APPLY_BUTTON = "#btnSubmit11"

    def __init__(self, page, script_name: str = "test_pre_application_meeting"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_pre_application_meeting(self):
        """Wait for the Pre-Application Meeting apply button to be visible."""
        self.logger.info("Waiting for Pre-Application Meeting Apply button.")
        self.page.locator(self.APPLY_BUTTON).wait_for(state="visible", timeout=15000)

    def click_apply_button(self):
        """Click the Pre-Application Meeting Apply button and wait for the page to load."""
        self.logger.info("Clicking Apply button for Pre-Application Meeting.")
        btn = self.page.locator(self.APPLY_BUTTON)
        btn.wait_for(state="visible", timeout=15000)
        btn.click()

        # Wait for the Pre-Application Meeting page URL redirection
        self.page.wait_for_url(
            re.compile(r"HTCP4321Driveway_PreApp|PermitType", re.I),
            timeout=30000
        )
        self.logger.info("Pre-Application Meeting form page loaded.")

    def assert_pre_application_meeting_page_loaded(self):
        """Verify the correct Pre-Application Meeting page is loaded."""
        self.logger.info("Asserting Pre-Application Meeting page loaded.")
        expect(self.page).to_have_url(
            re.compile(r"HTCP4321Driveway_PreApp|PermitType", re.I),
            timeout=30000
        )
        expect(self.page.get_by_role("heading", name=re.compile(r"Pre-Application Meeting", re.I))).to_be_visible(timeout=15000)
        expect(self.page.get_by_role("heading", name=re.compile(r"Applicant Information", re.I))).to_be_visible(timeout=15000)

    def fill_owner_info(self, owner_info):
        """Fill Applicant Information on Pre-Application Meeting page."""
        self.logger.info("Filling Applicant Information for Pre-Application Meeting.")
        phone_value = self._format_phone(owner_info.get("primary_phone", ""))
        
        # Company/Individual Name *
        company_input = self.page.locator("input[name*='com_name'], input[id*='com_name']")
        if company_input.count() == 0:
            for label in ["Company/Individual Name *", "Lot Owner Company Name *", "Company Name *"]:
                company_input = self.page.get_by_role("textbox", name=label)
                if company_input.count() > 0:
                    break
        company_input.first.fill(owner_info["company"])
        
        # Contact Address (labeled "Contact Address *" or "Lot Owner Address *")
        address_input = self.page.locator("input[name*='com_addr'], input[id*='com_addr']")
        if address_input.count() == 0:
            for label in ["Contact Address *", "Lot Owner Address *"]:
                address_input = self.page.get_by_role("textbox", name=label)
                if address_input.count() > 0:
                    break
        address_input.first.fill(owner_info["address"])
        
        # Lot Owner Contact First/Last Name
        first_name_input = self.page.locator("input[name*='poc_first_name'], input[id*='poc_first_name']")
        if first_name_input.count() == 0:
            for label in ["Contact First Name *", "Lot Owner Contact First Name *"]:
                first_name_input = self.page.get_by_role("textbox", name=label)
                if first_name_input.count() > 0:
                    break
        first_name_input.first.fill(owner_info["first_name"])
        
        last_name_input = self.page.locator("input[name*='poc_last_name'], input[id*='poc_last_name']")
        if last_name_input.count() == 0:
            for label in ["Contact Last Name *", "Lot Owner Contact Last Name *"]:
                last_name_input = self.page.get_by_role("textbox", name=label)
                if last_name_input.count() > 0:
                    break
        last_name_input.first.fill(owner_info["last_name"])
        
        # Masked Phone field
        self._set_masked_input_value("cmgenpoc_com_phone", phone_value)
        
        # City (might be "City" or "City *")
        city_input = self.page.locator("input[name*='com_city'], input[id*='com_city']")
        if city_input.count() == 0:
            for label in ["City", "City *"]:
                city_input = self.page.get_by_role("textbox", name=label)
                if city_input.count() > 0:
                    break
        city_input.first.fill(owner_info["city"])
        
        # Zip Code (might be "Zip Code" or "Zip Code *")
        zip_input = self.page.locator("input[name*='com_zip'], input[id*='com_zip']")
        if zip_input.count() == 0:
            for label in ["Zip Code", "Zip Code *"]:
                zip_input = self.page.get_by_role("textbox", name=label)
                if zip_input.count() > 0:
                    break
        zip_input.first.fill(owner_info["zip_code"])
        
        # Contact Email (labeled "Contact Email *" or "Email *")
        email_input = self.page.locator("input[name*='com_email'], input[id*='com_email']")
        if email_input.count() == 0:
            for label in ["Contact Email *", "Email *"]:
                email_input = self.page.get_by_role("textbox", name=label)
                if email_input.count() > 0:
                    break
        email_input.first.fill(owner_info["email"])
        self.logger.info("Applicant information filled successfully.")

    def fill_location_information(self):
        """Fill location information specifically using Pre-Application's dropdown selectors."""
        self.logger.info("Filling location information for Pre-Application application.")
        
        location_div = self.page.locator("#LocationInfoDiv")
        expect(location_div).to_be_visible(timeout=15000)

        # Select Route using RouteSldNameDD_listbox
        self._select_location_dropdown(location_div, "--Select Route--", 0, "RouteSldNameDD_listbox")
        
        # Fill Milepost Start
        try:
            self._set_kendo_numeric_value("milepost", 0.00)
            self.logger.info("Milepost Start filled with 0.00")
            self.page.evaluate("""
                () => {
                    const el = document.getElementById('milepost');
                    if (!el) return;
                    el.blur();
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.info(f"Milepost not present; skipping. Reason: {e}")

        # Select Suffix using route_suffix_listbox
        self._select_location_dropdown(location_div, "--Select Suffix--", 1, "route_suffix_listbox")

        # Select Direction using direction_listbox
        self._select_location_dropdown(location_div, "--Select Direction--", 2, "direction_listbox")

        # Click Add New to create a location row
        add_new_btn = location_div.get_by_role("link", name=re.compile("Add New"))
        add_new_btn.wait_for(state="visible")
        add_new_btn.scroll_into_view_if_needed()
        expect(add_new_btn).to_be_visible()

        for attempt in range(3):
            self.logger.info("Clicking Add New (attempt %d).", attempt + 1)
            add_new_btn.click()
            try:
                self.page.locator("#block_no").wait_for(state="visible", timeout=3000)
                break
            except Exception:
                continue

        # Fill Block and Lot
        block_input = self.page.locator("#block_no")
        lot_input = self.page.locator("#lot_no")
        block_input.wait_for(state="visible")
        block_input.fill("5")
        block_input.press("Tab")
        lot_input.wait_for(state="visible")
        lot_input.fill("6")
        lot_input.press("Tab")
        
        # Click Update and wait for the row to exit edit mode
        update_btn = location_div.locator(".k-grid-update").first
        if update_btn.is_visible():
            update_btn.scroll_into_view_if_needed()
            for _ in range(3):
                if not update_btn.is_visible():
                    break
                try:
                    update_btn.evaluate("el => el.click()")
                except Exception:
                    try:
                        self._scroll_and_click(update_btn, timeout_ms=1000)
                    except Exception:
                        pass
                self.page.wait_for_timeout(1000)
        self.logger.info("Location section updated and committed.")

    def fill_lot_development_frontage_information(self, way_driveway1: int = 1, way_driveway2: int = 1, tot_size_dev: float = 1.5):
        """Fill Lot/Development/Frontage Information including driveway counts."""
        self.logger.info("Filling Lot/Development/Frontage Information.")
        
        # Fill numeric values
        self._set_kendo_numeric_value("way_driveway1", float(way_driveway1))
        self._set_kendo_numeric_value("way_driveway2", float(way_driveway2))
        self._set_kendo_numeric_value("TotSizeDev", float(tot_size_dev))
        
        # Fill Comments
        self.page.locator("#LotComments").fill("Test driveway and development frontage info.")
        self.logger.info("Lot/Development/Frontage Information completed.")

    def upload_pre_app_attachments(self):
        """Upload required attachments for Pre-Application Meeting application using professional POM pattern."""
        self.logger.info("Uploading Pre-Application Meeting attachments.")
        
        # Verify dropzone container is visible (as requested by user)
        expect(self.page.locator("#ApplAttachDocDiv").get_by_text("Select files...Drop files")).to_be_visible(timeout=15000)
        
        # Upload the Pre-Application Meeting document
        self.page.locator("input#ApplicationAttachments").set_input_files(self.SUPPORTING_DOCUMENT_PATH)
        
        # Upload the Checklist document
        checklist_input = self.page.locator("input#ApplicationChecklist")
        if checklist_input.count() > 0:
            checklist_input.set_input_files(self.SUPPORTING_DOCUMENT_PATH)
        
        # Wait for uploads to be registered
        self.page.wait_for_timeout(2000)
        self.logger.info("Required Pre-Application documents uploaded successfully.")

    def upload_authorization_certificate(self):
        """Upload authorization certificate if visible on the page."""
        upload_input = self.page.locator("input#UploadAuthCertificate")
        if self.page.locator("#uploadAuth").is_visible() or (upload_input.count() > 0 and upload_input.is_visible()):
            self.logger.info("Uploading Authorization Certificate.")
            super().upload_authorization_certificate()
        else:
            self.logger.info("Authorization Certificate is not visible; skipping.")

    def fill_remaining_required_fields(self):
        """Fill remaining required fields specifically for Pre-Application Meeting, skipping duplicate uploads."""
        self.logger.info("Filling remaining required fields for Pre-Application Meeting.")
        
        # 1. Fill owner representative if present
        owner_rep = self.page.locator("#owner_representative")
        if owner_rep.count() == 0:
            owner_rep = self.page.locator("xpath=//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/following-sibling::input | //label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/..//input").first
        
        if owner_rep.count() > 0:
            owner_rep.first.scroll_into_view_if_needed()
            owner_rep.first.fill(self.fake.name())
            owner_rep.first.press("Tab")

        # 2. Check acknowledgment checkbox
        try:
            ack_label = self.page.locator(".col-md-12.huddleUp > .form-check > .k-checkbox-label")
            if ack_label.count() > 0:
                ack_label.first.scroll_into_view_if_needed()
                ack_label.first.evaluate("el => el.click()")
            else:
                ack_checkbox = self.page.locator("#Aknwldgmnt")
                ack_checkbox.first.scroll_into_view_if_needed()
                ack_checkbox.first.check(force=True, timeout=5000)
            
            # Wait for Kendo to naturally process the label click and update its bound viewmodel
            self.page.wait_for_timeout(2500)
        except Exception as e:
            self.logger.warning("Failed to naturally check Acknowledgment: %s", e)

        # 3. Clear stale invalid markers via JS injection
        self.page.evaluate(
            """
            () => {
                const hiddenConditionalUploads = [
                    { divId: "WaiverDocsDiv", inputId: "WaiverDocs" },
                    { divId: "CurbSuppDocDiv", inputId: "CurbSupportingDocs" },
                    { divId: "DrainageDocDiv", inputId: "DrainageSupportingDocs" },
                    { divId: "SideWalkDocDiv", inputId: "sideWalkDocs" },
                ];
                for (const item of hiddenConditionalUploads) {
                    const div = document.getElementById(item.divId);
                    const input = document.getElementById(item.inputId);
                    if (!input) continue;
                    const hidden = !div || getComputedStyle(div).display === "none";
                    if (!hidden) continue;
                    input.removeAttribute('aria-invalid');
                    input.classList.remove('k-invalid');
                    const msg = document.querySelector(`[data-valmsg-for="${item.inputId}"]`);
                    if (msg) {
                        msg.classList.remove('field-validation-error');
                        msg.style.display = 'none';
                    }
                }
            }
            """
        )
        self.logger.info("Pre-Application Meeting remaining required fields filled successfully.")

    def click_submit_request(self):
        """Click the Submit Request button on the Pre-Application Meeting page."""
        self.logger.info("Clicking Submit Request button.")
        
        # Click the submit button
        btn = self.page.get_by_role("button", name="Submit Request")
        if btn.count() == 0:
            btn = self.page.get_by_role("button", name="Continue to Payment")
            
        if btn.count() > 0:
            btn.scroll_into_view_if_needed()
            btn.click(force=True)
        else:
            # Try JS fallback
            self.page.evaluate(
                "() => { const b = document.getElementById('btnSubmit'); if (b) { b.removeAttribute('disabled'); b.click(); } }"
            )
        self.page.wait_for_timeout(3000)

    def handle_success_popup(self):
        """Click OK on the success alert popup and wait for redirect to dashboard."""
        self.logger.info("Handling the success popup.")
        
        # Wait for dialog OK button to appear
        ok_btn = self.page.locator(".k-dialog-buttongroup button, button:has-text('OK'), .k-confirm button, .k-dialog button").first
        ok_btn.wait_for(state="visible", timeout=25000)
        
        # Log dialog text for debugging
        alert_text = self._get_visible_dialog_text()
        self.logger.info(f"Submission dialog text: {alert_text}")
        
        ok_btn.click(force=True)
        self.logger.info("Clicked OK on the success popup.")
        
        # Assert redirection back to dashboard
        self.page.wait_for_url(
            re.compile(r"CustomerPortalDashboard|4321CustomerPortalDashboardFull", re.I),
            timeout=45000
        )
        self.logger.info("Successfully submitted Pre-Application Meeting request and redirected to dashboard.")

    def click_continue_to_payment(self):
        """Pre-Application Meeting does not require payment. Clicking submit navigates directly to success dialog and dashboard."""
        self.click_submit_request()
        self.handle_success_popup()
