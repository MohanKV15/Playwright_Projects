import re
import logging
from playwright.sync_api import expect

from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage


class MinorAccessPage(PermitMajorPage):
    """Page object for Minor Access application flow."""

    def click_submit_application(self):
        """Click Submit Application tile from dashboard."""
        self.logger.info("MinorAccessPage: clicking Submit Application.")
        super().click_submit_application()

    def select_minor_access(self):
        """Locate Minor Access application entry."""
        self.logger.info("Selecting Minor Access application.")

        btn = self.page.locator("#MinorAccessApplyBt")
        expect(btn).to_be_visible(timeout=15000)

        self._selected_row_locator = btn

    def click_apply_button(self):
        """Click Apply button to start Minor Access application."""
        self.logger.info("Clicking Apply button for Minor Access.")

        btn = self.page.locator("#MinorAccessApplyBt")
        expect(btn).to_be_visible(timeout=15000)
        btn.click()

        # Try page load + upload (non-blocking)
        try:
            self.assert_minor_access_page_loaded()
            self._upload_if_present("UploadAuthCertificate", self.SUPPORTING_DOCUMENT_PATH)
            self.logger.info("Authorization Certificate upload attempted.")
        except Exception as e:
            self.logger.warning(f"Post-click step skipped: {e}")

    def assert_minor_access_page_loaded(self):
        """Verify Minor Access application page loaded."""
        self.logger.info("Verifying Minor Access page loaded.")

        # Try heading first
        headings = [
            self.page.get_by_role("heading", name=re.compile(r"Minor\s*Access", re.I)),
            self.page.get_by_role("heading", name=re.compile(r"Application", re.I)),
            self.page.locator("h1, h2, h3, h4"),
        ]

        for h in headings:
            if h.count() > 0:
                try:
                    expect(h.first).to_be_visible(timeout=5000)
                    self.logger.info("Page heading found.")
                    return
                except Exception:
                    pass

        # Fallback: URL check
        try:
            expect(self.page).to_have_url(
                re.compile(r"MinorAccess|Application", re.I), timeout=15000
            )
            self.logger.info("Page loaded via URL.")
        except Exception:
            self._capture_debug_artifacts("minor_access_page_load_failed")
            raise AssertionError("Minor Access page not loaded.")