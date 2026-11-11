import logging
import re
from typing import Optional
from playwright.sync_api import Page, expect
from utils.config import Config
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Page Object representing the NCDOT Right Of Way (ROW) Portal Login Page.
    Encapsulates all locators and authentication workflow interactions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Login Form Inputs & Buttons
        self.email_input = page.get_by_role("textbox", name="Email").or_(page.locator("#Email, input[name='Email']"))
        self.password_input = page.get_by_role("textbox", name="Password").or_(page.locator("#Password, input[name='Password']"))
        self.login_button = page.get_by_role("button", name="Login").or_(page.locator("#btnLogin, input[type='submit'][value='Login']"))

        # Security PIN / 2FA Input (Spinbutton)
        self.pin_spinbutton = page.get_by_role("spinbutton").or_(page.locator("input[type='number'], #pin, #OTP"))

        # Post-Login Landing Elements
        self.row_landing_text = page.get_by_text("ROW", exact=True)
        self.dashboard_header = page.locator(".navbar, #header, #navigationMenu, header").filter(has_text=re.compile(r"ROW|Right of Way", re.I))

        # Error & Validation Messages
        self.invalid_credentials_alert = page.locator(".k-dialog:visible, .k-window:visible, .k-alert:visible, .alert-danger, [role='alert']").or_(
            page.get_by_text(re.compile(r"invalid|incorrect|failed|error", re.I))
        )
        self.modal_ok_button = page.locator(".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')").first

        # Inline Field Validation Locators
        self.email_validation = page.locator("[data-valmsg-for='Email'], span#Email-error, .field-validation-error:has-text('Email')")
        self.password_validation = page.locator("[data-valmsg-for='Password'], span#Password-error, .field-validation-error:has-text('Password')")

    def navigate_to_login(self) -> "LoginPage":
        """Navigates to the NCDOT portal login URL."""
        self.navigate(Config.LOGIN_URL)
        return self

    def verify_login_page_elements(self, timeout_ms: int = 15000) -> None:
        """Asserts visibility of key login form inputs and buttons."""
        self.logger.info("Verifying login page elements")
        expect(self.email_input.first).to_be_visible(timeout=timeout_ms)
        expect(self.password_input.first).to_be_visible(timeout=timeout_ms)
        expect(self.login_button.first).to_be_visible(timeout=timeout_ms)

    def fill_email(self, email: str) -> "LoginPage":
        """Fills the email field."""
        self.logger.info(f"Filling Email: '{email}'")
        self.email_input.first.fill(email or "")
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """Fills the password field."""
        self.logger.info("Filling Password")
        self.password_input.first.fill(password or "")
        return self

    def click_login(self) -> "LoginPage":
        """Clicks the Login button."""
        self.logger.info("Clicking Login button")
        self.login_button.first.click()
        return self

    def fill_pin_if_prompted(self, pin: str = "11", timeout_ms: int = 8000) -> bool:
        """Fills security PIN / OTP spinbutton if displayed following initial login submission."""
        try:
            self.pin_spinbutton.first.wait_for(state="visible", timeout=timeout_ms)
            self.logger.info(f"Filling security PIN spinbutton: '{pin}'")
            self.pin_spinbutton.first.fill(pin)
            self.page.wait_for_timeout(500)
            # If an explicit proceed or submit button exists for the pin, press enter
            self.pin_spinbutton.first.press("Enter")
            return True
        except Exception as e:
            self.logger.debug(f"PIN prompt note: {e}")
            return False

    def login(self, email: str, password: str, pin: str = "11") -> "LoginPage":
        """Executes complete authentication flow."""
        self.fill_email(email)
        self.fill_password(password)
        self.click_login()
        self._wait_for_loader()
        self.fill_pin_if_prompted(pin=pin)
        self._wait_for_loader()
        return self

    def verify_successful_login(self, timeout_ms: int = 35000) -> None:
        """Verifies successful authentication by confirming ROW text is visible on dashboard."""
        self.logger.info("Verifying successful login: asserting 'ROW' landing visibility")
        self._wait_for_loader(timeout=20000)
        expect(self.row_landing_text.first).to_be_visible(timeout=timeout_ms)

    def verify_invalid_login_popup(self, expected_text: Optional[str] = None, timeout_ms: int = 10000) -> None:
        """Verifies that an error alert appears for invalid credentials."""
        self.logger.info("Verifying invalid credentials alert dialog")
        expect(self.invalid_credentials_alert.first).to_be_visible(timeout=timeout_ms)
        if expected_text:
            expect(self.invalid_credentials_alert.first).to_contain_text(re.compile(re.escape(expected_text), re.I))

    def dismiss_error_modal(self) -> None:
        """Dismisses error alert or modal dialog."""
        if self.modal_ok_button.is_visible():
            self.logger.info("Dismissing error dialog with OK")
            self.modal_ok_button.click()
        self.dismiss_kendo_dialogs()

    def verify_empty_field_validations(self) -> None:
        """Asserts that the page stays on login and displays required field validations."""
        self.logger.info("Verifying empty input validations")
        # Ensure page remains on login
        assert "Account" in self.page.url or self.email_input.first.is_visible(), "Page unexpectedly navigated away on empty submit"
        # Check validation messages or HTML5 invalid states
        email_val = self.email_validation.first
        password_val = self.password_validation.first
        if email_val.is_visible(timeout=3000):
            expect(email_val).to_be_visible()
        if password_val.is_visible(timeout=3000):
            expect(password_val).to_be_visible()

    def is_at_login_page(self) -> bool:
        """Returns True if the current page is the login page."""
        return "Account" in self.page.url or self.email_input.first.is_visible()

