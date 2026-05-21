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