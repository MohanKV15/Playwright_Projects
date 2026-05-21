import re
import logging
from datetime import datetime
from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage


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
        # Open calendar
        self.page.get_by_role("button", name="select").click()

        day = str(datetime.now().day)

        self.page.locator(".k-calendar td:not(.k-other-month)") \
        .get_by_role("link", name=day, exact=True).click()

        # Continue remaining fields
 
        self.page.get_by_role("textbox", name="Attached Utility Compan").fill("testing purpose")
        self.page.get_by_role("textbox", name="Attached Appurtenance").fill("testing purpose")

    def upload_erection_pole_attachments(self):
        """Upload required file and complete final required acknowledgements."""
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)
