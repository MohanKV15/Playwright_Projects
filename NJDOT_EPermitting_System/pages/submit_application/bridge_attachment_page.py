import re
import logging
from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage


class BridgeAttachmentPage(PermitMajorPage):
    """Page Object for Bridge Attachment (MT-105A) permit flow."""

    APPLY_BUTTON = "#btnSubmit8"
    PERMIT_SUBTYPE = "HPMPST14"

    def __init__(self, page, script_name: str = None):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_bridge_attachment(self):
        """Ensure button is visible."""
        self.page.locator(self.APPLY_BUTTON).wait_for(state="visible", timeout=15000)

    def click_apply_button(self):
        """Click Apply."""
        self.page.locator(self.APPLY_BUTTON).click()

    def assert_bridge_attachment_page_loaded(self):
        """Verify correct page using subtype."""
        self.page.wait_for_url(re.compile(r"HighwayOccupancyFV", re.I), timeout=30000)

        self.page.wait_for_function(
            "(subtype) => new URL(window.location.href).searchParams.get('PermitSubType') === subtype",
            arg=self.PERMIT_SUBTYPE,
            timeout=30000,
        )

        self.page.get_by_role(
            "textbox", name=re.compile("Lot Owner Company Name", re.I)
        ).wait_for(state="visible", timeout=30000)

    def fill_permit_information(self):
        """Fill required fields."""
        self.page.get_by_role(
            "textbox", name=re.compile("State location exactly", re.I)
        ).fill("testing purpose")

        self.page.get_by_role(
            "textbox", name=re.compile("Purpose of attachment", re.I)
        ).fill("testing purpose")

    def upload_bridge_attachments(self):
        """Upload file."""
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)
        self._upload_if_present("HAndHChecklist", self.SUPPORTING_DOCUMENT_PATH)

    # def fill_acknowledgement(self):
    #     """Handle acknowledgement."""

    #     ack_checkbox = self.page.locator("#Aknwldgmnt")

    #     if ack_checkbox.count() > 0:
    #         try:
    #             ack_checkbox.first.check(timeout=5000)
    #         except Exception:
    #             self.logger.warning("Checkbox click failed, using JS fallback")

    #             self.page.evaluate(
    #                 """
    #                 () => {
    #                     const ack = document.getElementById('Aknwldgmnt');
    #                     if (!ack) return;
    #                     ack.checked = true;
    #                     ack.dispatchEvent(new Event('change', { bubbles: true }));

    #                     const btn = document.getElementById('btnSubmit');
    #                     if (btn) btn.removeAttribute('disabled');
    #                 }
    #                 """
    #             )

    #     # Optional name field
    #     name = self.page.locator("input[type='text']").last
    #     if name.count() > 0:
    #         try:
    #             name.first.fill("Test User")
    #         except Exception:
    #             self.logger.warning("Name field not filled")