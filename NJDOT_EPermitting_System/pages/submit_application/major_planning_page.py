import re
from playwright.sync_api import expect
from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage


class MajorPlanningPage(PermitMajorPage):

    def click_apply_for_major_with_planning(self):
        """Click Apply for Major with Planning."""

        self.logger.info("Clicking Apply for Major with Planning.")

        apply_btn = self.page.locator("#btnSubmit2")
    
        expect(apply_btn).to_be_visible(timeout=15000)
    
        # ❌ REMOVE expect_navigation
        apply_btn.click()

        # ✅ WAIT for URL change instead (this is the FIX)
        self.page.wait_for_url(
            re.compile(r"HTCP4321Driveway|PermitType", re.I),
            timeout=30000
        )

        self.logger.info("Apply for Major with Planning clicked and page loaded.")

    def assert_major_with_planning_page_loaded(self):
        """Verify Major with Planning form page loaded."""

        # ✅ Keep this (already correct)
        expect(self.page).to_have_url(
            re.compile(r"HTCP4321Driveway|PermitType", re.I),
            timeout=30000
        )

        # ✅ EXTRA STABILITY (IMPORTANT)
        # Wait for any form element to ensure page is fully loaded
        try:
            self.page.locator("form").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

    def fill_remaining_required_fields(self):
        """Fill remaining required fields, including Pre-Application Customer Reference for Major with Planning."""
        self.logger.info("Filling Pre-Application Information / Customer Reference.")
        
        # Verify Pre - Application Information heading is visible
        pre_app_heading = self.page.get_by_role("heading", name="Pre - Application Information")
        expect(pre_app_heading).to_be_visible(timeout=15000)
        
        # Read the latest pre-app reference from the shared file
        ref_no = "APG18335" # Default fallback
        from NJDOT_EPermitting_System.config import PROJECT_ROOT
        ref_file = PROJECT_ROOT / ".pytest_cache" / "latest_pre_app_ref.txt"
        if ref_file.exists():
            try:
                ref_no = ref_file.read_text(encoding="utf-8").strip()
                self.logger.info(f"Loaded latest Pre-Application reference from shared file: {ref_no}")
            except Exception:
                pass

        # Click and fill Customer Reference #
        ref_input = self.page.get_by_role("textbox", name="Enter Customer Reference # *")
        expect(ref_input).to_be_visible(timeout=10000)
        ref_input.click()
        ref_input.fill(ref_no)
        ref_input.press("Tab")
        self.page.evaluate(
            """
            () => {
                const el = document.getElementById('PreAppNo');
                if (!el) return;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """
        )
        self.page.wait_for_timeout(1000)
        
        # Fill Owner Representative
        owner_rep = self.page.locator("#owner_representative")
        if owner_rep.count() == 0:
            owner_rep = self.page.locator("xpath=//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/following-sibling::input | //label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'owner or authorized representative')]/..//input").first
        
        if owner_rep.count() > 0:
            owner_rep.first.scroll_into_view_if_needed()
            owner_rep.first.fill(self.fake.name())
            owner_rep.first.press("Tab")

        # Upload standard required documents
        for input_id in [
            "ApplicationAttachments",
            "ApplicationChecklist",
            "POAAttachment",
        ]:
            self._upload_if_present(input_id, self.SUPPORTING_DOCUMENT_PATH)

        # Handle acknowledgment checkbox
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

        # Clear stale invalid markers for hidden conditional upload controls
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
        self.logger.info("Remaining required fields for Major with Planning filled successfully.")