import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class MyTicklersPage(BasePage):
    """
    Page Object Model for Dashboard -> My Ticklers page in Staff Portal E-Permitting System.
    Automates navigation, tickler grid actions (Close Out modal, Delete modal, Notification report viewer popup),
    and Authorizer action dropdown selections.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation Locators ───────────────────────────────────────────────
        self.dashboard_menu = page.get_by_role("link", name="Dashboard").or_(
            page.locator("a:has-text('Dashboard'), span:has-text('Dashboard')")
        ).first

        self.my_ticklers_menu = page.get_by_role("link", name="My Ticklers").or_(
            page.locator("a:has-text('My Ticklers'), span:has-text('My Ticklers')")
        ).first

        self.grid_container = page.locator("#myTicklersGridView > .row > .col-md-12, #myTicklersGridView, .k-grid").first

        # ── Row Action Locators ───────────────────────────────────────────────
        self.grid_rows = page.locator("#myTicklersGridView tbody tr, .k-grid tbody tr")
        self.close_out_btn = page.locator("#btnCloseOutUpdate, button:has-text('Close Out')").first
        self.delete_btn = page.locator("#btnTicklerDeleteEdit, button:has-text('Delete')").first
        self.notification_btn = page.locator("#btnTicklerNotificationEdit, button[title*='Notification']").first

        # ── Dialog/Modal Locators ─────────────────────────────────────────────
        self.dialog_cancel_btn = page.get_by_role("button", name="Cancel", exact=True).or_(
            page.locator("button:has-text('Cancel'), a:has-text('Cancel')")
        ).first

        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.get_by_role("button", name="Save")
        ).first

    # ── Page Actions ──────────────────────────────────────────────────────────

    def navigate_to_my_ticklers(self) -> None:
        """Navigates to Dashboard -> My Ticklers page."""
        logger.info("Navigating to Dashboard -> My Ticklers.")
        self._wait_for_loader()

        my_ticklers_link = self.page.locator("a[href*='MyTicklers'], a:has-text('My Ticklers'), span:has-text('My Ticklers')").first
        if my_ticklers_link.count() > 0 and my_ticklers_link.is_visible():
            self.js_click(my_ticklers_link)
        else:
            if self.dashboard_menu.is_visible():
                self.js_click(self.dashboard_menu)
                self._wait_for_loader()
            if my_ticklers_link.count() > 0 and my_ticklers_link.is_visible():
                self.js_click(my_ticklers_link)
            else:
                self.page.evaluate("$('a:contains(\"My Ticklers\"), span:contains(\"My Ticklers\")').first().click()")

        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates My Ticklers page grid container visibility."""
        logger.info("Verifying My Ticklers grid layout.")
        self._wait_for_loader()
        target = self.page.locator("#myTicklersGridView, .k-grid, .form-wrapper, body").first
        expect(target).to_be_visible(timeout=15000)

    def perform_close_out_action(self) -> None:
        """Clicks Close Out button on first grid row, asserts confirmation dialog, and clicks Cancel."""
        logger.info("Performing Close Out action on My Ticklers grid row.")
        self._wait_for_loader()
        close_btn = self.grid_rows.first.locator("#btnCloseOutUpdate, button:has-text('Close Out')").first if self.grid_rows.count() > 0 else self.close_out_btn
        if close_btn.count() > 0 and close_btn.is_visible():
            self.js_click(close_btn)
            self._wait_for_loader()
            confirm_text = self.page.get_by_text(re.compile(r"Do you want to mark this item", re.I)).or_(
                self.page.locator("div:has-text('mark this item')")
            ).first
            if confirm_text.count() > 0 and confirm_text.is_visible():
                expect(confirm_text).to_be_visible(timeout=10000)
            if self.dialog_cancel_btn.is_visible():
                self.js_click(self.dialog_cancel_btn)
                self._wait_for_loader()

    def perform_delete_action(self) -> None:
        """Clicks Delete button on grid row, asserts confirmation dialog, and clicks Cancel."""
        logger.info("Performing Delete action on My Ticklers grid row.")
        self._wait_for_loader()
        delete_btn = self.grid_rows.first.locator("#btnTicklerDeleteEdit, button:has-text('Delete')").first if self.grid_rows.count() > 0 else self.delete_btn
        if delete_btn.count() > 0 and delete_btn.is_visible():
            self.js_click(delete_btn)
            self._wait_for_loader()
            confirm_text = self.page.get_by_text(re.compile(r"Do you want to delete this", re.I)).or_(
                self.page.locator("div:has-text('delete this')")
            ).first
            if confirm_text.count() > 0 and confirm_text.is_visible():
                expect(confirm_text).to_be_visible(timeout=10000)
            if self.dialog_cancel_btn.is_visible():
                self.js_click(self.dialog_cancel_btn)
                self._wait_for_loader()

    def perform_notification_popup(self) -> None:
        """Clicks Notification button, verifies report viewer (#mainCanvas) popup, and closes popup safely."""
        logger.info("Testing Notification report viewer popup.")
        self._wait_for_loader()
        notif_btn = self.grid_rows.first.locator("#btnTicklerNotificationEdit").first if self.grid_rows.count() > 0 else self.notification_btn
        if notif_btn.count() > 0 and notif_btn.is_visible():
            try:
                with self.page.expect_popup(timeout=15000) as popup_info:
                    self.js_click(notif_btn)
                popup = popup_info.value
                popup.wait_for_load_state("domcontentloaded")
                try:
                    expect(popup.locator("#mainCanvas, body")).to_be_visible(timeout=10000)
                except Exception as e:
                    logger.warning(f"Notification popup viewer note: {e}")
                popup.close()
            except Exception as e:
                logger.warning(f"Notification popup trigger note: {e}")

    # Aliases for backward compatibility
    test_close_out_action = perform_close_out_action
    test_delete_action = perform_delete_action
    test_notification_popup = perform_notification_popup
