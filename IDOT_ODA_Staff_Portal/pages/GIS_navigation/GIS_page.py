import logging
from playwright.sync_api import Page, FrameLocator, expect
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class GISPage(BasePage):
    """
    Page Object Model representing the GIS Navigation and Map Information workflow
    in the IDOT Outdoor Advertising Staff Portal.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Main Page Navigation & Guidance Locators
        self.gis_menu_link = page.locator("a[href*='GISPage']").or_(
            page.get_by_role("link", name="GIS")
        ).first
        self.instruction_text = page.get_by_text("Zoom in on the area where you")
        self.browser_support_container = page.locator("div").filter(
            has_text="Your browser doesn't support"
        ).nth(4)
        self.return_to_application_button = page.get_by_role(
            "button", name="Return to Application"
        ).or_(
            page.locator("a:has-text('Return to Application'), button:has-text('Return to Application')")
        ).first

        # Embedded GIS Iframe Locators
        self.gis_iframe = page.locator("iframe[src*='idgis'], iframe").first
        self.gis_frame: FrameLocator = page.frame_locator("iframe[src*='idgis'], iframe").first

        # Map Viewport & Toolbar Elements inside Iframe
        self.map_content = self.gis_frame.locator("#mapContent")
        self.map_left_pane = self.gis_frame.locator("#leftPane")
        self.location_finder_tool = self.gis_frame.get_by_text("Location Finder").first
        self.measure_tools = self.gis_frame.get_by_text("Measure Tools").first
        self.zoom_in_tool = self.gis_frame.get_by_text("Zoom-in").first
        self.zoom_out_tool = self.gis_frame.get_by_text("Zoom-out").first
        self.pan_tool = self.gis_frame.get_by_text("Pan").first
        self.basemap_tool = self.gis_frame.get_by_text("Basemap").first
        self.visible_map_tiles = self.gis_frame.locator("img:visible")
        self.search_tab = self.gis_frame.get_by_text("Search").first
        self.layers_tab = self.gis_frame.get_by_text("Layers").first

    # -------------------------------------------------------------------------
    # Actions & Navigation
    # -------------------------------------------------------------------------
    def navigate_to_gis(self) -> None:
        """
        Navigates to the GIS Information module by clicking the GIS menu link
        from the staff portal sidebar.
        """
        self.logger.info("Navigating to GIS Information page via sidebar link")
        self._wait_for_loader()
        expect(self.gis_menu_link).to_be_visible(timeout=30000)
        self.gis_menu_link.click(force=True)
        self._wait_for_loader()

    def verify_gis_instructions_displayed(self, timeout_ms: int = 25000) -> None:
        """
        Verifies that the GIS instruction guidance banner is visible:
        'Zoom in on the area where you want your permit to be located...'
        """
        self.logger.info("Verifying GIS instruction text is displayed")
        expect(self.instruction_text).to_be_visible(timeout=timeout_ms)

    def verify_browser_support_container(self, timeout_ms: int = 25000) -> None:
        """
        Verifies the container holding the embedded GIS map frame (matching the
        browser fallback element from codegen or the iframe itself).
        """
        self.logger.info("Verifying browser support container for GIS iframe")
        container = self.browser_support_container.or_(self.gis_iframe).first
        expect(container).to_be_visible(timeout=timeout_ms)

    def wait_for_map_to_display(self, timeout_ms: int = 40000) -> None:
        """
        Waits until the GIS map iframe is rendered and its internal map canvas/tiles
        and toolbar controls are fully visible.
        """
        self.logger.info("Waiting for GIS map iframe and map controls to be displayed")
        expect(self.gis_iframe).to_be_visible(timeout=timeout_ms)

        # Wait for map content container or left pane within iframe
        map_container = self.map_left_pane.or_(self.map_content).first
        expect(map_container).to_be_visible(timeout=timeout_ms)

        # Wait until interactive toolbar controls are rendered
        expect(self.location_finder_tool).to_be_visible(timeout=timeout_ms)

        # Wait until map image tiles are actively rendered and visible on screen
        expect(self.visible_map_tiles.first).to_be_visible(timeout=timeout_ms)
        self.logger.info("GIS Map successfully loaded and displayed with visible map tiles")

    def verify_gis_map_controls(self, timeout_ms: int = 15000) -> None:
        """
        Validates all major interactive map tools (Location Finder, Measure Tools,
        Zoom-in, Zoom-out, Pan, Basemap) and tabs (Search, Layers) are displayed.
        """
        self.logger.info("Verifying GIS interactive toolbar controls")
        expect(self.location_finder_tool).to_be_visible(timeout=timeout_ms)
        expect(self.measure_tools).to_be_visible(timeout=timeout_ms)
        expect(self.zoom_in_tool).to_be_visible(timeout=timeout_ms)
        expect(self.zoom_out_tool).to_be_visible(timeout=timeout_ms)
        expect(self.pan_tool).to_be_visible(timeout=timeout_ms)
        expect(self.basemap_tool).to_be_visible(timeout=timeout_ms)
        expect(self.search_tab).to_be_visible(timeout=timeout_ms)
        expect(self.layers_tab).to_be_visible(timeout=timeout_ms)

    def click_return_to_application(self) -> None:
        """Clicks the 'Return to Application' button."""
        self.logger.info("Clicking 'Return to Application' button")
        expect(self.return_to_application_button).to_be_visible(timeout=15000)
        self.return_to_application_button.click(force=True)
        self._wait_for_loader()
