import logging
import re
from typing import Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Page Object representing the IDOT Outdoor Advertising Customer Portal Login Page.
    Encapsulates all locators and authentication workflow interactions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Branding & Tutorial Header Locators
        self.portal_branding_link = page.get_by_role(
            "link", name=re.compile(r"Outdoor Advertising", re.I)
        ).first
        self.heading_link = self.portal_branding_link
        self.dashboard_branding_link = self.portal_branding_link
        self.welcome_tutorial_text = page.get_by_text(
            "Click here to view our YouTube tutorial page. Welcome to the Illinois"
        )

        # Login Form Inputs & Buttons
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.create_account_button = page.get_by_role("button", name="Create an Account")

        # Security PIN Input
        self.pin_spinbutton = page.get_by_role("spinbutton")

        # Post-Login Customer Section
        self.customer_section = page.locator("#frmCustomer section")

        # Invalid Credentials Alert & Modal Dialog
        self.invalid_credentials_alert = page.get_by_text("You have entered an invalid")
        self.modal_ok_button = page.get_by_role("button", name="OK")

    def navigate_to_login(self) -> "LoginPage":
        """Navigates to the portal login page URL."""
        self.navigate(Config.LOGIN_URL)
        return self

    def verify_login_page_elements(self, timeout_ms: int = 15000) -> None:
        """Asserts visibility of key login page branding and welcome elements."""
        self.logger.info("Verifying login page branding and header elements")
        self.login_button.wait_for(state="visible", timeout=timeout_ms)
        expect(self.portal_branding_link).to_be_visible(timeout=timeout_ms)
        expect(self.welcome_tutorial_text).to_be_visible(timeout=timeout_ms)
        expect(self.login_button).to_be_visible(timeout=timeout_ms)

    def fill_email(self, email: str) -> "LoginPage":
        """Fills email textbox directly without redundant click."""
        self.logger.info(f"Filling email input: '{email}'")
        self.email_input.fill(email or "")
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """Fills password textbox directly without redundant click."""
        self.logger.info("Filling password input")
        self.password_input.fill(password or "")
        return self

    def click_login_button(self) -> "LoginPage":
        """Clicks the Login button."""
        self.logger.info("Clicking Login button")
        self.login_button.click()
        return self

    def click_create_account(self) -> None:
        """Clicks the Create an Account button to navigate to Company Registration."""
        self.logger.info("Clicking Create an Account button")
        self.create_account_button.click()

    def fill_pin_if_prompted(self, pin: str = "11", timeout_ms: int = 5000) -> bool:
        """Fills security PIN spinbutton if displayed."""
        try:
            if self.pin_spinbutton.is_visible(timeout=timeout_ms):
                self.logger.info(f"Filling security PIN spinbutton: '{pin}'")
                self.pin_spinbutton.fill(pin)
                return True
        except Exception:
            pass
        return False

    def verify_successful_login(self, timeout_ms: int = 15000) -> None:
        """
        Verifies that after successful authentication:
        1. Header link '**TEST** Outdoor Advertising' is visible.
        2. Customer section '#frmCustomer section' is displayed.
        """
        self.logger.info("Verifying successful login: checking dashboard branding and '#frmCustomer section'")
        self._wait_for_loader()
        expect(self.dashboard_branding_link).to_be_visible(timeout=timeout_ms)
        expect(self.customer_section).to_be_visible(timeout=timeout_ms)

    def login(
        self,
        email: str,
        password: str,
        pin: Optional[str] = None,
        verify_success: bool = False,
    ) -> "LoginPage":
        """
        Executes full login sequence with email and password.
        Optionally handles PIN and verifies successful landing if specified.
        """
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()
        if pin:
            self.fill_pin_if_prompted(pin=pin)
        if verify_success:
            self.verify_successful_login()
        return self

    def verify_invalid_login_popup(self, timeout_ms: int = 5000) -> None:
        """Asserts that 'You have entered an invalid' error modal is visible."""
        self.logger.info("Verifying invalid login alert popup")
        expect(self.invalid_credentials_alert).to_be_visible(timeout=timeout_ms)

    def dismiss_error_modal(self, timeout_ms: int = 5000) -> bool:
        """Clicks OK button on invalid login popup modal if visible."""
        self.logger.info("Dismissing error modal dialog by clicking OK")
        try:
            if self.modal_ok_button.is_visible(timeout=timeout_ms):
                self.modal_ok_button.click()
                return True
        except Exception:
            pass
        return False
