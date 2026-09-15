import logging
from typing import Dict, Optional
from playwright.sync_api import Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.status_log_page import StatusLogPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage

logger = logging.getLogger(__name__)


class JunkyardStatusLogPage(StatusLogPage):
    """
    Optimized Page Object Model representing the Junkyards Status Log & Add Status module
    in the IDOT Outdoor Advertising Staff Portal.

    Subclasses StatusLogPage to directly inherit shared Status Log form automation logic:
    - Search company on Junkyard/Permit Search ('IDOTOAtest2')
    - Select 1st record row to activate permit session context
    - Navigate via Junkyards sidebar to 'Status Log'
    - Assert headers ('Junkyard Details Permit', 'Status Log', #StatusLogGrid)
    - Directly invoke parent class form fill (Action Type, Action Item, Date, Comments)
    - Save form, confirm OK modal dialog, and return to Status Log listing grid view
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Junkyards Specific Sidebar & Header Locators
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_status_log_link = page.get_by_role("link", name="Status Log").filter(visible=True).or_(
            page.locator("a[href*='StatusLog']").filter(visible=True)
        ).first
        self.header_junkyard_details_permit = page.get_by_text("Junkyard Details Permit").or_(
            page.get_by_text("Application Details Permit")
        ).first
        self.heading_status_log = page.get_by_role("heading", name="Status Log").filter(visible=True).or_(
            page.get_by_text("Status Log").filter(visible=True)
        ).first
        self.status_log_grid = page.locator("#StatusLogGrid").or_(
            page.locator(".k-grid-content, #StatusLogGrid, .k-grid")
        ).first
        self.status_log_listing_text = self.heading_status_log.or_(self.status_log_grid).first

    def dismiss_ok_popups(self, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """Safely dismisses visible OK modal popups."""
        dismissed = 0
        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:visible:has-text('OK')"
        ).first
        for _ in range(max_clicks):
            try:
                if ok_btn.is_visible(timeout=timeout_ms):
                    ok_btn.click(force=True)
                    self.page.wait_for_timeout(400)
                    dismissed += 1
                else:
                    break
            except Exception:
                break
        return dismissed

    def navigate_to_junkyard_status_log(self, company_name: str = "IDOTOAtest2") -> str:
        """
        Navigates to Junkyard Status Log page after activating permit session context.
        """
        self.logger.info("Navigating to Junkyard Status Log for company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self._wait_for_loader()
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.sidebar_status_log_link.is_visible():
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        expect(self.sidebar_status_log_link).to_be_visible(timeout=20000)
        self.sidebar_status_log_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.dismiss_ok_popups(timeout_ms=1000, max_clicks=1)
        self.verify_junkyard_status_log_page_loaded()
        return record_info

    def verify_junkyard_status_log_page_loaded(self, timeout_ms: int = 20000) -> None:
        """Verifies that Junkyard Details Permit header, Status Log heading, and grid are visible."""
        expect(self.header_junkyard_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.heading_status_log).to_be_visible(timeout=timeout_ms)
        expect(self.status_log_grid).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)

    def click_add_status(self, timeout_ms: int = 15000) -> None:
        """Reuses parent class click Add Status method with popup handling."""
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        super().click_add_status(timeout_ms=timeout_ms)

    def fill_and_submit_status_form(
        self,
        action_type: str = "Application Status",
        action_item: str = "Amended Permit",
        comments: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> Dict[str, str]:
        """Reuses parent class form fill & submission logic with popup handling."""
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        data = super().fill_and_submit_status_form(
            action_type=action_type,
            action_item=action_item,
            comments=comments,
            timeout_ms=timeout_ms,
        )
        self.dismiss_ok_popups(timeout_ms=2000, max_clicks=3)
        return data

    def add_status_log_full_workflow(
        self,
        company_name: str = "IDOTOAtest2",
        action_type: str = "Application Status",
        action_item: str = "Amended Permit",
        comments: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Executes complete Junkyard Status Log workflow.
        """
        self.navigate_to_junkyard_status_log(company_name=company_name)
        self.click_add_status()
        return self.fill_and_submit_status_form(
            action_type=action_type,
            action_item=action_item,
            comments=comments,
        )
