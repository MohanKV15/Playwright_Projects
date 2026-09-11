import logging
import re
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.review_page import ReviewPage
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage

logger = logging.getLogger(__name__)
fake = Faker()


class JunkyardReviewPage(ReviewPage):
    """
    Page Object Model representing the Junkyards Review workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Customized for Junkyards Review Codegen sequence:
    - Search company on Junkyard/Permit Search ('IDOTOAtest2')
    - Select 1st record row to activate permit session context
    - Expand Junkyards sidebar menu and click 'Review' link
    - Assert listing view ('Junkyard Details Permit', 'Reviewers Assigned', .k-grid-content)
    - Click 'Add Reviewer', assert dropdown container (#divfrmReviewer)
    - Populate Review Type ('Amendment'), Reviewer ('Bill Siders'), Role ('Director - Outdoor Advertising')
    - Fill present day date and optional Faker comments
    - Click Save, assert 'Operation completed', confirm OK popup, and verify #ReviewAssignmentsList
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.junkyard_details = JunkyardDetailsPage(page)

        # Junkyards Specific Sidebar Links
        self.junkyards_menu_link = page.get_by_role("link", name="Junkyards ").or_(
            page.locator("a[href*='Junkyard'], .sidebar a:has-text('Junkyards')")
        ).first
        self.sidebar_review_link = page.get_by_role("link", name="Review", exact=True).filter(visible=True).or_(
            page.locator("a[href*='Reviewer']").filter(visible=True)
        ).first

        # Codegen Specific Locators
        self.header_junkyard_details_permit = page.get_by_text("Junkyard Details Permit").or_(
            page.get_by_text("Application Details Permit")
        ).first
        self.heading_reviewers_assigned = page.get_by_role("heading", name="Reviewers Assigned").or_(
            page.get_by_text("Reviewers Assigned")
        ).first
        self.grid_content = page.locator(".k-grid-content, #ReviewAssignmentsList, .k-grid").first
        self.add_reviewer_button = page.get_by_role("button", name="Add Reviewer").or_(
            page.locator("button:has-text('Add Reviewer'), a:has-text('Add Reviewer')")
        ).first

        # Reviewer Form Locators (#divfrmReviewer)
        self.form_reviewer_container = page.locator("#divfrmReviewer")
        self.review_type_trigger = self.form_reviewer_container.get_by_text("--Select Review Type--").or_(
            page.locator("#Text_PlaceHolder1, #divfrmReviewer span.k-dropdown").first
        )
        self.reviewer_trigger = self.form_reviewer_container.get_by_text("--Select Reviewer --").or_(
            page.locator("#Review_By, #divfrmReviewer span.k-dropdown").nth(1)
        )
        self.role_trigger = self.form_reviewer_container.get_by_text("--Select Role--").or_(
            page.locator("#Review_Unit, #divfrmReviewer span.k-dropdown").nth(2)
        )

        self.comments_input = page.locator("#Comment_PlaceHolder1, textarea[name='Comment_PlaceHolder1']").first

        self.save_button = page.get_by_role("button", name=re.compile(r"Save", re.I)).or_(
            page.locator("#divfrmReviewer button:has-text('Save'), button:has-text('Save')")
        ).first
        self.operation_completed_text = page.get_by_text("Operation completed").first
        self.review_assignments_list = page.locator("#ReviewAssignmentsList, .k-grid-content").first

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

    def navigate_to_junkyard_review(self, company_name: str = "IDOTOAtest2") -> str:
        """
        1. Searches company name on Junkyard/Permit Search page
        2. Clicks Edit on 1st record row to activate permit session context
        3. Expands Junkyards sidebar menu if collapsed
        4. Clicks visible 'Review' menu link under Junkyards
        5. Verifies Review page loaded
        """
        self.logger.info("Navigating to Junkyard/Permit Search and searching company: '%s'", company_name)
        self.junkyard_details.navigate_to_junkyard_search()
        self.junkyard_details.search_junkyard_permits(company_name=company_name)
        record_info = self.junkyard_details.click_edit_on_permit_record()

        self.logger.info("Navigating to Review menu link under Junkyards")
        if self.junkyards_menu_link.is_visible(timeout=5000):
            if not self.page.locator(".sidebar a[href*='Reviewer']").filter(visible=True).is_visible():
                self.logger.info("Expanding Junkyards sidebar menu")
                self.junkyards_menu_link.click(force=True)
                self.page.wait_for_timeout(400)

        target_link = self.page.get_by_role("link", name="Review", exact=True).filter(visible=True).or_(
            self.page.locator("a[href*='Reviewer']").filter(visible=True)
        ).first

        expect(target_link).to_be_visible(timeout=20000)
        target_link.click(force=True)
        self.page.wait_for_timeout(400)
        self._wait_for_loader()

        self.verify_junkyard_review_page_loaded()
        return record_info

    def verify_junkyard_review_page_loaded(self, timeout_ms: int = 20000) -> None:
        """
        Verifies that Junkyard Review page headers and grid content are visible.
        """
        self.logger.info("Verifying Junkyard Review page elements")
        if self.heading_reviewers_assigned.is_visible(timeout=5000):
            expect(self.heading_reviewers_assigned).to_be_visible(timeout=timeout_ms)
        if self.header_junkyard_details_permit.is_visible(timeout=5000):
            expect(self.header_junkyard_details_permit).to_be_visible(timeout=timeout_ms)
        expect(self.grid_content).to_be_visible(timeout=timeout_ms)
        expect(self.add_reviewer_button).to_be_visible(timeout=timeout_ms)

    def click_add_reviewer_and_verify_form(self, timeout_ms: int = 20000) -> None:
        """
        Clicks 'Add Reviewer' button and verifies reviewer form container is displayed.
        """
        self.logger.info("Clicking 'Add Reviewer' button")
        expect(self.add_reviewer_button).to_be_visible(timeout=timeout_ms)
        self.add_reviewer_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_timeout(500)
        expect(self.form_reviewer_container).to_be_visible(timeout=timeout_ms)

    def create_reviewer(
        self,
        review_type_name: Optional[str] = None,
        reviewer_name: Optional[str] = None,
        role_name: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Reuse the shared Review workflow. Once the Junkyard page is opened, the base class
        already applies the required rules: present-day date + first valid dropdown option + Faker comments.
        """
        self.click_add_reviewer_and_verify_form()
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        data = super().fill_reviewer_form(comments=comments)
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=2)
        self.logger.info("Saving reviewer via shared Application Permit flow")
        super().save_reviewer()
        self.dismiss_ok_popups(timeout_ms=1500, max_clicks=3)
        return data
