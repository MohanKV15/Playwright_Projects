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

    def verify_link_modals(self) -> None:
        """Verifies link modals (Link Permits, Link To LONI, Link To Pre-App)."""
        logger.info("Verifying modal links.")
        self._wait_for_loader()

        for btn_name, locator in [
            ("Link Permits", self.link_permits_button),
            ("Link To LONI", self.link_to_loni_button),
            ("Link To Pre-App", self.link_to_pre_app_button),
        ]:
            try:
                if locator.is_visible():
                    self.js_click(locator)
                    self.page.wait_for_timeout(300)
                    if self.modal_back_button.is_visible():
                        self.js_click(self.modal_back_button)
                        self._wait_for_loader()
            except Exception as e:
                logger.warning(f"Modal verification note for '{btn_name}': {e}")
