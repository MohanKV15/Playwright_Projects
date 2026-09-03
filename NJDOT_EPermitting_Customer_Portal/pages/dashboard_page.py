import re
import logging
from playwright.sync_api import Page, expect
from NJDOT_EPermitting_Customer_Portal.core.base_page import BasePage

class DashboardPage(BasePage):
    """Page Object for the Authenticated Customer Dashboard."""
    
    DASHBOARD_URL = "CustomerPortalDashboardFull"

    def __init__(self, page: Page, script_name: str = "dashboard"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    # Open the application login page and confirm the title is correct.
    def goto_application(self, url):
        from NJDOT_EPermitting_Customer_Portal.pages.login.login_page import LoginPage
        LoginPage(self.page).goto(url)

    # Fill login credentials and submit the sign-in form.
    def login(self, email, password):
        from NJDOT_EPermitting_Customer_Portal.pages.login.login_page import LoginPage
        LoginPage(self.page).login(email, password)

    # Wait until the dashboard is visible after login.
    def wait_for_dashboard_to_load(self):
        from NJDOT_EPermitting_Customer_Portal.pages.login.login_page import LoginPage
        LoginPage(self.page).wait_for_dashboard()

    # Confirm the browser is on the expected dashboard URL.
    def assert_dashboard_url(self):
        from NJDOT_EPermitting_Customer_Portal.pages.login.login_page import LoginPage
        LoginPage(self.page).wait_for_dashboard()

    # Click the Submit Application card from the dashboard.
    def click_submit_application(self):
        self.logger.info("Clicking Submit Application card.")
        tile_candidates = [
            self.page.locator("#btnSubmitApp"),
            self.page.get_by_text("Submit Application", exact=True),
            self.page.get_by_role("link", name=re.compile(r"Submit\s+Application", re.I)),
            self.page.get_by_role("button", name=re.compile(r"Submit\s+Application", re.I)),
        ]
        tile = self._first_visible_candidate(tile_candidates, timeout_ms=30000)
        if tile is None:
            raise AssertionError("Submit Application card was not visible on the dashboard.")
        expect(tile).to_be_visible(timeout=30000)
        try:
            expect(tile).to_be_enabled(timeout=10000)
        except Exception:
            pass
        try:
            with self.page.expect_navigation():
                tile.click()
            self.logger.info("Submit Application card clicked.")
        except Exception as ex:
            self.logger.error("Click failed: %s", ex)
            tile.screenshot(path=f"{self.script_name}_submit_tile_click_failed.png")
            self.page.wait_for_timeout(2000)
            with self.page.expect_navigation():
                tile.click()
