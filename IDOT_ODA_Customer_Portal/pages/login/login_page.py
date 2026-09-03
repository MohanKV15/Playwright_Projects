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
    Encapsulates all recorded locators and authentication workflow interactions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Page Header & Welcome Information Locators
        self.heading_title = page.get_by_role("heading", name="**Test** Outdoor Advertising")
        self.heading_link = page.get_by_role("link", name="**Test** Outdoor Advertising")
        self.welcome_tutorial_text = page.get_by_text("Click here to view our YouTube tutorial page. Welcome to the Illinois")
        self.login_section_header = page.get_by_text("Login Login Forgot/Reset")

        # Login Form Inputs & Buttons
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.create_account_button = page.get_by_role("button", name="Create an Account")
        
        # Security PIN Input
        self.pin_spinbutton = page.get_by_role("spinbutton")

        # Invalid Credentials Alert & Modal Dialog Locators
        self.invalid_credentials_alert = page.get_by_text("You have entered an invalid")
        self.modal_ok_button = page.get_by_role("button", name="OK")
        self.validation_error_msg = page.locator(".field-validation-error, .text-danger, .validation-summary-errors")
        self.domain_header_filter = page.locator("div").filter(has_text=re.compile(r"^u-idcp\.bemcorp\.net$"))

    def navigate_to_login(self) -> None:
        """Navigates to the portal login page URL."""
        self.navigate(Config.LOGIN_URL)

    def verify_login_page_elements(self) -> None:
        """Asserts visibility of key login page branding and welcome elements."""
        self.logger.info("Verifying login page branding and header elements")
        expect(self.heading_link).to_be_visible()
        expect(self.welcome_tutorial_text).to_be_visible()
        expect(self.login_section_header).to_be_visible()

    def fill_email(self, email: str) -> None:
        """Fills email textbox or clears if empty string."""
        self.logger.info(f"Filling email input: '{email}'")
        self.email_input.click()
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

    def fill_password(self, password: str) -> None:
        """Fills password textbox or clears if empty string."""
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

    def click_create_account(self) -> None:
        """Clicks the Create an Account button to navigate to Company Registration."""
        self.logger.info("Clicking Create an Account button")
        self.create_account_button.click()

    def login(self, email: str, password: str) -> None:
        """Executes full login sequence with email and password."""
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()

    def fill_pin_if_prompted(self, pin: str = "11") -> bool:
        """Fills security PIN spinbutton if displayed."""
        if self.pin_spinbutton.is_visible(timeout=5000):
            self.logger.info(f"Filling security PIN spinbutton: '{pin}'")
            self.pin_spinbutton.fill(pin)
            return True
        return False

    def verify_invalid_login_popup(self) -> None:
        """Asserts that 'You have entered an invalid' error modal is visible."""
        self.logger.info("Verifying invalid login alert popup")
        expect(self.invalid_credentials_alert).to_be_visible()

    def dismiss_error_modal(self) -> None:
        """Clicks OK button on invalid login popup modal."""
        self.logger.info("Dismissing error modal dialog by clicking OK")
        if self.modal_ok_button.is_visible(timeout=5000):
            self.modal_ok_button.click()
