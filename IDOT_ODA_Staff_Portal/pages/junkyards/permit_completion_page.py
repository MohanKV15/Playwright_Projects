import logging
import re
from typing import Dict, Optional, Union
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.permit_completion_page import PermitCompletionPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage

logger = logging.getLogger(__name__)


class JunkyardPermitCompletionPage(PermitCompletionPage):
    """
    Page Object Model representing the Junkyards Permit Completion workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Customized for Junkyards Permit Completion Codegen sequence:
    - Search company on Junkyard/Permit Search ('IDOTOAtest2')
    - Select 1st record row to activate permit session context
    - Expand Junkyards sidebar menu and click 'Permit Completion' link
    - Assert heading ('Permit Completion')
    - Click 'Generate Permit', handle popup canvas preview (#mainCanvas), close popup, confirm OK popup
    - Click 'Save', assert 'Operation completed', and confirm OK popup
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Junkyards Specific Sidebar Links
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_permit_completion_link = page.get_by_role("link", name="Permit Completion").filter(visible=True).or_(
            page.locator("a[href*='PermitCompletion']").filter(visible=True)
        ).first

        # Codegen Specific Locators
        self.heading_permit_completion = page.get_by_role("heading", name="Permit Completion").or_(
            page.locator("h1:has-text('Permit Completion'), h2:has-text('Permit Completion'), h3:has-text('Permit Completion'), h4:has-text('Permit Completion'), div:has-text('Permit Completion Save Permit'), .form-wrapper:has-text('Permit Completion')").filter(visible=True)
        ).first

        self.generate_permit_button = page.get_by_role("button", name=re.compile(r"Generate\s+Permit", re.I)).or_(
            page.locator("button:has-text('Generate Permit'), #btnGeneratePermit")
        ).first
        self.generated_successfully_text = page.get_by_text("Generated successfully").first

        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("button:has-text('Save'), #btnSubmit")
        ).first
        self.operation_completed_text = page.get_by_text("Operation completed").first

    def dismiss_ok_popups(self, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """
        Safely dismisses visible OK modal popups without throwing errors if popups auto-dismiss or don't appear.
        """
        dismissed = 0
        ok_btn = self.page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:visible:has-text('OK'), a:visible:has-text('OK')"
        ).first
        for _ in range(max_clicks):
            try:
                if ok_btn.is_visible(timeout=timeout_ms):
                    self.logger.info("Dismissing modal popup OK button")
                    ok_btn.click(force=True)
                    self.page.wait_for_timeout(400)
                    dismissed += 1
                else:
                    break
            except Exception as e:
                self.logger.debug("Modal OK popup handling note: %s", e)
                break
        return dismissed

    def navigate_to_junkyard_permit_completion(self, company_name: str = "IDOTOAtest2") -> str:
        """
        1. Searches company name on Junkyard/Permit Search page
        2. Clicks Edit on 1st record row to activate permit session context
        3. Expands Junkyards sidebar menu if collapsed
        4. Clicks visible 'Permit Completion' menu link under Junkyards
        5. Verifies Permit Completion page loaded
        """
        self.logger.info("Navigating to Junkyard/Permit Search and searching company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self.logger.info("Navigating to Permit Completion menu link under Junkyards")
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.page.locator(".sidebar a[href*='PermitCompletion']").filter(visible=True).is_visible():
                self.logger.info("Expanding Junkyards sidebar menu")
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        target_link = self.page.get_by_role("link", name="Permit Completion").filter(visible=True).or_(
            self.page.locator("a[href*='PermitCompletion']").filter(visible=True)
        ).first

        expect(target_link).to_be_visible(timeout=20000)
        target_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.verify_junkyard_permit_completion_page_loaded()
        return record_info

    def verify_junkyard_permit_completion_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Junkyard Permit Completion page heading is visible.
        """
        self.logger.info("Verifying Junkyard Permit Completion page elements")
        expect(self.heading_permit_completion).to_be_visible(timeout=timeout_ms)

    def generate_permit(self) -> bool:
        """
        Reuse the shared permit-generation flow once the page is already loaded.
        Any visible OK dialog is automatically clicked before continuing.
        """
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        return super().generate_permit()

    def save_permit_completion(self) -> None:
        """
        Reuse the shared save flow and automatically dismiss any visible confirmation popup.
        """
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        super().save_permit()
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=3)
        self._wait_for_loader()
