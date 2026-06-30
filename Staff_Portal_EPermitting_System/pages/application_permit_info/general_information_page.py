from pages.base_page import BasePage
from playwright.sync_api import expect

class GeneralInformationPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # General Info Fields
        self.block_no_input = page.locator("#block_no")
        self.lot_no_input = page.locator("#lot_no")
        self.update_button = page.get_by_role("button", name=" Update")
        self.add_new_link = page.get_by_role("link", name=" Add New")
        
        # Navigation / Link Buttons
        import re
        self.link_permits_button = page.locator("a, button").filter(has_text=re.compile(r"Link Permits", re.I)).first
        self.link_to_loni_button = page.locator("a, button").filter(has_text=re.compile(r"Link To LONI", re.I)).first
        self.link_to_pre_app_button = page.locator("a, button").filter(has_text=re.compile(r"Link To Pre-App", re.I)).first
        
        # Modal Selectors
        self.modal_back_button = page.get_by_label("Link Permit").get_by_role("button", name=" Back")



    def update_block_and_lot(self, block: str, lot: str):
        """Fills block/lot and clicks update."""
        self._wait_for_loader()
        
        # Scroll to ensure visibility on long forms
        self.scroll_to_locator(self.block_no_input)
        
        self.block_no_input.fill(block)
        self.lot_no_input.click() # Click pattern from codegen
        self.lot_no_input.fill(lot)
        
        self.scroll_to_locator(self.update_button)
        self.update_button.click()
        self._wait_for_loader()

    def add_new_record_detail(self):
        """Clicks 'Add New' link."""
        self._wait_for_loader()
        self.scroll_to_locator(self.add_new_link)
        self.add_new_link.click()
        self._wait_for_loader()

    def verify_link_modals(self):
        """Verifies the link modals open and close correctly."""
        self._wait_for_loader()
        
        # Link Permits
        self.scroll_to_locator(self.link_permits_button)
        self.link_permits_button.click()
        expect(self.page.get_by_label("Link Permit")).to_be_visible()
        self.modal_back_button.click()
        
        # Link to LONI
        self.scroll_to_locator(self.link_to_loni_button)
        self.link_to_loni_button.click()
        expect(self.page.get_by_label("Link Permit")).to_be_visible()
        self.modal_back_button.click()
        
        # Link to Pre-App
        self.scroll_to_locator(self.link_to_pre_app_button)
        self.link_to_pre_app_button.click()
        expect(self.page.get_by_label("Link Permit")).to_be_visible()
        self.modal_back_button.click()

    def verify_data_matching(self, expected_data: dict):
        """
        Verifies that the data on this page matches the record clicked in the listing.
        Example mapping (adjust based on actual field IDs):
        """
        # Note: We need to find the correct selectors for static labels on this page.
        # For now, let's assume we are looking for the application number in the header or a specific label.
        # This is a placeholder for professional verification.
        pass
