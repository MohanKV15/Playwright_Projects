import re
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class StreetIntersectionPage(PermitMajorPage):
    """Page object for Street Intersection application flow."""

    APPLY_BUTTON = "#btnSubmit3"

    def select_street_intersection(self):
        """Select Street Intersection application."""
        self.logger.info("Selecting Street Intersection application.")

        locator = self.page.get_by_text(
            re.compile(r"Street\s*Intersection", re.I)
        ).first

        locator.wait_for(state="visible", timeout=15000)
        self._selected_row_locator = locator

    def click_apply_button(self):
        """Click Apply button."""
        self.logger.info("Clicking Apply for Street Intersection.")

        btn = self.page.locator(self.APPLY_BUTTON)
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        # Avoid waiting for `networkidle` (often never reached). The caller asserts
        # the final page via `assert_street_intersection_page_loaded()`.

    def assert_street_intersection_page_loaded(self):
        """Verify Street Intersection page loaded."""
        self.page.wait_for_url(
            re.compile(r"StreetIntersection|Application", re.I),
            timeout=30000
        )

    def upload_street_attachments(self):
        """Upload required attachments."""
        for attachment in ["AdditionalAttachments", "HAndHChecklist"]:
            self._upload_if_present(attachment, self.SUPPORTING_DOCUMENT_PATH)