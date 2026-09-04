import logging
import re
from typing import Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Staff_Portal.utils.config import Config
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Page Object representing the IDOT Outdoor Advertising Staff Portal Login Page.
    Encapsulates security PIN entry, user credentials, login actions, branding verification,
    and invalid credential error alert handling.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Branding & Heading Locators
        self.heading_title = page.get_by_role("heading", name="**Test** Outdoor Advertising")
        self.heading_banner = page.locator("div").filter(has_text="**Test**Outdoor Advertising")

        # Form Input Locators
        self.pin_spinbutton = page.get_by_role("spinbutton")
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")

        # Alert / Error Modal Locators
        self.invalid_credentials_alert = page.get_by_text("You have entered an invalid")
        self.modal_ok_button = page.get_by_role("button", name="OK")
        self.validation_errors = page.locator(".field-validation-error, .text-danger, .validation-summary-errors")

    def navigate_to_login(self) -> None:
        """Navigates to the Staff Portal login page URL."""
        self.navigate(Config.LOGIN_URL)

    def verify_login_page_elements(self, timeout_ms: int = 25000) -> None:
        """Asserts visibility of key login page branding elements."""
        self.logger.info("Verifying login page branding and header elements")
        expect(self.heading_title).to_be_visible(timeout=timeout_ms)

    def fill_pin(self, pin: str = "11") -> bool:
        """Fills security PIN spinbutton if visible."""
        try:
            if self.pin_spinbutton.is_visible(timeout=1000):
                self.logger.info(f"Filling security PIN: '{pin}'")
                self.pin_spinbutton.click()
                self.pin_spinbutton.fill(pin)
                return True
        except Exception:
            pass
        return False

    def fill_email(self, email: str) -> None:
        """Fills email textbox or clears if empty."""
        self.logger.info(f"Filling email input: '{email}'")
        self.email_input.click()
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

    def fill_password(self, password: str) -> None:
        """Fills password textbox or clears if empty."""
        self.logger.info("Filling password input")
        self.password_input.click()
        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

    def click_login_button(self) -> None:
        """Clicks the Login button."""
        self.logger.info("Clicking Login button")
        self.login_button.click()

    def login(self, email: str, password: str, pin: str = "11") -> None:
        """
        Executes full login sequence:
        1. Fills security PIN (spinbutton) if prompted
        2. Fills Email
        3. Fills Password
        4. Clicks Login and waits for portal navigation or invalid error popup
        """
        if pin:
            self.fill_pin(pin)
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()

        # If credentials were provided, wait for either successful portal navigation
        # OR an invalid login error popup to appear (without waiting for the full 30s timeout)
        if email and password:
            try:
                self.page.wait_for_function(
                    """() => {
                        const hasUrl = /Portal|Home/i.test(window.location.href);
                        const hasAlert = document.body && (
                            document.body.innerText.includes('invalid') ||
                            document.body.innerText.includes('Invalid') ||
                            document.querySelector('.k-dialog:not([style*="display: none"]), .modal.show, .alert-danger') !== null
                        );
                        return hasUrl || hasAlert;
                    }""",
                    timeout=30000
                )
            except Exception:
                pass
            self._wait_for_loader()

    def verify_invalid_login_popup(self) -> None:
        """Asserts that 'You have entered an invalid' error modal is visible."""
        self.logger.info("Verifying invalid login alert popup")
        expect(self.invalid_credentials_alert).to_be_visible(timeout=10000)

    def dismiss_error_modal(self) -> None:
        """Clicks OK button on invalid login popup modal and confirms it closes."""
        self.logger.info("Dismissing error modal dialog by clicking OK")
        ok_btn = self.page.locator(
            ".k-dialog button:has-text('OK'), .modal button:has-text('OK'), button:has-text('OK'), .k-button:has-text('OK')"
        ).first
        if ok_btn.is_visible(timeout=5000):
            ok_btn.click(force=True)
            self._wait_for_loader()
            try:
                self.invalid_credentials_alert.wait_for(state="hidden", timeout=5000)
            except Exception:
                pass

    def is_at_login_page(self) -> bool:
        """Checks if current browser state is at the Login page."""
        return "Accounts/Account" in self.page.url or self.email_input.is_visible()
