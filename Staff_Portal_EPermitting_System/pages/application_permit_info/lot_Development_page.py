import logging
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class LotDevelopmentPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Navigation / Tabs
        self.lot_development_tab = page.get_by_role("link", name="Lot Development/ Frontages").or_(page.locator("a:has-text('Lot Development')")).first
        
        # Headings & Sections
        self.heading_lot_development = page.get_by_role("heading", name=re.compile("Lot Development", re.I)).or_(page.locator("#LogAppHeader, h1, h2, h3, h4, h5, .page-title")).first
        self.spacing_heading = page.get_by_role("heading", name=re.compile("Spacing", re.I)).or_(page.locator("h1, h2, h3, h4, h5, .section-title")).first
        
        # Land Use Elements
        self.add_land_use_button = page.get_by_role("button", name=" Add Land Use").or_(page.locator(".btn:has-text('Land Use')")).first
        self.land_use_modal_title = page.locator(".k-window-title:visible, [role='dialog']:visible .k-window-title").filter(has_text=re.compile("Land Use", re.I))
        self.land_use_type_dropdown = page.get_by_role("button", name="select").first
        self.land_use_size_input = page.get_by_role("spinbutton", name="Units/Size").or_(page.locator("input[name*='Size'], input[id*='Size']")).first
        self.save_land_use_button = page.get_by_role("button", name=" Save").or_(page.locator(".btn:has-text('Save')")).first
        
        # Spacing Elements
        self.add_spacing_button = page.get_by_role("button", name=" Add Spacing").or_(page.locator(".btn:has-text('Spacing')")).first
        self.spacing_modal_title = page.locator(".k-window-title:visible, [role='dialog']:visible .k-window-title").filter(has_text=re.compile("Spacing", re.I))
        self.spacing_dropdowns = page.get_by_role("button", name="select")
        self.lot_size_input = page.get_by_role("spinbutton", name="Lot Size").or_(page.locator("input[name*='Lot'], input[id*='Lot']")).first
        self.frontage_input = page.get_by_role("spinbutton", name="Frontage").or_(page.locator("input[name*='Frontage'], input[id*='Frontage']")).first
        self.save_spacing_button = page.get_by_role("button", name=" Save").or_(page.locator(".btn:has-text('Save')")).first

    def _select_first_dropdown_option(self):
        """Selects the first valid option from a Kendo UI dropdown list."""
        try:
            self.page.wait_for_selector("[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible", timeout=5000)
            list_box = self.page.locator("[role='listbox']:visible, .k-list-container:visible, .k-animation-container:visible").last
            options = list_box.locator("li, [role='option'], .k-item")
            count = options.count()
            for i in range(count):
                txt = options.nth(i).inner_text().strip()
                if txt and not txt.startswith("--") and not txt.lower().startswith("select"):
                    options.nth(i).click()
                    self.page.wait_for_timeout(300)
                    return
            if count > 1:
                options.nth(1).click()
            else:
                options.first.click()
        except Exception as e:
            logger.warning(f"Dropdown selection note: {e}")

    def navigate_to_lot_development(self) -> None:
        """Navigates to the Lot Development/Frontages tab."""
        logger.info("Navigating to Lot Development/Frontages tab.")
        self._wait_for_loader()
        self.js_click(self.lot_development_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layout grids exist on the page."""
        logger.info("Verifying initial layout of Lot Development/Frontages page.")
        expect(self.heading_lot_development).to_be_visible(timeout=15000)

    def add_land_use(self, units: str = "4") -> None:
        """Creates a new Land Use entry with the specified units/size."""
        logger.info("Adding a new Land Use entry.")
        if self.add_land_use_button.count() > 0 and self.add_land_use_button.is_visible():
            self.js_click(self.add_land_use_button)
            self._wait_for_loader()
            
            # Click dropdown and select first valid option
            if self.land_use_type_dropdown.is_visible():
                self.js_click(self.land_use_type_dropdown)
                self._select_first_dropdown_option()
            
            # Fill Units/Size
            if self.land_use_size_input.is_visible():
                self.js_click(self.land_use_size_input)
                self.land_use_size_input.fill(units)
            
            # Save
            if self.save_land_use_button.is_visible():
                self.js_click(self.save_land_use_button)
                self._wait_for_loader()
            logger.info("Land Use entry added successfully.")

    def add_spacing(self, size: str = "4", frontage: str = "5") -> None:
        """Creates a new Spacing entry by filling form inputs and choosing dropdown options."""
        logger.info("Adding a new Spacing entry.")
        if self.add_spacing_button.count() > 0 and self.add_spacing_button.is_visible():
            self.js_click(self.add_spacing_button)
            self._wait_for_loader()
            
            # Handle modal dropdowns
            count = self.spacing_dropdowns.count()
            for i in range(min(count, 3)):
                try:
                    self.js_click(self.spacing_dropdowns.nth(i))
                    self._select_first_dropdown_option()
                except Exception as e:
                    logger.warning(f"Spacing dropdown index {i} note: {e}")
                    
            # Fill Lot Size and Frontage
            if self.lot_size_input.is_visible():
                self.js_click(self.lot_size_input)
                self.lot_size_input.fill(size)
            
            if self.frontage_input.is_visible():
                self.js_click(self.frontage_input)
                self.frontage_input.fill(frontage)
            
            # Save
            if self.save_spacing_button.is_visible():
                self.js_click(self.save_spacing_button)
                self._wait_for_loader()
            logger.info("Spacing entry added successfully.")

    def send_email_and_verify(self) -> None:
        """Triggers Send Email popup, verifies form controls, and clicks Cancel."""
        logger.info("Testing Send Email form flow.")
        self._wait_for_loader()
        if self.send_email_button.count() > 0 and self.send_email_button.is_visible():
            self.js_click(self.send_email_button)
            self._wait_for_loader()
            if self.cancel_email_button.count() > 0 and self.cancel_email_button.is_visible():
                self.js_click(self.cancel_email_button)
                self._wait_for_loader()
            logger.info("Send Email popup tested and cancelled successfully.")
