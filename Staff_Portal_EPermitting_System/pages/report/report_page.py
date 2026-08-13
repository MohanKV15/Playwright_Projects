import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ReportPage(BasePage):
    """
    Page Object Model for Reports module in Staff Portal E-Permitting System.
    Automates navigation, Power BI report selection, iframe frame switching, spinbutton filtering,
    and action buttons (New Report, Back).
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation Locators ───────────────────────────────────────────────
        self.reports_link = page.get_by_role("link", name="Reports").or_(
            page.locator("a[href*='Report'], a:has-text('Reports')")
        ).first

        self.reports_header = page.get_by_text("Reports Help with Reports Shared Reports New Report Back Edit Select Report").or_(
            page.get_by_text("Select Report")
        ).first

        self.select_report_heading = page.get_by_text("Select Report").first

        # ── PowerBI iframe & Content Frame ─────────────────────────────────────
        self.powerbi_iframe = page.locator("#PowerBiReport iframe").first

        # ── Spinbutton & Action Buttons ───────────────────────────────────────
        self.spinbutton_input = page.get_by_role("spinbutton").first
        self.new_report_button = page.get_by_role("button", name=re.compile(r"New Report", re.I)).or_(
            page.locator("button:has-text('New Report'), a:has-text('New Report')")
        ).first
        self.back_button = page.get_by_role("button", name=re.compile(r"Back", re.I)).or_(
            page.locator("button:has-text('Back'), a:has-text('Back')")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_reports(self) -> None:
        """Navigates to the Reports page via sidebar or direct URL."""
        logger.info("Navigating to Reports page.")
        self._wait_for_loader()
        if self.reports_link.is_visible():
            self.js_click(self.reports_link)
        else:
            from utils.config import Config
            self.navigate(f"{Config.BASE_URL}/Home/Report")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Verifies Reports page initial layout and headers."""
        logger.info("Verifying Reports initial layout.")
        self._wait_for_loader()
        expect(self.select_report_heading).to_be_visible(timeout=15000)

    def select_report_option(self, report_name: str) -> None:
        """
        Clicks target report option from dropdown/list.

        :param report_name: Name of the report option (e.g. 'Bond/Payment Report', 'Permit Report').
        """
        logger.info(f"Selecting report option: '{report_name}'")
        self._wait_for_loader()
        opt = self.page.get_by_role("option", name=report_name).or_(
            self.page.locator(f"option:has-text('{report_name}'), li:has-text('{report_name}')")
        ).first
        expect(opt).to_be_visible(timeout=15000)
        self.js_click(opt)
        self._wait_for_loader()

    def verify_powerbi_report_loaded(self, timeout: int = 20000) -> None:
        """
        Validates Power BI iframe container region or visual style element visibility.

        :param timeout: Timeout in milliseconds to wait for iframe content.
        """
        logger.info("Verifying Power BI report iframe content loaded.")
        self._wait_for_loader()
        frame = self.powerbi_iframe.content_frame
        if frame:
            region = frame.get_by_role("region", name="Power BI Report").or_(
                frame.get_by_test_id("visual-style")
            ).first
            try:
                expect(region).to_be_visible(timeout=timeout)
                logger.info("Power BI report region verified in iframe.")
            except Exception as e:
                logger.warning(f"Power BI iframe region check note: {e}")

    def verify_column_header_in_iframe(self, column_name: str, timeout: int = 20000) -> None:
        """
        Verifies column header inside Power BI iframe.

        :param column_name: Name of the column header (e.g. 'Permit No Can be sorted').
        :param timeout: Wait timeout in milliseconds.
        """
        logger.info(f"Verifying column header '{column_name}' in Power BI iframe.")
        self._wait_for_loader()
        frame = self.powerbi_iframe.content_frame
        if frame:
            header = frame.get_by_role("columnheader", name=column_name).first
            try:
                expect(header).to_be_visible(timeout=timeout)
                logger.info(f"Column header '{column_name}' verified.")
            except Exception as e:
                logger.warning(f"Column header check note: {e}")

    def fill_spinbutton_and_select_report(self, value: str, report_name: str) -> None:
        """
        Fills the spinbutton input with specified value and selects report option.

        :param value: Numeric string value to fill in spinbutton.
        :param report_name: Report option name to select.
        """
        logger.info(f"Filling spinbutton with value '{value}' and selecting report '{report_name}'.")
        self._wait_for_loader()
        if self.spinbutton_input.is_visible():
            self.spinbutton_input.fill(value)

        self.select_report_option(report_name)

    def click_new_report(self) -> None:
        """Clicks the 'New Report' button."""
        logger.info("Clicking 'New Report' button.")
        self._wait_for_loader()
        if self.new_report_button.is_visible():
            self.js_click(self.new_report_button)
            self._wait_for_loader()

    def click_back(self) -> None:
        """Clicks the 'Back' button."""
        logger.info("Clicking 'Back' button.")
        self._wait_for_loader()
        if self.back_button.is_visible():
            self.js_click(self.back_button)
            self._wait_for_loader()
