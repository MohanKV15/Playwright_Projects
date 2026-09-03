import logging
from pages.core.base_page import BasePage
from utils.config import Config

logger = logging.getLogger(__name__)

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Locators structure matching the NJDOT accounts portal page
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_text_container = page.get_by_text("Login Login Forgot/Reset")
        self.login_button = page.get_by_role("button", name="Login")
        
        # Link for entering the Outdoor Advertising application (if landing on app selection page)
        self.outdoor_advertising_link = page.locator("a:has-text('Outdoor Advertising')").first
        
        # Dashboard elements
        self.dashboard_header = page.locator("text='Outdoor Advertising E-Permitting System'").first
        self.submit_application_tile = page.get_by_text("Submit an Application").first
        
        # Logout link
        self.logout_link = page.locator("a:has-text('Logout')").first
        
        # Fallback locator for catching error messages during invalid login attempts
        self.error_message = page.locator(".toast-message, .validation-summary-errors, .error-message, text='Invalid'")
        
        # Negative login error locators
        self.email_mandatory_error = page.get_by_text("Email is mandatory")
        self.password_mandatory_error = page.get_by_text("Password is mandatory")
        self.invalid_credentials_error = page.get_by_text("You have entered an invalid")
        self.ok_button = page.get_by_role("button", name="OK")

    def load(self, url: str) -> None:
        """Navigates to the designated Login URL."""
        logger.info(f"Loading login page: {url}")
        self.page.goto(url, timeout=Config.TIMEOUT, wait_until="domcontentloaded")

    def login(self, email: str, password: str) -> None:
        """Performs login using standard credentials, with professional error-proofing."""
        if email:
            logger.info(f"Entering email: {email}")
            # Match codegen modifier behavior if needed, or fallback to direct interaction
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
            
        # Optional helper step recorded in codegen
        try:
            if self.login_text_container.is_visible(timeout=2000):
                logger.info("Clicking the login text container")
                self.login_text_container.click()
        except Exception:
            pass
            
        logger.info("Clicking the login button")
        self.login_button.click()

    def select_outdoor_advertising(self) -> None:
        """Clicks the link to enter the Outdoor Advertising module if present and not already on dashboard."""
        logger.info("Selecting 'Outdoor Advertising' application link if needed")
        if "CADashboardFull" in self.page.url:
            logger.info("Already on CADashboardFull dashboard.")
            return
        try:
            if self.outdoor_advertising_link.is_visible(timeout=3000):
                self.outdoor_advertising_link.click()
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    pass
        except Exception:
            pass

    def logout(self) -> None:
        """Clicks the logout link to clean up user session."""
        logger.info("Clicking logout link")
        self.logout_link.click()

    def get_error_message(self) -> str:
        """Fetches the error message text if visible."""
        try:
            self.error_message.first.wait_for(state="visible", timeout=3000)
            err_text = self.error_message.first.inner_text()
            logger.info(f"Retrieved login error message: '{err_text}'")
            return err_text
        except Exception:
            return ""

    def dismiss_alert(self) -> None:
        """Dismisses the modal popup by clicking the OK button."""
        logger.info("Dismissing invalid login alert dialog")
        self.ok_button.click()
