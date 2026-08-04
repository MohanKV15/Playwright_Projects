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
        self.modal_back_button = page.get_by_label("Link Permit").get_by_role("button", name=" Back").or_(
            page.locator(".k-window:visible button:has-text('Back'), [role='dialog']:visible button:has-text('Back')")
        ).first

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

    def fill_standard_location_fields(self, milepost_value: float = 0.0) -> None:
        """Fills Route, Suffix, Direction, and Milepost for standard permit location sections."""
        logger.info("Filling standard location fields.")
        self._wait_for_loader()
        location_div = self.page.locator("#ApplicationLocationInfoDiv")

        for trigger_text in ["--Select Route--", "--Select Suffix--", "--Select Direction--"]:
            trigger = location_div.get_by_text(trigger_text).first
            try:
                if trigger.is_visible():
                    self.select_first_dropdown_option(trigger)
                    self.page.wait_for_timeout(500)
                    self._wait_for_loader()
            except Exception as e:
                logger.warning(f"Location dropdown note ({trigger_text}): {e}")

        try:
            self._set_kendo_numeric_value("milepost", milepost_value)
        except Exception:
            try:
                spin = self.page.get_by_role("spinbutton", name=re.compile(r"Milepost Start", re.I)).first
                if spin.is_visible():
                    spin.click(force=True)
                    spin.fill(str(milepost_value))
                    spin.press("Enter")
            except Exception as e:
                logger.warning(f"Milepost fill note: {e}")

    def verify_link_modals(self) -> None:
        """Verifies link modals (Link Permits, Link To LONI, Link To Pre-App)."""
        logger.info("Verifying modal links.")
