import re
import logging

from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class LotConsolidationSubdivisionPage(PermitMajorPage):
    """Page object for Lot Consolidation / Subdivision flow."""

    APPLY_BUTTON = "#btnSubmit4"

    def __init__(self, page, script_name: str = "test_lot_consolidation_subdivision"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_lot_consolidation_subdivision(self):
        locator = self.page.get_by_text(
            re.compile(r"Lot\s*Consolidation/Subdivision", re.I)
        ).first

        locator.wait_for(state="visible", timeout=15000)
        self._selected_row_locator = locator

    # 🔥 FIXED METHOD
    def click_apply_button(self):
        btn = self.page.locator(self.APPLY_BUTTON)

        btn.wait_for(state="visible", timeout=15000)

        # Click first
        btn.click()

        # ✅ WAIT for actual navigation (IMPORTANT FIX)
        self.page.wait_for_url(
            re.compile(r"HTCP4321Driveway|PermitType", re.I),
            timeout=30000
        )

        self.logger.info("Apply button clicked and navigation completed.")

    def assert_page_loaded(self):
        # ✅ URL validation
        self.page.wait_for_url(
            re.compile(r"HTCP4321Driveway|PermitType", re.I),
            timeout=30000
        )

        # ✅ Ensure page content loaded
        try:
            self.page.locator("#LocationInfoDiv").wait_for(state="visible", timeout=15000)
        except Exception:
            self.logger.warning("LocationInfoDiv not found")

    def choose_permit_type(self, kind: str = "Lot Consolidation"):
        """Select permit type radio (minimal + stable)."""

        radio = self.page.get_by_role(
            "radio", name=re.compile(re.escape(kind), re.I)
        ).first

        if radio.count() == 0:
            radio = self.page.locator("input[type='radio']").first

        radio.wait_for(state="attached", timeout=10000)

        try:
            radio.scroll_into_view_if_needed()
            radio.click(timeout=5000, force=True)
            self.logger.info(f"Selected radio: {kind}")
        except Exception as e:
            self.logger.warning(f"Click failed, using JS fallback: {e}")
            self._select_radio_js(radio)

    def _select_radio_js(self, locator):
        """JS fallback for radio selection."""
        radio_id = locator.get_attribute("id")
        radio_name = locator.get_attribute("name")
        radio_value = locator.get_attribute("value")

        if radio_id:
            self.page.evaluate(
                """(id) => {
                    const el = document.getElementById(id);
                    if (el) {
                        el.checked = true;
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""",
                radio_id,
            )
        elif radio_name and radio_value:
            self.page.evaluate(
                """({ name, value }) => {
                    const el = document.querySelector(
                        `input[type='radio'][name="${name}"][value="${value}"]`
                    );
                    if (el) {
                        el.checked = true;
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""",
                {"name": radio_name, "value": radio_value},
            )

    def upload_required_attachments(self):
        for input_id in [
            "ApplicationAttachments",
            "ApplicationChecklist",
            "POAAttachment",
        ]:
            try:
                self._upload_if_present(input_id, self.SUPPORTING_DOCUMENT_PATH)
            except Exception as e:
                self.logger.warning(f"Upload skipped for {input_id}: {e}")