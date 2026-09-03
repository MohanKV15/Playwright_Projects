import re
import logging
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage


class HighwayOccupancyPage(PermitMajorPage):
    """Page Object for Highway Occupancy (MT-120A) permit application flow."""

    APPLY_BUTTON = "#btnSubmit7"

    def __init__(self, page, script_name: str = "test_highway_occupancy"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    def select_highway_occupancy(self):
        """Locate the Highway Occupancy entry on the applications list."""
        locator = self.page.get_by_text(re.compile(r"Highway\s*Occupancy", re.I)).first
        locator.wait_for(state="visible", timeout=15000)
        self._selected_row_locator = locator

    def click_apply_button(self):
        """Click Apply without waiting for networkidle (reduces flakiness)."""
        btn = self.page.locator(self.APPLY_BUTTON)
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        # Navigation/ready state is asserted by `assert_highway_occupancy_page_loaded`.

    def assert_highway_occupancy_page_loaded(self):
        """Verify form page loaded."""
        self.page.wait_for_url(
            re.compile(r"HighwayOccupancy", re.I),
            timeout=30000
        )

    def upload_street_attachments(self):
        """Upload attachments."""
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)

    def fill_highway_occupancy_permit_information(self):
        """Fill all permit fields."""
        self._fill_type_dropdown()
        self._fill_location_reference_field()
        self._fill_description_field()

    def fill_permit_information(self):
        """Alias for tests."""
        self.fill_highway_occupancy_permit_information()

    def _fill_type_dropdown(self):
        """Select dropdown option."""
        dropdown = self.page.locator("#PermitInfoPvMainDiv").get_by_text("--Select Type--")
        dropdown.wait_for(state="visible", timeout=10000)
        dropdown.click()

        option = self.page.get_by_role("option", name="Automatic traffic counting")
        option.wait_for(state="visible", timeout=10000)
        option.click()

    def _fill_location_reference_field(self):
        """Fill location field."""
        field = self.page.get_by_role(
            "textbox",
            name=re.compile("Location in Reference", re.I)
        )
        field.wait_for(state="visible", timeout=10000)
        field.fill("testing purpose")

    def _fill_description_field(self):
        """Fill description field."""
        field = self.page.get_by_role(
            "textbox",
            name=re.compile("installation", re.I)
        )
        field.wait_for(state="visible", timeout=10000)
        field.fill("testing purpose")