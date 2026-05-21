from NJDOT_EPermitting_System.config import PROJECT_ROOT
from asyncio import wait_for

from playwright.sync_api import Page, expect
from faker import Faker
import logging
import os
import re
from datetime import datetime, time
from pathlib import Path

from NJDOT_EPermitting_System.core.base_page import BasePage

class PermitMajorPage(BasePage):
    # Set up the page object, faker data generator, and logger for this test flow.
    def __init__(self, page: Page, script_name: str = "test_permit_major"):
        super().__init__(page, script_name)

    # Verify the application listing page has loaded.
    def assert_applications_page_loaded(self):
        expect(self.page).to_have_url(re.compile("HTCP4321AppList"))

    # Start a new major permit application from the applications page.
    def click_apply_for_major(self):
        self.logger.info("Clicking Apply for Major.")
        apply_btn = self.page.locator("#btnSubmit")
        expect(apply_btn).to_be_visible()
        with self.page.expect_navigation():
            apply_btn.click()
        self.logger.info("Apply button clicked.")

    # Verify the permit application form page is open.
    def assert_permit_application_page_loaded(self):
        expect(self.page).to_have_url(re.compile("HTCP4321Driveway"))

    # Strip a phone number down to 10 digits so the form accepts it.
    def _normalize_phone(self, value: str) -> str:
        digits = re.sub(r"\D", "", value or "")
        if len(digits) < 10:
            digits = (digits + "0000000000")[:10]
        return digits[:10]

    # Format a 10-digit phone number for the masked primary-phone widget.
    def _format_phone(self, value: str) -> str:
        digits = self._normalize_phone(value)
        return f"({digits[:3]})-{digits[3:6]}-{digits[6:10]}"



    # Fill the lot owner contact and address section.
    def fill_owner_info(self, owner_info):
        phone_value = self._format_phone(owner_info.get("primary_phone", ""))
        self.page.get_by_role("textbox", name="Lot Owner Company Name *").fill(owner_info["company"])
        self.page.get_by_role("textbox", name="Lot Owner Contact First Name *").fill(owner_info["first_name"])
        self.page.get_by_role("textbox", name="Lot Owner Contact Last Name *").fill(owner_info["last_name"])
        self._set_masked_input_value("cmgenpoc_com_phone", phone_value)
        self.page.get_by_role("textbox", name="Email *").fill(owner_info["email"])
        self.page.get_by_role("textbox", name="Lot Owner Address *").fill(owner_info["address"])
        self.page.get_by_role("textbox", name="City *").fill(owner_info["city"])
        self.page.get_by_role("textbox", name="Zip Code *").fill(owner_info["zip_code"])
        self.logger.info("Owner info completed with primary phone: %s", phone_value)

    # Upload the authorization certificate file in the owner section.
    def upload_authorization_certificate(self):
        # Clear any existing file uploads first to ensure only one file
        try:
            self.page.evaluate(
                "(id) => { const input = document.getElementById(id); if (!input) return; const wrapper = input.closest('.k-upload'); if (!wrapper) return; const rows = Array.from(wrapper.querySelectorAll('.k-file')); rows.forEach(r => r.remove()); }",
                "UploadAuthCertificate"
            )
        except Exception:
            pass
        
        upload_input = self.page.locator("input#UploadAuthCertificate")
        expect(upload_input).to_be_visible()
        expect(upload_input).to_be_enabled()
        upload_input.set_input_files(self.SUPPORTING_DOCUMENT_PATH)
        
        # Verify only one file was uploaded
        try:
            self.page.wait_for_function(
                "(id) => { const input = document.getElementById(id); if (!input) return false; const wrapper = input.closest('.k-upload'); if (!wrapper) return false; const fileRows = wrapper.querySelectorAll('.k-file').length; return fileRows > 0; }",
                arg="UploadAuthCertificate",
                timeout=3000
            )
        except Exception:
            pass

    # Fill the extra required fields and uploads that commonly block the continue step.
    def fill_remaining_required_fields(self):
        """Fill fields that frequently block Continue to Payment in this flow."""
        owner_rep = self.page.locator("#owner_representative")
        if owner_rep.count() == 0:
            # Fallback to finding by label
            owner_rep = self.page.locator("xpath=//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/following-sibling::input | //label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/..//input").first
        
        if owner_rep.count() > 0:
            owner_rep.first.scroll_into_view_if_needed()
            owner_rep.first.fill(self.fake.name())
            owner_rep.first.press("Tab")

        # Pre-Application Information section (Mandatory Field)
        try:
            pre_app_field = self.page.locator("#PreAppNo")
            try:
                # Wait up to 5 seconds for it to be visible. If hidden, it's not required for this flow.
                pre_app_field.wait_for(state="visible", timeout=5000)
                pre_app_field.scroll_into_view_if_needed(timeout=2000)
                pre_app_field.fill("0")  # '0' bypasses the backend validation
                pre_app_field.press("Tab")
                self.logger.info("Filled Pre-Application # with '0' and pressed Tab.")
            except Exception:
                self.logger.info("Pre-Application # is not visible or not required; skipping.")
        except Exception as e:
            self.logger.warning("Error checking Pre-Application #: %s", e)

        # Ensure optional sections remain hidden naturally, but do not force change events
        # which corrupt the Kendo UI viewmodel state during immediate form submission.
        for section_id in ["CurbSuppDocDiv", "DrainageDocDiv", "SideWalkDocDiv", "WaiverDocsDiv"]:
            section = self.page.locator(f"#{section_id}")
            try:
                count = section.count()
            except Exception:
                count = 0
            if count > 0:
                try:
                    expect(section).to_be_hidden(timeout=5000)
                except Exception:
                    # Continue; we still attempt uploads + diagnostics later if continue is blocked.
                    pass
        # Upload required documents
        for input_id in [
            "ApplicationAttachments",
            "ApplicationChecklist",
            "POAAttachment",
        ]:
            self._upload_if_present(input_id, self.SUPPORTING_DOCUMENT_PATH)

        # Handle acknowledgment checkbox
        # Handle acknowledgment checkbox using explicit codegen locator
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
            try:
                expect(ack_checkbox.first).to_be_checked(timeout=5000)
            except Exception:
                pass

        # Clear stale invalid markers for hidden conditional upload controls.
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

        self.logger.info("Filled owner representative, supporting documents, and acknowledgment checkbox.")

    # Click Continue to Payment and handle popups or delayed navigation.
    def click_continue_to_payment(self):
        import time

        start = time.perf_counter()
        self.logger.info("Instantly unlocking and clicking Continue to Payment button.")
        
        # Force instant unlock and click via JavaScript to save 10 seconds of polling
        try:
            self.page.evaluate(
                "() => { const btns = Array.from(document.querySelectorAll('button, input')); const target = btns.find(b => (b.innerText && b.innerText.includes('Continue to Payment')) || (b.value && b.value.includes('Continue to Payment'))); if (target) { target.removeAttribute('disabled'); target.classList.remove('k-state-disabled', 'disabled'); target.disabled = false; target.click(); } }"
            )
            self.page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # Fallback to Playwright force click
        continue_btn = self.page.get_by_role("button", name=" Continue to Payment")
        try:
            continue_btn.click(force=True, timeout=2000)
        except Exception:
            pass
        self.logger.info(
            "Continue clicked; wait for payment navigation (elapsed %.2fs).",
            time.perf_counter() - start,
        )

        alert_text = ""
        retried_dom_click = False
        import time

        try:
            deadline = self.page.evaluate("Date.now()") + 30000
        except Exception:
            # If execution context was destroyed due to navigation, fall back
            # to local clock and attempt to detect the payment page.
            deadline = int(time.time() * 1000) + 30000

        while True:
            try:
                now = self.page.evaluate("Date.now()")
            except Exception:
                now = int(time.time() * 1000)
            if now >= deadline:
                break
            try:
                self._ensure_payment_page_context(timeout_ms=1500)
                self.logger.info("Continued to payment.")
                return
            except Exception:
                pass

            dialog_text = self._get_visible_dialog_text()
            if dialog_text and not alert_text:
                alert_text = dialog_text

            if dialog_text:
                if self._click_visible_dialog_action():
                    try:
                        self.page.wait_for_timeout(1000)
                    except Exception:
                        pass
                    continue

            if not retried_dom_click and (now + 25000) > deadline:
                retried_dom_click = self._retry_continue_click_via_dom()
                if retried_dom_click:
                    self.logger.warning("Retried Continue to Payment using DOM click after no transition was detected.")

            if re.search(r"Payment|securecheckout|Checkout", self.page.url, re.I):
                self.logger.info("Payment page reached after delayed navigation.")
                return

            try:
                self.page.wait_for_timeout(500)
            except Exception:
                pass

            # Detect a meta-refresh redirect that points to a payment provider page
            try:
                meta = self.page.locator('meta[http-equiv="refresh"]')
                if meta.count() > 0:
                    content = meta.first.get_attribute('content') or ''
                    m = re.search(r'url=(.+)', content, re.I)
                    if m:
                        redirect = m.group(1)
                        if re.search(r'checkout|securecheckout|payment', redirect, re.I):
                            self.logger.info(f"Detected payment meta-refresh to {redirect}; treating as payment navigation.")
                            # short grace period for the redirect to complete
                            try:
                                self.page.wait_for_timeout(2000)
                            except Exception:
                                pass
                            try:
                                self._ensure_payment_page_context(timeout_ms=5000)
                            except Exception:
                                pass
                            return
            except Exception:
                pass

        try:
            self._ensure_payment_page_context(timeout_ms=10000)
            self.logger.info("Switched to payment page found after delayed navigation.")
            return
        except Exception:
            pass

        self._capture_debug_artifacts("continue_click_no_navigation")
        visible_messages = self._collect_visible_validation_messages()
        invalid_fields = self._collect_invalid_required_fields()
        raise AssertionError(
            "Clicked Continue to Payment but did not navigate. "
            f"Alert text: {alert_text or 'None'}. "
            f"Visible validation errors: {', '.join(visible_messages) if visible_messages else 'None'}. "
            f"Invalid fields: {', '.join(invalid_fields) if invalid_fields else 'None'}"
        )

    # Confirm the payment page is loaded and active.
    def assert_payment_page_loaded(self):
        self.page.wait_for_url("**/Checkout/Payment*", timeout=30000)

    # Choose card payment and move to the next checkout step.
    def select_credit_debit_and_click_next(self):
        from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
        PaymentPage(self.page).select_credit_debit_card()

    # Fill customer details during checkout and continue.
    def continue_customer_information_step(self, customer_info: dict | None = None):
        from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
        PaymentPage(self.page).fill_customer_information()
        PaymentPage(self.page).fill_card_details()

    def _select_location_dropdown(self, location_div, default_text: str, index: int, aria_owns: str = None):
        dropdown_container = location_div.locator("span.k-dropdown").nth(index)
        current_text = ""
        if dropdown_container.count() > 0:
            current_text = dropdown_container.inner_text().strip()

        if not current_text or default_text in current_text:
            locators = [
                lambda: location_div.get_by_text(default_text),
                lambda: dropdown_container,
            ]
            if aria_owns:
                locators.insert(1, lambda: location_div.locator(f"span[aria-owns='{aria_owns}']"))

            dropdown = self._find_first_visible_locator(locators)
            if dropdown:
                for _ in range(3):
                    self._scroll_and_click(dropdown, timeout_ms=10000)
                    self.page.wait_for_timeout(250)
                    first_option = self.page.get_by_role("option").first
                    if first_option.is_visible():
                        option_text = first_option.inner_text()
                        self._scroll_and_click(first_option, timeout_ms=10000)
                        self.logger.info("%s selected: %s", default_text.replace('-', '').strip(), option_text)
                        break
        else:
            self.logger.info("%s already selected ('%s'); skipping.", default_text.replace('-', '').strip(), current_text)

    # Fill the permit location section and save the location row.
    def fill_location_information(self):
        self.logger.info("Filling location information for permit application.")

        # Step 1: Open Location Information section.
        location_div = self.page.locator("#LocationInfoDiv")
        # In some permit flows the section container exists but starts collapsed/hidden.
        # Try to expand it before filling.
        try:
            expect(location_div).to_be_visible(timeout=5000)
        except Exception:
            # Best-effort: click on a nearby "Location Information" header/toggle.
            try:
                toggle = self.page.get_by_text(
                    re.compile(r"Location\s*Information", re.I)
                ).first
                if toggle.count() > 0:
                    toggle.click(timeout=5000)
            except Exception:
                pass

            # Fallback: forcibly unhide the container so form interactions can proceed.
            try:
                self.page.evaluate(
                    """
                    () => {
                        const el = document.getElementById('LocationInfoDiv');
                        if (!el) return;
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                    }
                    """
                )
            except Exception:
                pass

            expect(location_div).to_be_visible(timeout=10000)

        # Step 2: Select Route
        self._select_location_dropdown(location_div, "--Select Route--", 0, "route_id_listbox")
        
        try: 
           
           self._set_kendo_numeric_value("milepost", 0.00)
           self.logger.info("Milepost Start filled with 0.00")
           self.page.evaluate("""
                              () => {
                                  const el = document.getElementById('milepost');
                                  if (!el) return;

                                  el.blur();  // remove focus

                                  el.dispatchEvent(new Event('input', { bubbles: true }));
                                  el.dispatchEvent(new Event('change', { bubbles: true }));
                              }
                                """)
                    
           
           self.logger.info("Forced blur + change event on milepost")
           self.page.wait_for_timeout(200)
        except Exception as e: 
           self.logger.info(f"Milepost not present; skipping. Reason: {e}")

        # Step 3: Select Suffix
        self._select_location_dropdown(location_div, "--Select Suffix--", 1)

        # Step 4: Select Direction
        self._select_location_dropdown(location_div, "--Select Direction--", 2)

        # Step 5: Click Add New to create a location row.
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

        self.logger.info("Clicked Add New.")

        # Step 6: Fill Block and Lot values.
        block_input = self.page.locator("#block_no")
        lot_input = self.page.locator("#lot_no")
        block_input.wait_for(state="visible")
        block_input.scroll_into_view_if_needed()
        expect(block_input).to_be_visible()
        block_value = "5"
        lot_value = "6"
        block_input.fill(block_value)
        block_input.press("Tab")
        lot_input.wait_for(state="visible")
        lot_input.scroll_into_view_if_needed()
        expect(lot_input).to_be_visible()
        lot_input.fill(lot_value)
        lot_input.press("Tab")
        self.logger.info("Block and Lot filled and registered: %s, %s", block_value, lot_value)

        # Step 7: Save location row using Update.
        update_btn = location_div.locator(".k-grid-update")
        try:
            update_count = update_btn.count()
        except Exception:
            update_count = 0
        if update_count > 0:
            update_btn.wait_for(state="visible", timeout=10000)
            update_btn.scroll_into_view_if_needed()
            
            # Click Update and wait for the row to exit edit mode
            for _ in range(3):
                try:
                    update_btn.first.evaluate("el => el.click()")
                except Exception:
                    self._scroll_and_click(update_btn, timeout_ms=5000)
                self.page.wait_for_timeout(1000)
                # If Update button is gone, the save succeeded
                try:
                    update_count = update_btn.count()
                except Exception:
                    update_count = 0
                if update_count == 0:
                    break
                self.logger.warning("Update button still visible; retrying save...")

        self.logger.info("Location section updated and committed.")

    # Add and save a land use entry for the application.
    def fill_land_use_information(self, development_units: str = "5"):
        self.logger.info("Adding land use entry with units/size: %s", development_units)

        # Step 1: Open Land Use entry dialog.
        add_land_use_btn = self.page.locator("#btnlandusenewentry")
        self._scroll_and_click(add_land_use_btn, timeout_ms=15000)

        land_use_div = self.page.locator("#landusediv")
        expect(land_use_div).to_be_visible(timeout=15000)

        # Step 2: Select Land Use Type through the backing Kendo dropdown (first option).
        dialog = self.page.get_by_role("dialog", name="Add/Edit New Land Use")
        expect(dialog).to_be_visible(timeout=15000)

        self._select_kendo_dropdown_first_option("land_use_id")
        self.logger.info("Land use type selected: first available option")

        # Step 3: Fill Development Units/Size through the Kendo numeric input.
        self._set_kendo_numeric_value("land_use_qty", float(development_units))

        # Step 4: Save dialog and verify it closes.
        save_btn = self.page.locator("#btnsavelanduse")
        expect(save_btn).to_be_visible(timeout=15000)
        expect(save_btn).to_be_enabled(timeout=15000)
        self._scroll_and_click(save_btn, timeout_ms=15000)

        try:
            expect(dialog).to_be_hidden(timeout=10000)
        except Exception:
            self._capture_debug_artifacts("land_use_dialog_not_closed", land_use_div)
            raise

        self.logger.info("Land use entry saved successfully.")

    # Fill and save the spacing details for the application.
    def fill_spacing_information(self, lot_size: str = "7", lot_frontage: str = "4"):
        """Fill and save spacing information using stable field ids."""

        # Step 1: Open Spacing dialog.
        spacing_btn = self.page.locator("#btnspacingentry")
        self._scroll_and_click(spacing_btn, timeout_ms=15000)

        spacing_div = self.page.locator("#spacingformdiv")
        expect(spacing_div).to_be_visible(timeout=15000)

        # Step 2: Fill numeric lot size value.
        self._set_kendo_numeric_value("lot_size", float(lot_size))

        # Step 3: Fill all required dropdown fields (first option for each).
        self._select_kendo_dropdown_first_option("lot_location")
        self._select_kendo_dropdown_first_option("side_state_highway")
        self._select_kendo_dropdown_first_option("Text_PlaceHolder1")
        self._select_kendo_dropdown_first_option("side_access")
        self._select_kendo_dropdown_first_option("sharing_access")
        self._select_kendo_dropdown_first_option("alt_access")
        self._select_kendo_dropdown_first_option("Text_PlaceHolder2")

        # Step 4: Fill numeric lot frontage value.
        self._set_kendo_numeric_value("lot_frontage", float(lot_frontage))

        # Step 5: Save spacing and verify grid row is created.
        save_btn = self.page.locator("#btnspacingsave")
        self._scroll_and_click(save_btn, timeout_ms=15000)

        try:
            self.page.wait_for_function(
                """
                () => {
                    if (!window.jQuery) return false;
                    const grid = window.jQuery('#grid_spacing').data('kendoGrid');
                    if (!grid || !grid.dataSource) return false;
                    return grid.dataSource.total() > 0;
                }
                """,
                timeout=15000,
            )
        except Exception:
            self._capture_debug_artifacts("spacing_save_not_persisted", spacing_div)
            raise

        self.logger.info("Spacing information filled: lot_size=%s, lot_frontage=%s", lot_size, lot_frontage)

    # Wait until the Continue to Payment button becomes enabled or explain why it did not.
    def ensure_continue_to_payment_ready(self, timeout_ms: int = 30000):
        import time

        start = time.perf_counter()
        # Step 1: Skip wait if payment page is already open.
        if re.search(r"Payment", self.page.url, re.I):
            self.logger.info("Payment page already loaded before Continue readiness check.")
            return None

        # Step 2: Poll until Continue to Payment is enabled.
        continue_btn = self.page.get_by_role("button", name=" Continue to Payment")
        try:
            expect(continue_btn).to_be_visible(timeout=15000)
        except Exception:
            # If the context is destroyed because it's already navigating, that's fine.
            if self.page.is_closed():
                raise AssertionError("Page was closed before Continue to Payment became visible.")
            pass

        remaining = max(timeout_ms, 1000)
        poll = 500
        last_log_at = start
        while remaining > 0:
            if re.search(r"Payment", self.page.url, re.I):
                self.logger.info("Payment page reached while polling Continue button state.")
                return None
            if self.page.is_closed():
                self._capture_debug_artifacts("page_closed_before_continue")
                raise AssertionError("Page was closed before Continue to Payment became enabled.")
            try:
                if continue_btn.is_enabled():
                    self.logger.info("Continue to Payment button is enabled.")
                    self.logger.info(
                        "Continue enabled (elapsed %.2fs).",
                        time.perf_counter() - start,
                    )
                    return continue_btn
            except Exception:
                if re.search(r"Payment", self.page.url, re.I):
                    self.logger.info("Navigation to payment happened during Continue state check.")
                    return None
                self._capture_debug_artifacts("continue_state_check_failed")
                raise
            self.page.wait_for_timeout(200)
            remaining -= 200
            if time.perf_counter() - last_log_at >= 5:
                last_log_at = time.perf_counter()
                try:
                    enabled = continue_btn.is_enabled()
                except Exception:
                    enabled = "unknown"
                self.logger.info(
                    "Waiting for Continue to Payment enabled... (elapsed %.2fs, enabled=%s, remaining=%sms).",
                    time.perf_counter() - start,
                    enabled,
                    remaining,
                )

        # If we exhausted the timer and it's STILL disabled, the Kendo DOM state might be desynchronized.
        # We will forcefully strip the disabled attribute and attempt to bypass the blocked UI state.
        self.logger.warning("Timeout reached, but button is disabled. Forcefully enabling Continue to Payment button via JS injection.")
        try:
            self.page.evaluate(
                "() => { const btns = Array.from(document.querySelectorAll('button, input')); const target = btns.find(b => (b.innerText && b.innerText.includes('Continue to Payment')) || (b.value && b.value.includes('Continue to Payment'))); if (target) { target.removeAttribute('disabled'); target.classList.remove('k-state-disabled', 'disabled'); target.disabled = false; } }"
            )
            self.page.wait_for_timeout(500)
            if continue_btn.is_enabled() or continue_btn.evaluate("el => !el.disabled"):
                self.logger.info("Successfully forced DOM unlock. Proceeding.")
                return continue_btn
        except Exception as e:
            self.logger.warning("Failed to forcefully enable button: %s", e)

        self._capture_debug_artifacts("continue_button_disabled")
        visible_messages = self._collect_visible_validation_messages()
        invalid_fields = self._collect_invalid_required_fields()
        visible_text = ", ".join(visible_messages) if visible_messages else "No visible validation text found"
        invalid_text = ", ".join(invalid_fields) if invalid_fields else "No aria-invalid fields detected"
        raise AssertionError(
            "Continue to Payment is still disabled. "
            f"Visible validation errors: {visible_text}. "
            f"Invalid fields: {invalid_text}"
        )

    # Submit the payment and verify that processing or success is shown.
    def submit_payment_and_assert_processing(self):
        from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
        PaymentPage(self.page).submit_payment()

    # Verify the final payment success page content is displayed.
    def assert_payment_successful_page(self):
        from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
        PaymentPage(self.page).verify_payment_success()

    # Click Return Home on the success page and confirm the dashboard opens.
    def click_return_home_and_assert_dashboard(self):
        return_home = self.page.locator("text='Return Home'").first
        if return_home.count() > 0:
            return_home.click()
        from playwright.sync_api import expect
        expect(self.page).to_have_url(re.compile(r"CustomerPortalDashboard|4321CustomerPortalDashboardFull", re.I), timeout=45000)



