import logging
import re
from typing import Dict
from playwright.sync_api import Locator, Page, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """
    Page Object representing the IDOT Outdoor Advertising Customer Portal Dashboard.
    Encapsulates dashboard navigation, action cards verification, card navigation,
    and user logout workflows.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Branding & Customer Section Container
        self.portal_branding_link = page.get_by_role(
            "link", name=re.compile(r"Outdoor Advertising", re.I)
        ).first
        self.customer_section = page.locator("#frmCustomer section")

        # Action Cards / Tiles
        self.submit_application_card = page.get_by_text(
            re.compile(r"Submit an Application", re.I)
        ).first
        self.action_items_card = page.get_by_text(
            re.compile(r"Action Items", re.I)
        ).first
        self.application_history_card = page.get_by_text(
            re.compile(r"Application History", re.I)
        ).first
        self.payment_activity_card = page.get_by_text(
            re.compile(r"Payment Activity", re.I)
        ).first

        # Header Logout Action
        self.logout_link = page.get_by_role(
            "link", name=re.compile(r"Logout", re.I)
        ).first

        # Post-Logout Login Form Verification Elements
        self.login_button = page.get_by_role("button", name="Login")
        self.email_input = page.get_by_role("textbox", name="Email")

    def get_action_cards(self) -> Dict[str, Locator]:
        """Returns a mapped dictionary of all 4 dashboard action cards for iteration."""
        return {
            "Submit an Application": self.submit_application_card,
            "Action Items": self.action_items_card,
            "Application History": self.application_history_card,
            "Payment Activity": self.payment_activity_card,
        }

    def navigate_to_dashboard(self) -> "DashboardPage":
        """Directly navigates to the customer dashboard URL."""
        self.navigate(Config.DASHBOARD_URL)
        return self

    def verify_dashboard_cards(self, timeout_ms: int = 15000) -> "DashboardPage":
        """
        Asserts that all 4 primary dashboard action cards are visible:
        1. Submit an Application
        2. Action Items
        3. Application History
        4. Payment Activity
        """
        self.logger.info("Verifying all 4 dashboard action cards are visible")
        self._wait_for_loader()
        for name, locator in self.get_action_cards().items():
            expect(
                locator,
                f"Dashboard action card '{name}' should be visible",
            ).to_be_visible(timeout=timeout_ms)
        return self

    def click_submit_application(self) -> None:
        """Navigates to application submission by clicking the Submit an Application card."""
        self.logger.info("Clicking 'Submit an Application' card")
        self.safe_click(self.submit_application_card)

    def click_action_items(self) -> None:
        """Navigates to action items review by clicking the Action Items card."""
        self.logger.info("Clicking 'Action Items' card")
        self.safe_click(self.action_items_card)

    def click_application_history(self) -> None:
        """Navigates to application history by clicking the Application History card."""
        self.logger.info("Clicking 'Application History' card")
        self.safe_click(self.application_history_card)

    def click_payment_activity(self) -> None:
        """Navigates to payment activity by clicking the Payment Activity card."""
        self.logger.info("Clicking 'Payment Activity' card")
        self.safe_click(self.payment_activity_card)

    def click_logout(self, timeout_ms: int = 10000) -> "DashboardPage":
        """Clicks the Logout link to terminate the user session."""
        self.logger.info("Clicking Logout link")
        self.logout_link.wait_for(state="visible", timeout=timeout_ms)
        self.logout_link.click()
        self._wait_for_loader()
        return self

    def verify_redirect_to_login(self, timeout_ms: int = 15000) -> None:
        """
        Verifies that upon logging out:
        1. URL redirects back to the Account / Login endpoint.
        2. Login form elements (Login button, Email input) are visible.
        """
        self.logger.info("Verifying redirection back to Login page after logout")
        self._wait_for_loader()
        expect(
            self.page,
            "Expected page URL to redirect back to Accounts/Account",
        ).to_have_url(
            re.compile(r".*/Accounts/Account/Account.*", re.I),
            timeout=timeout_ms,
        )
        expect(
            self.login_button,
            "Login button should be visible on login page after logout",
        ).to_be_visible(timeout=timeout_ms)
        expect(
            self.email_input,
            "Email input should be visible on login page after logout",
        ).to_be_visible(timeout=timeout_ms)
