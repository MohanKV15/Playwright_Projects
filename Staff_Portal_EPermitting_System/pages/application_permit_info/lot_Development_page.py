import logging
import datetime
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage
from faker import Faker

logger = logging.getLogger(__name__)

class LotDevelopmentPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation / Tabs
        self.lot_development_tab = page.get_by_role("link", name="Lot Development/Frontages")
        
        # Heading & Section Container Selectors
        self.heading_lot_development = page.get_by_role("heading", name="Lot/Development/Frontage")
        self.spacing_heading = page.get_by_role("heading", name="Spacing")
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        
        # Add New Land Use Selectors
        self.add_land_use_button = page.locator("#btnlandusenewentry")
        self.land_use_modal_title = page.locator("div").filter(has_text="Add/Edit New Land Use")
        self.land_use_type_dropdown = page.locator("#landusediv").get_by_text("--Select Land Use Type--")
        self.land_use_size_input = page.get_by_role("dialog", name="Add/Edit New Land Use").get_by_role("spinbutton")
        self.save_land_use_button = page.locator("#btnsavelanduse")
        
        # Add/Edit Spacing Selectors
        self.add_spacing_button = page.locator("#btnspacingentry")
        self.spacing_modal_title = page.locator("#DivForNewEntryWindow_wnd_title")
        self.lot_size_input = page.locator("#lot_size")
        self.lot_frontage_input = page.locator("#lot_frontage")
        self.save_spacing_button = page.locator("#btnspacingsave")
        




    def navigate_to_lot_development(self) -> None:
        """Transitions to the Lot Development / Frontages tab."""
        logger.info("Navigating to Lot Development/Frontages tab.")
        self._wait_for_loader()
        self.js_click(self.lot_development_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layout grids exist on the page."""
        logger.info("Verifying initial layout of Lot Development/Frontages page.")
        expect(self.heading_lot_development).to_be_visible(timeout=15000)
        expect(self.page.locator(".col-md-8")).to_be_visible(timeout=10000)
        expect(self.page.locator("#partial-form > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)

    def add_land_use(self, units: str = "4") -> None:
        """Creates a new Land Use entry with the specified units/size."""
        logger.info("Adding a new Land Use entry.")
        self.js_click(self.add_land_use_button)
        expect(self.land_use_modal_title.first).to_be_visible(timeout=10000)
        
        # Click dropdown and select first valid option
        self.js_click(self.land_use_type_dropdown)
        self._select_first_dropdown_option()
        
        # Fill Units/Size
        self.js_click(self.land_use_size_input)
        self.land_use_size_input.fill(units)
        
        # Save
        self.js_click(self.save_land_use_button)
        self._wait_for_loader()
        expect(self.page.locator("#partial-form > .form-wrapper > .row > .col-md-12").first).to_be_visible(timeout=10000)
        logger.info("Land Use entry added successfully.")

    def add_spacing(self, size: str = "4", frontage: str = "5") -> None:
        """Creates a new Spacing entry by filling form inputs and choosing dropdown options."""
        logger.info("Adding a new Spacing entry.")
        expect(self.spacing_heading).to_be_visible(timeout=10000)
        self.js_click(self.add_spacing_button)
        expect(self.spacing_modal_title).to_be_visible(timeout=10000)
        
        # Fill Lot Size & Lot Frontage using focused inputs
        self.fill_kendo_numeric("lot_size", size)
        self.fill_kendo_numeric("lot_frontage", frontage)
        
        # Loop through all dropdown widgets inside spacing form and choose the 1st valid option
        dropdowns = self.page.locator("#spacingformdiv span.k-dropdown:visible, #spacingformdiv span[role='listbox']:visible")
        count = dropdowns.count()
        logger.info(f"Found {count} dropdowns inside spacing form container. Cycling selections.")
        for i in range(count):
            self.js_click(dropdowns.nth(i))
            self._select_first_dropdown_option()
            
        # Save spacing
        self.js_click(self.save_spacing_button)
        self._wait_for_loader()
        logger.info("Spacing entry added successfully.")


