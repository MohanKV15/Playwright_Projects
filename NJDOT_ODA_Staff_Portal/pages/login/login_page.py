import logging
import re
from pages.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Locators structure matching the NJDOT accounts portal page
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")
        
        # Link for entering the Outdoor Advertising application (if applicable)
        self.outdoor_advertising_link = page.get_by_role("link", name=re.compile(r"Outdoor Advertising", re.I)) if hasattr(re, 'compile') else page.get_by_role("link", name="Outdoor Advertising")
        
        # Logout link
        self.logout_link = page.get_by_role("link", name=re.compile(r"Logout", re.I)) if hasattr(re, 'compile') else page.get_by_role("link", name="Logout")
        
        # Fallback locator for catching error messages during invalid login attempts
        self.error_message = page.locator(".toast-message, .validation-summary-errors, .error-message, :text-matches('Invalid', 'i')")
        
        # Negative login error locators
        self.email_mandatory_error = page.get_by_text("Email is mandatory")
        self.password_mandatory_error = page.get_by_text("Password is mandatory")

    def load(self, url: str) -> None:
        """Navigates to the designated Login URL."""
        logger.info(f"Loading login page: {url}")
        self.page.goto(url, timeout=Config.TIMEOUT, wait_until="domcontentloaded")

    def login(self, email: str, password: str, pin: str = None) -> None:
        """Performs login using standard credentials, with professional error-proofing."""
        if email:
            logger.info(f"Entering email: {email}")
            try:
                self.email_input.click(modifiers=["ControlOrMeta"], timeout=5000)
            except Exception:
                self.email_input.click(timeout=5000)
            self.email_input.fill(email)
        else:
            logger.info("Email field left blank")
        
        if password:
            logger.info("Entering password value")
            try:
                self.password_input.click(modifiers=["ControlOrMeta"], timeout=5000)
            except Exception:
                self.password_input.click(timeout=5000)
            self.password_input.fill(password)
        else:
            logger.info("Password field left blank")
            
        logger.info("Clicking the login button")
        self.login_button.click()

    def select_outdoor_advertising(self) -> None:
        """Clicks the link to enter the Outdoor Advertising module."""
        logger.info("Selecting Outdoor Advertising application link")
        self.outdoor_advertising_link.first.click()

    def logout(self) -> None:
        """Clicks the logout link to clean up user session."""
        logger.info("Clicking logout link")
        self.logout_link.first.click()

    def get_error_message(self) -> str:
        """Fetches the error message text if visible."""
        try:
            self.error_message.first.wait_for(state="visible", timeout=10000)
            err_text = self.error_message.first.inner_text()
            logger.info(f"Retrieved login error message: '{err_text}'")
            return err_text
        except Exception:
            return ""
