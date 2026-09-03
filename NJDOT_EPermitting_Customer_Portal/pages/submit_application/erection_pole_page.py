import re
import logging
from datetime import datetime
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class ErectionPolePage(PermitMajorPage):
    """Page Object for Permit Information - Erection of Pole (MT33A)"""

    APPLY_BUTTON = "#btnSubmit6"
    PERMIT_SUBTYPE = "HPMPST12"

    def __init__(self, page, script_name: str = "test_erection_pole"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_erection_pole(self):
        "ensure button is visible"
        self.page.locator(self.APPLY_BUTTON).wait_for(state="visible", timeout=15000)

    def click_apply_button(self):
        """Click Apply button.""" 
        btn = self.page.locator(self.APPLY_BUTTON)
        btn.wait_for(state="visible", timeout=15000)
        btn.click() 

    def assert_erection_pole_page_loaded(self):  
        """Verify correct page using subtype."""  
        self.page.wait_for_url(
            re.compile(r"HighwayOccupancy", re.I),
            timeout=30000
        )

    def fill_additional_details(self):
        self.page.get_by_role("textbox", name="Location in Reference to").fill("testing purpose")
        self.page.get_by_role("textbox", name="Voltage not to exceed").fill("123")

    def select_today_date(self):
        from datetime import timedelta
        tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        
        self._set_kendo_date_value("EOPWorktobecompletedBy", tomorrow_str)
 
        self.page.get_by_role("textbox", name="Attached Utility Compan").fill("testing purpose")
        self.page.get_by_role("textbox", name="Attached Appurtenance").fill("testing purpose")

    def _set_kendo_date_value(self, input_id: str, value: str):
        """Set a Kendo DatePicker value directly using JavaScript to avoid flaky calendar UI clicks."""
        self.logger.info(f"Setting Kendo DatePicker {input_id} to {value}")
        input_locator = self.page.locator(f"#{input_id}")
        input_locator.wait_for(state="attached", timeout=15000)
        self.page.evaluate(
            """
            ({ id, value }) => {
                const el = document.getElementById(id);
                if (!el) return;
                if (window.jQuery) {
                    const dp = window.jQuery(el).data('kendoDatePicker');
                    if (dp) {
                        dp.value(value);
                        dp.trigger('change');
                        return;
                    }
                }
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """,
            {"id": input_id, "value": value},
        )

    def upload_erection_pole_attachments(self):
        """Upload required file and complete final required acknowledgements."""
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)
