import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class TechnicalReviewPage(BasePage):
    """
    Page Object Model for the Technical Review tab within the Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Tab Navigation & Sidebar ────────────────────────────────────────
        self.tech_review_tab = page.get_by_role("link", name="Technical Review")

        # ── Page Header & Heading Elements ──────────────────────────────────
        self.log_app_header = page.locator("#LogAppHeader")
        self.reviewers_assigned_heading = page.get_by_role("heading", name="Reviewers Assigned")
        self.tech_review_heading = page.get_by_role("heading", name="Technical Review")
        self.review_comments_heading = page.get_by_role("heading", name="Review Comments")

        # ── Layout Containers & Status ──────────────────────────────────────
        self.grid_content = page.locator(".k-grid-content")
        self.tech_review_save_cancel_text = page.get_by_text("Technical Review Save Cancel")
        self.comments_wrapper = page.locator("#partial-form > .form-wrapper > .row > .col-md-12").first

        # ── Actions & Buttons (Robust regex matching handles unicode icons) ────
        self.back_button = page.get_by_role("button", name=re.compile("Back", re.I))
        self.next_button = page.get_by_role("button", name=re.compile("Next", re.I))
        self.prev_button = page.get_by_role("button", name=re.compile("Previous", re.I))
        self.cancel_button = page.get_by_role("button", name=re.compile("Cancel", re.I))
        self.add_new_button = page.get_by_role("button", name=re.compile("Add New", re.I))
        self.save_button = page.get_by_role("button", name=re.compile("Save", re.I))
        self.ok_confirm_button = page.get_by_role("button", name="OK")

        # ── Dynamic Row Locators ────────────────────────────────────────────
        self.target_edit_row = page.get_by_role("row", name="2 09/09/2024 10/10/2024").locator("#editTechReview")
        self.fallback_edit_button = page.locator("#editTechReview").first

        # ── Documents and Log Section ───────────────────────────────────────
        self.documents_log_heading = page.get_by_role("heading", name="Documents and Log")
        self.complete_log_status = page.locator("#CompleteLog > div:nth-child(2)")
        self.complete_log_grid = page.locator("#LogDynGridLoad > #partial-form > .form-wrapper > .row > .col-md-12")

    # ── Actions ─────────────────────────────────────────────────────────────

    def click_back_button(self) -> None:
        """Clicks the Back button on the detail page to navigate back."""
        logger.info("Clicking the Back button.")
        self.back_button.wait_for(state="visible", timeout=15000)
        self.js_click(self.back_button)
        self._wait_for_loader()

    def navigate_to_technical_review(self) -> None:
        """Transitions to the Technical Review tab."""
        logger.info("Navigating to Technical Review tab.")
        self._wait_for_loader()
        self.js_click(self.tech_review_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_reviewers_layout(self) -> None:
        """Verifies headings and containers on the initial Reviewers Assigned view."""
        logger.info("Verifying Reviewers Assigned initial view layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.reviewers_assigned_heading).to_be_visible(timeout=15000)
        expect(self.grid_content).to_be_visible(timeout=15000)

    def navigate_wizard_steps(self, next_clicks: int = 4, prev_clicks: int = 2) -> None:
        """Clicks Next and Previous wizard buttons as specified."""
        logger.info(f"Navigating wizard: clicking Next {next_clicks} times, then Previous {prev_clicks} times.")
        
        for i in range(next_clicks):
            self.next_button.wait_for(state="visible", timeout=10000)
            logger.info(f"Clicking Next ({i + 1}/{next_clicks})")
            self.js_click(self.next_button)
            self._wait_for_loader()
            self.page.wait_for_timeout(500)

        for i in range(prev_clicks):
            self.prev_button.wait_for(state="visible", timeout=10000)
            logger.info(f"Clicking Previous ({i + 1}/{prev_clicks})")
            self.js_click(self.prev_button)
            self._wait_for_loader()
            self.page.wait_for_timeout(500)

    def edit_technical_reviewer(self) -> bool:
        """
        Attempts to click the target row edit button ('2 09/09/2024 10/10/2024').
        Falls back to the first available edit button if the specific target is not found.
        Returns True if an edit button was clicked, False otherwise.
        """
        self._wait_for_loader()
        if self.target_edit_row.count() > 0:
            logger.info("Found target row ('2 09/09/2024 10/10/2024'). Clicking edit.")
            self.js_click(self.target_edit_row)
            self._wait_for_loader()
            return True
        elif self.fallback_edit_button.count() > 0:
            logger.info("Target row not found. Clicking first available fallback edit button.")
            self.js_click(self.fallback_edit_button)
            self._wait_for_loader()
            return True
        else:
            logger.warning("No assigned reviewer edit buttons found.")
            return False

    def verify_technical_review_detail_layout(self) -> None:
        """Verifies headings, save/cancel buttons, comments, and Documents & Log area on details/edit page."""
        logger.info("Verifying Technical Review detail/edit page layout.")
        expect(self.log_app_header).to_be_visible(timeout=15000)
        expect(self.tech_review_save_cancel_text).to_be_visible(timeout=15000)
        expect(self.review_comments_heading).to_be_visible(timeout=15000)
        expect(self.comments_wrapper).to_be_visible(timeout=15000)
        expect(self.documents_log_heading).to_be_visible(timeout=15000)
        expect(self.complete_log_status).to_be_visible(timeout=15000)
        expect(self.complete_log_grid).to_be_visible(timeout=15000)

    def click_cancel(self) -> None:
        """Clicks the Cancel button."""
        logger.info("Clicking Cancel button.")
        self.cancel_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.cancel_button)
        self._wait_for_loader()

    def click_add_new(self) -> None:
        """Clicks the Add New button."""
        logger.info("Clicking Add New button.")
        self.add_new_button.wait_for(state="visible", timeout=10000)
        self.js_click(self.add_new_button)
        self._wait_for_loader()

    def verify_add_review_layout(self) -> None:
        """Verifies layout components on the Add New page."""
        logger.info("Verifying Add New layout.")
        expect(self.tech_review_heading).to_be_visible(timeout=15000)
        expect(self.comments_wrapper).to_be_visible(timeout=15000)

    def create_package_and_verify(self) -> None:
        """Overridden package creation helper with stability wait for Technical Review detail page."""
        logger.info("Creating package from attachments on Technical Review page.")
        self._wait_for_loader()
        self.page.wait_for_timeout(2000)
        self.js_click(self.create_package_button)
        expect(self.select_attachments_title).to_be_visible(timeout=20000)
        
        # Select first checkbox
        expect(self.first_attachment_checkbox).to_be_visible(timeout=10000)
        self.js_click(self.first_attachment_checkbox)
        
        # Select attachments button
        self.js_click(self.select_attachments_confirm_button)
        
        # Verify success message and click OK
        expect(self.package_created_message).to_be_visible(timeout=15000)
        self.js_click(self.ok_button)
        self._wait_for_loader()
        logger.info("Document package created and verified successfully on Technical Review.")
