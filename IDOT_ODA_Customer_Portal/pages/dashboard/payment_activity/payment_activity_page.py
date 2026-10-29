import logging
import re
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class PaymentActivityPage(BasePage):
    """
    Page Object Model representing the Customer Portal: Payment Activity workflow.

    Encapsulates:
    - Navigation from Dashboard to Payment Activity
    - Verification of Payment Activity heading and Kendo Grid content
    - Period filtering via Kendo DropDownList (e.g. '2026', 'Last 6 months')
    - Exporting payment activity records to dedicated downloads directory (latest file retained)
    - Returning back to the Dashboard via 'Back'
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Header Locators
        self.payment_activity_dashboard_card = page.get_by_text(
            "Payment Activity View your", exact=False
        ).first
        self.view_payment_btn = page.locator("#btnViewPayment")
        self.payment_activity_heading = page.get_by_text(
            "Payment Activity Payment", exact=False
        )

        # 2. Grid & Content Locators
        self.grid_content = page.locator(".k-grid-content").first

        # 3. Kendo DropDownList Locator
        self.period_dropdown = page.locator(
            "#frmPaymentActivity .k-dropdown, #frmPaymentActivity span.k-widget.k-dropdown"
        ).first

        # 4. Action Buttons
        self.export_button = page.get_by_role("button", name=re.compile(r"Export", re.I))
        self.back_button = page.get_by_role("button", name=re.compile(r"Back", re.I))
        self.dashboard_marker = page.locator("#btnSubmitApp")

    # -----------------------------------------------------------------
    # Navigation & Verification Methods
    # -----------------------------------------------------------------
    def navigate_to_payment_activity(self) -> "PaymentActivityPage":
        """Navigates from Dashboard to Payment Activity page."""
        self.logger.info("Navigating to Payment Activity page")
        self._wait_for_loader()

        if self.payment_activity_heading.is_visible() and self.grid_content.is_visible():
            return self

        expect(self.payment_activity_dashboard_card).to_be_visible(timeout=30000)
        self.view_payment_btn.click()
        self._wait_for_loader()

        self.verify_payment_activity_page()
        self.logger.info("Successfully navigated to Payment Activity page")
        return self

    def verify_payment_activity_page(self, timeout_ms: int = 15000) -> "PaymentActivityPage":
        """Asserts visibility of Payment Activity heading and grid content."""
        self.logger.info("Verifying Payment Activity heading and grid content")
        expect(self.payment_activity_heading).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)
        return self

    # -----------------------------------------------------------------
    # Period Dropdown Filtering (Encapsulated Kendo Dropdown)
    # -----------------------------------------------------------------
    def select_period(self, period_text: str, timeout_ms: int = 10000) -> "PaymentActivityPage":
        """
        Selects a time period option from the Kendo DropDownList (e.g. '2026', 'Last 6 months').
        Delegates completely to the encapsulated KendoDropdown component.
        """
        self.logger.info(f"Filtering payment activity by period: '{period_text}'")
        self.select_kendo_dropdown(self.period_dropdown, period_text, timeout_ms=timeout_ms)
        self._wait_for_loader()
        return self

    # -----------------------------------------------------------------
    # Export & Downloads Management (Ensures latest PaymentActivity file)
    # -----------------------------------------------------------------
    def export_payment_activity(self, timeout_ms: int = 30000) -> Path:
        """
        Triggers 'Export', cleans previous payment activity exports,
        and saves the latest exported file into the downloads folder.
        """
        self.logger.info("Exporting payment activity history to downloads folder")
        return self.download_export_file(
            self.export_button,
            default_filename="PaymentActivity_Details.csv",
            clean_pattern="PaymentActivity*",
            timeout_ms=timeout_ms,
        )

    # -----------------------------------------------------------------
    # Back to Dashboard
    # -----------------------------------------------------------------
    def click_back(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Back' button and verifies navigation back to the Dashboard."""
        self.logger.info("Clicking 'Back' button to return to Dashboard")
        self.back_button.click()
        self._wait_for_loader()

        expect(self.dashboard_marker).to_be_visible(timeout=timeout_ms)
        self.logger.info(f"Successfully returned to Dashboard. Current URL: {self.page.url}")

    # -----------------------------------------------------------------
    # Full End-to-End Workflow Orchestration
    # -----------------------------------------------------------------
    def complete_payment_activity_workflow(self) -> Path:
        """
        Executes full Payment Activity workflow matching recorded user codegen:
        1. Navigates to Payment Activity
        2. Asserts heading and grid content
        3. Filters period by '2026'
        4. Filters period back to 'Last 6 months'
        5. Exports payment activity and saves latest file to downloads folder
        6. Clicks 'Back' and returns to Dashboard
        """
        self.navigate_to_payment_activity()
        self.select_period("2026")
        self.select_period("Last 6 months")
        downloaded_file = self.export_payment_activity()
        self.click_back()
        return downloaded_file
