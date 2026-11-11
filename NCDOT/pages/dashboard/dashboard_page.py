import logging
from playwright.sync_api import Page, expect
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """
    Page Object representing the NCDOT ROW Portal Dashboard & Navigation bar.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Dashboard Landing Locators
        self.row_landing_text = page.get_by_text("ROW", exact=True)
        self.navigation_menu = page.locator("#navigationMenu, .k-panelbar, nav").first
        self.logout_link = page.get_by_role("link", name="Logout").or_(page.locator("a[href*='LogOut']"))

    def verify_dashboard_loaded(self, timeout_ms: int = 15000) -> None:
        """Verifies that the dashboard landing view is visible."""
        self.logger.info("Asserting dashboard loaded with 'ROW' text")
        self._wait_for_loader()
        expect(self.row_landing_text.first).to_be_visible(timeout=timeout_ms)

    def logout(self) -> None:
        """Logs out from the portal."""
        self.logger.info("Performing logout")
        if self.logout_link.is_visible():
            self.logout_link.click()
            self._wait_for_loader()

