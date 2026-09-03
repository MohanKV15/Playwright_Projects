import re
from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # Locators
        self.email_input = page.locator("#Email")
        self.password_input = page.locator("#Password")
        self.login_button = page.locator("#btnAccountLogin")

        # Dashboard locator
        self.submit_application_btn = page.locator("#btnSubmitApp")

        self.dashboard_url_pattern = re.compile(
            r".*CustomerPortalDashboardFull"
        )

    def _wait_for_login_form(self, timeout: int = 30000):
        """Wait until login form is visible."""
        expect(self.email_input).to_be_visible(timeout=timeout)
        expect(self.password_input).to_be_visible(timeout=timeout)

    def goto(self, url: str, timeout: int = 60000, wait_until: str = "domcontentloaded"):
        """Navigate to login page.

        Uses a larger default timeout and waits for DOMContentLoaded to avoid
        timing out on pages that defer heavy resources until the window `load`.
        """
        self.page.goto(url, wait_until=wait_until, timeout=timeout)
        self._wait_for_login_form(timeout=timeout)

    def login(self, email: str, password: str):
        """Perform login."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    def wait_for_dashboard(self, timeout: int = 20000):
        """Verify dashboard page is loaded."""
        expect(self.page).to_have_url(self.dashboard_url_pattern, timeout=timeout)

        dashboard_candidates = [
            self.submit_application_btn,
            self.page.get_by_text("Submit Application", exact=True),
            self.page.get_by_role(
                "link", name=re.compile(r"Submit\s+Application", re.I)
            ),
            self.page.get_by_role(
                "button", name=re.compile(r"Submit\s+Application", re.I)
            ),
        ]

        for candidate in dashboard_candidates:
            try:
                # Restore a safer timeout for each candidate check to handle
                # latency during the initial login or dashboard load.
                expect(candidate).to_be_visible(timeout=15000)
                return candidate
            except Exception:
                continue

        raise AssertionError(
            "Dashboard loaded, but Submit Application entry point was not visible."
        )

    def assert_login_form_visible(self, timeout: int = 10000):
        """Verify login form is visible."""
        self._wait_for_login_form(timeout=timeout)