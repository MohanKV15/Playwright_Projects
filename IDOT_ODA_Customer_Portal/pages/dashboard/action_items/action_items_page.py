import logging
import re
from playwright.sync_api import Page, expect
from IDOT_ODA_Customer_Portal.utils.config import Config
from IDOT_ODA_Customer_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)


class ActionItemsPage(BasePage):
    """
    Page Object Model representing the Customer Portal: Action Items workflow.

    Encapsulates:
    - Navigation from Dashboard to Action Items
    - Verification of Action Items heading and #ActionItemGrid
    - Selection and opening of the 1st record row in the table via KendoGrid
    - Saving application for later submission ('Save for Later') via KendoButton
    - Confirmation dialog sequence ('The page information will be...' -> 'OK'
      and 'Record saved successfully.' -> 'OK') via Kendo alert handling
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Dashboard Navigation Locators
        self.action_items_dashboard_card = page.get_by_text(
            "Action Items Complete your", exact=False
        ).first
        self.action_items_btn = page.locator("#btnActionItems")
        self.action_items_heading = page.get_by_role(
            "heading", name=re.compile(r"Action Items", re.I)
        ).or_(page.locator("text=Action Items")).first

        # 2. Grid Table Locator
        self.action_item_grid = page.locator("#ActionItemGrid")

        # 3. Application Form & Save for Later Locators
        self.save_for_later_btn = (
            page.get_by_role("button", name=re.compile(r"Save for Later", re.I))
            .or_(page.locator("#btnSaveForLater, button:has-text('Save for Later')"))
            .first
        )

        # 4. Confirmation Dialog Locators
        self.dialog_info_prompt = page.get_by_text(
            "The page information will be", exact=False
        ).first
        self.dialog_record_saved = page.get_by_text(
            "Record saved successfully.", exact=False
        ).first

    # -----------------------------------------------------------------
    # Navigation & Verification Methods
    # -----------------------------------------------------------------
    def navigate_to_action_items(self) -> "ActionItemsPage":
        """Navigates from Dashboard to the Action Items page."""
        self.logger.info("Navigating to Action Items page")
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

        # Return immediately if already on Action Items page
        if self.action_items_heading.is_visible() and self.action_item_grid.is_visible():
            return self

        expect(self.action_items_dashboard_card).to_be_visible(timeout=30000)
        expect(self.action_items_btn).to_be_visible(timeout=30000)
        self.action_items_btn.click()
        self._wait_for_loader(timeout=30000)

        self.verify_action_items_page()
        self.logger.info("Successfully navigated to Action Items page")
        return self

    def verify_action_items_page(self, timeout_ms: int = 15000) -> "ActionItemsPage":
        """Asserts visibility of the Action Items heading and #ActionItemGrid."""
        self.logger.info("Verifying Action Items heading and #ActionItemGrid")
        expect(self.action_items_heading).to_be_visible(timeout=timeout_ms)
        expect(self.action_item_grid).to_be_visible(timeout=timeout_ms)
        return self

    # -----------------------------------------------------------------
    # Table Interaction (1st Record Selection via KendoGrid)
    # -----------------------------------------------------------------
    def open_first_action_item(self, timeout_ms: int = 15000) -> "ActionItemsPage":
        """
        Locates the 1st record row in #ActionItemGrid and clicks its action button.
        Always targets index 0 using the encapsulated KendoGrid component.
        """
        self.logger.info("Opening the 1st record in #ActionItemGrid via KendoGrid")
        row_text = self.kendo_grid.get_row_text(self.action_item_grid, row_index=0)
        self.logger.info(f"Targeting 1st record row: '{row_text}'")

        self.click_grid_row_button(self.action_item_grid, row_index=0, timeout_ms=timeout_ms)
        self._wait_for_loader(timeout=25000)
        return self

    # -----------------------------------------------------------------
    # Save for Later & Confirmation Dialog Methods
    # -----------------------------------------------------------------
    def click_save_for_later(self, timeout_ms: int = 15000) -> "ActionItemsPage":
        """Clicks 'Save for Later' button on the opened application form using KendoButton."""
        self.logger.info("Clicking 'Save for Later' button")
        self._wait_for_loader()
        self.click_kendo_button(self.save_for_later_btn, timeout_ms=timeout_ms)
        self._wait_for_loader()
        return self

    def confirm_save_for_later_dialog(self, timeout_ms: int = 15000) -> "ActionItemsPage":
        """Asserts 'The page information will be...' confirmation modal and clicks 'OK'."""
        self.logger.info("Confirming 'The page information will be...' modal (clicking OK)")
        expect(self.dialog_info_prompt).to_be_visible(timeout=timeout_ms)
        self.click_dialog_ok(timeout_ms=timeout_ms)
        return self

    def confirm_record_saved_modal(self, timeout_ms: int = 15000) -> "ActionItemsPage":
        """Asserts 'Record saved successfully.' alert modal and clicks 'OK'."""
        self.logger.info("Confirming 'Record saved successfully.' modal (clicking OK)")
        expect(self.dialog_record_saved).to_be_visible(timeout=timeout_ms)
        self.click_dialog_ok(timeout_ms=timeout_ms)
        return self

    def save_and_confirm_application(self) -> "ActionItemsPage":
        """Executes 'Save for Later' and handles both confirmation modals in sequence."""
        self.click_save_for_later()
        self.confirm_save_for_later_dialog()
        self.confirm_record_saved_modal()
        return self

    def complete_action_items_save_for_later_flow(self) -> "ActionItemsPage":
        """
        Executes full end-to-end Action Items Save for Later workflow:
        1. Navigates from Dashboard to Action Items
        2. Asserts heading and #ActionItemGrid
        3. Clicks button in 1st row of table via KendoGrid
        4. Clicks 'Save for Later' via KendoButton
        5. Confirms 'The page information will be...' -> 'OK'
        6. Confirms 'Record saved successfully.' -> 'OK'
        """
        self.navigate_to_action_items()
        self.open_first_action_item()
        self.save_and_confirm_application()
        return self
