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
    - Exporting payment activity records to dedicated downloads directory
      (cleans older files so only the latest download is retained)
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
        ).or_(
            page.get_by_role("heading", name=re.compile(r"Payment Activity", re.I))
        ).first

        # 2. Grid & Content Locators
        self.grid_content = page.locator(
            ".k-grid-content, #PaymentActivityGrid, #frmPaymentActivity .k-grid-content"
        ).first

        # 3. Kendo DropDownList Locators
        self.period_dropdown = (
            page.locator(
                "#frmPaymentActivity .k-dropdown, "
                "#frmPaymentActivity [data-role='dropdownlist'], "
                "#PaymentPeriod, "
                "#frmPaymentActivity span.k-widget.k-dropdown"
            )
            .or_(page.locator("#frmPaymentActivity").get_by_text("Last 6 months"))
            .first
        )

        # 4. Action Buttons
        self.export_button = (
            page.get_by_role("button", name=re.compile(r"Export", re.I))
            .or_(page.locator("#btnExport, button:has-text('Export')"))
            .first
        )
        self.back_button = (
            page.get_by_role("button", name=re.compile(r"Back", re.I))
            .or_(page.locator("#btnBack, button:has-text('Back')"))
            .first
        )
        self.dashboard_marker = (
            page.locator("#btnSubmitApp")
            .or_(page.get_by_text("Submit an Application"))
            .first
        )

    # -----------------------------------------------------------------
    # Navigation & Verification Methods
    # -----------------------------------------------------------------
    def navigate_to_payment_activity(self) -> "PaymentActivityPage":
        """Navigates from Dashboard to Payment Activity page."""
        self.logger.info("Navigating to Payment Activity page")
        self._wait_for_loader(timeout=30000)

        if "CALanding" in self.page.url or "Account" in self.page.url:
            try:
                self.page.wait_for_url(
                    re.compile(r"CADashboardFull|4321CustomerPortalDashboardFull"),
                    timeout=20000,
                )
            except Exception:
                self.page.goto(
                    f"{Config.BASE_HOST}/Portal/Page/Index/CADashboardFull",
                    wait_until="domcontentloaded",
                )

        self._wait_for_loader(timeout=30000)

        if self.payment_activity_heading.is_visible() and self.grid_content.is_visible():
            return self

        expect(self.payment_activity_dashboard_card).to_be_visible(timeout=30000)
        expect(self.view_payment_btn).to_be_visible(timeout=30000)
        self.view_payment_btn.click()
        self._wait_for_loader(timeout=30000)

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
    # Period Dropdown Filtering (Kendo Dropdown Component)
    # -----------------------------------------------------------------
    def select_period(self, period_text: str, timeout_ms: int = 10000) -> "PaymentActivityPage":
        """
        Selects a time period option from the Kendo DropDownList (e.g. '2026', 'Last 6 months').
        Uses the encapsulated KendoDropdown component with resilient option selection.
        """
        self.logger.info(f"Filtering payment activity by period: '{period_text}'")
        self._wait_for_loader()

        selected = self.select_kendo_dropdown(self.period_dropdown, period_text, timeout_ms=timeout_ms)
        if not selected:
            # Fallback direct UI interaction
            self.period_dropdown.scroll_into_view_if_needed()
            self.period_dropdown.click(force=True)
            self.page.wait_for_timeout(200)

            opt = (
                self.page.get_by_role("option", name=re.compile(f"^{re.escape(period_text)}$", re.I))
                .or_(self.page.locator("[role='option']:visible").filter(has_text=period_text))
                .first
            )
            opt.wait_for(state="visible", timeout=timeout_ms)
            opt.click(force=True)

        self._wait_for_loader()
        return self

    # -----------------------------------------------------------------
    # Export & Downloads Management (Ensures single latest file)
    # -----------------------------------------------------------------
    def export_payment_activity(self, timeout_ms: int = 30000) -> Path:
        """
        Triggers 'Export', cleans the download directory beforehand,
        and saves the latest exported file into the downloads folder.
        Returns the saved file Path and verifies it exists and is not empty.
        """
        self.logger.info("Exporting payment activity history to downloads folder")
        return self.download_export_file(
            self.export_button,
            default_filename="PaymentActivityExport.csv",
            timeout_ms=timeout_ms,
        )

    # -----------------------------------------------------------------
    # Back to Dashboard
    # -----------------------------------------------------------------
    def click_back(self, timeout_ms: int = 20000) -> None:
        """Clicks 'Back' button and verifies navigation back to the Dashboard."""
        self.logger.info("Clicking 'Back' button to return to Dashboard")
        self.back_button.scroll_into_view_if_needed()
        self.click_kendo_button(self.back_button)
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

