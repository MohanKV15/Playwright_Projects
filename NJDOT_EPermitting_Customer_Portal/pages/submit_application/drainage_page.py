import re
import logging
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class DrainagePage(PermitMajorPage):
    """Page Object for Drainage (MT-39A) permit flow."""

    APPLY_BUTTON = "#btnSubmit5"
    PERMIT_SUBTYPE = "HPMPST13"

    def __init__(self, page, script_name: str = None):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_drainage(self):
        """Ensure button is visible."""
        self.page.locator(self.APPLY_BUTTON).wait_for(state="visible", timeout=15000)

    def click_apply_button(self):
        """Click Apply."""
        btn = self.page.locator(self.APPLY_BUTTON)
        btn.click()
        try:
            self.page.wait_for_load_state("commit", timeout=30000)
        except Exception:
            self.logger.warning("Page load state not reached")

    def assert_drainage_page_loaded(self):
        """Verify correct page using subtype."""
        self.page.wait_for_url(re.compile(r"HighwayOccupancyFV", re.I), timeout=30000)

        self.page.wait_for_function(
            """(subtype) => new URL(window.location.href).searchParams.get("PermitSubType") === subtype""",
            arg=self.PERMIT_SUBTYPE,
            timeout=30000
        )

        self.page.get_by_role(
            "textbox",
            name=re.compile("Lot Owner Company Name", re.I)
        ).wait_for(state="visible", timeout=30000)

    def fill_permit_information(self):
        """Fill required fields."""
        self.page.get_by_role(
            "textbox",
            name=re.compile(r"State location exactly", re.I)
        ).fill(self.fake.street_address())

        self.page.get_by_role(
            "textbox",
            name=re.compile(r"Purpose", re.I)
        ).fill(self.fake.sentence(nb_words=6))



    def upload_drainage_attachments(self):
        """Upload file."""
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)
        self._upload_if_present("HAndHChecklist", self.SUPPORTING_DOCUMENT_PATH)

