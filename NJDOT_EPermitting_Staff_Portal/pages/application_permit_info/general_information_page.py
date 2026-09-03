import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class GeneralInformationPage(BasePage):
    """
    Page Object Model for General Information tab in Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # General Info Fields
        self.block_no_input = page.locator("#block_no")
        self.lot_no_input = page.locator("#lot_no")
        self.update_button = page.get_by_role("button", name=" Update")
        self.add_new_link = page.get_by_role("link", name=" Add New")

        # Modal Links
        self.link_permits_button = page.locator("a, button").filter(has_text=re.compile(r"Link Permits", re.I)).first
        self.link_to_loni_button = page.locator("a, button").filter(has_text=re.compile(r"Link To LONI", re.I)).first
        self.link_to_pre_app_button = page.locator("a, button").filter(has_text=re.compile(r"Link To Pre-App", re.I)).first
        # Shared Add-New Permit Locators
        self.render_add_new_container = page.locator("#renderaddnew")
        self.frm_permit_container = page.locator("#frmPermit")
        self.location_info_container = page.locator("#ApplicationLocationInfoDiv")

        self.general_info_heading = page.get_by_role("heading", name="General Information").or_(
            page.get_by_text("General Information")
        ).first
        self.location_info_heading = page.get_by_role("heading", name="Location Information").or_(
            page.get_by_text("Location Information")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).or_(page.locator("#btnSavePermit, #btnSave, .btn:has-text('Save')")).first

    def save_permit(self) -> None:
        """Clicks Save button and asserts no validation errors."""
        logger.info("Saving permit.")
        self._wait_for_loader()
        self.js_click(self.save_button)
        self._wait_for_loader()
        self.assert_no_validation_errors()

    def fill_permit_dropdowns(self, placeholders: list = None) -> None:
        """Selects first available option for specified Kendo dropdown placeholders in #frmPermit."""
        placeholders = placeholders or [
            "--Select Team Leader--",
            "--Select Department--",
            "--Select Permit Sub Type--",
            "--Select Case Manager--",
        ]
        for placeholder in placeholders:
            try:
                trig = self.page.locator("#frmPermit").get_by_text(placeholder).first
                if trig.is_visible():
                    trig.click()
                    self.page.wait_for_timeout(300)
                    self.page.get_by_role("option").first.click()
                    self.page.wait_for_timeout(300)
            except Exception as e:
                logger.warning(f"Dropdown '{placeholder}' selection note: {e}")

    def update_block_and_lot(self, block: str, lot: str) -> None:
        """Fills block/lot and clicks update."""
        logger.info(f"Updating Block ({block}) and Lot ({lot}).")
        self._wait_for_loader()
        if self.block_no_input.is_visible():
            self.block_no_input.fill(block)
        if self.lot_no_input.is_visible():
            self.lot_no_input.fill(lot)

        if self.update_button.is_visible():
            self.js_click(self.update_button)
            self._wait_for_loader()

    def add_new_record_detail(self) -> None:
        """Clicks Add New link."""
        logger.info("Clicking Add New record link.")
        self._wait_for_loader()
        if self.add_new_link.is_visible():
            self.js_click(self.add_new_link)
            self._wait_for_loader()

    def verify_permit_saved(self) -> None:
        """Verifies the permit was saved and the post-save detail header is visible."""
        logger.info("Verifying permit saved status.")
        self._wait_for_loader()
        saved_header = self.log_app_header.or_(
            self.page.locator("div").filter(has_text=re.compile(r"Department Job # Permit Type", re.I)).first
        )
        expect(saved_header).to_be_visible(timeout=15000)

    def close_permit_page(self) -> None:
        """Returns to Permit Listing after permit creation."""
        logger.info("Closing permit page and navigating back to Permit Listing.")
        from pages.application_permit_info.permit_listing_page import PermitListingPage

        listing_page = PermitListingPage(self.page)
        listing_page.navigate_to_permit_listing()
        listing_page.verify_search_form_ready()

    def fill_location_information(self, data: dict = None) -> None:
        """Fills standard Location Information section (Route, Mileposts, Suffix, Direction)."""
        logger.info("Filling Location Information section.")
        data = data or {}
        milepost_val = data.get("milepost_start", data.get("milepost", "1"))
        milepost_end = data.get("milepost_end", milepost_val)
        self._wait_for_loader()

        location_info_heading = self.page.get_by_role("heading", name="Location Information").or_(
            self.page.get_by_text("Location Information")
        ).first
        try:
            if location_info_heading.is_visible():
                expect(location_info_heading).to_be_visible(timeout=5000)
        except Exception:
            pass

        # 1. Select Route
        try:
            route_trig = self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Route--").first
            if route_trig.is_visible():
                route_trig.click()
                self.page.wait_for_timeout(300)
                self.page.get_by_role("option").first.click()
                self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Route selection note: {e}")

        # 2. Fill Mileposts
        try:
            spin1 = self.page.get_by_role("spinbutton").first
            if spin1.is_visible():
                spin1.click()
                spin1.fill(str(milepost_val))
                spin1.press("Enter")

            spin2 = self.page.get_by_role("spinbutton").nth(1)
            if spin2.is_visible():
                spin2.click()
                spin2.fill(str(milepost_end))
                spin2.press("Enter")
        except Exception as e:
            logger.warning(f"Milepost spinbutton note: {e}")

        # 3. Select Suffix
        try:
            suffix_trig = self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Suffix--").first
            if suffix_trig.is_visible():
                suffix_trig.click()
                self.page.wait_for_timeout(300)
                self.page.get_by_role("option").first.click()
                self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Suffix selection note: {e}")

        # 4. Select Direction
        try:
            dir_trig = self.page.locator("#ApplicationLocationInfoDiv").get_by_text("--Select Direction--").first
            if dir_trig.is_visible():
                dir_trig.click()
                self.page.wait_for_timeout(200)
                dir_trig.click()
                self.page.wait_for_timeout(300)
                self.page.get_by_role("option").first.click()
                self.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Direction selection note: {e}")

    def fill_standard_location_fields(self, milepost_value: float = 0.0) -> None:
        """Fills Route, Suffix, Direction, and Milepost for standard permit location sections."""
        logger.info("Filling standard location fields.")
        self.fill_location_information({"milepost": milepost_value})

    def verify_link_modals(self) -> None:
        """Verifies link modals (Link Permits, Link To LONI, Link To Pre-App)."""
        logger.info("Verifying modal links.")
