import logging
from datetime import datetime
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage
from IDOT_ODA_Staff_Portal.pages.core.kendo_controls import KendoDropdown, KendoDatePicker

logger = logging.getLogger(__name__)
fake = Faker()


class ReviewPage(BasePage):
    """
    Page Object Model representing the Review / Reviewers Assigned workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit context (delegated to ApplicationDetailsPage)
    - Navigate to Review page via sidebar menu link (ATSP4321Reviewer)
    - Verify page elements (Application Details Permit, Reviewers Assigned, .k-grid-content)
    - Click 'Add Reviewer'
    - Populate Date Assigned with present day date
    - Dynamically select the 1st valid option for Review Type, Reviewer, and Role
    - Populate Instructions/Comments with dynamic Faker text
    - Save reviewer form, verify 'Operation completed' confirmation, and click OK
    - Verify new reviewer appears in Reviewers Assigned grid table
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger
        self.kendo_dropdown = KendoDropdown(page)
        self.kendo_datepicker = KendoDatePicker(page)

        # 1. Navigation & Permit Context
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_review_link = page.locator(
            "a[href*='Reviewer'], .sidebar a:has-text('Review'), nav a:has-text('Review')"
        ).filter(visible=True).first

        # 2. Review Listing Elements (ATSP4321Reviewer)
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_reviewers_assigned = page.get_by_role("heading", name="Reviewers Assigned").first
        self.grid_content = page.locator(".k-grid-content").first
        self.add_reviewer_button = page.locator(
            "button:has-text('Add Reviewer'), a:has-text('Add Reviewer'), [role='button']:has-text('Add Reviewer')"
        ).first
        self.grid_rows = page.locator(".k-grid-content table tbody tr")

        # 3. Add Reviewer Form Elements (#divfrmReviewer)
        self.form_header_text = page.get_by_text("Assign Reviewer Date Assigned").first
        self.date_assigned_id = "Sent_tot_Review_Date"
        self.review_type_id = "#Text_PlaceHolder1"
        self.reviewer_id = "#Review_By"
        self.role_id = "#Review_Unit"
        self.comments_input = page.locator(
            "#Comment_PlaceHolder1, textarea[name='Comment_PlaceHolder1']"
        ).first

        # 4. Form Actions & Confirmation Dialogs
        self.save_button = page.locator("#divfrmReviewer #btnSubmit, #btnSubmit").first
        self.operation_completed_popup = page.get_by_text("Operation completed").first
        self.dialog_ok_button = page.locator(
            ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:has-text('OK')"
        ).first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification
    # -------------------------------------------------------------------------
    def navigate_to_review(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application session via company search and navigates to Review page.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        first_row = self.app_details.permit_grid_rows.first

        # Activate permit session by clicking action button on 1st record row
        action_btn = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_review_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Review")
        expect(self.sidebar_review_link).to_be_visible(timeout=15000)
        self.sidebar_review_link.click(force=True)
        self._wait_for_loader()

        self.page.wait_for_url("**/ATSP4321Reviewer**", timeout=20000)
        self.verify_review_page_loaded()

    def verify_review_page_loaded(self) -> None:
        """
        Verifies that Review page headers, grid content, and Add Reviewer button are visible.
        """
        self.logger.info("Verifying Review page elements are visible")
        expect(self.header_app_details_permit).to_be_visible(timeout=15000)
        expect(self.heading_reviewers_assigned).to_be_visible(timeout=15000)
        expect(self.grid_content).to_be_visible(timeout=15000)
        expect(self.add_reviewer_button).to_be_visible(timeout=15000)

    # -------------------------------------------------------------------------
    # Reviewer Form Interaction
    # -------------------------------------------------------------------------
    def click_add_reviewer(self) -> None:
        """
        Clicks 'Add Reviewer' button and asserts the assign reviewer form appears.
        """
        self.logger.info("Clicking 'Add Reviewer' button")
        self.add_reviewer_button.click(force=True)
        self._wait_for_loader()
        expect(self.form_header_text).to_be_visible(timeout=15000)

    def select_first_valid_dropdown_option(self, dropdown_locator_or_id: Union[Locator, str]) -> str:
        """
        Selects the first valid option dynamically from a Kendo DropDownList.
        """
        return self.kendo_dropdown.select_first_valid_option(dropdown_locator_or_id)

    def select_present_day_date(self) -> str:
        """
        Sets the present day date in the Date Assigned field using KendoDatePicker.
        """
        today_str = datetime.now().strftime("%m/%d/%Y")
        self.logger.info("Selecting present day date: %s", today_str)
        return self.kendo_datepicker.select_present_day_date(field_id=self.date_assigned_id)

    def fill_reviewer_form(self, comments: Optional[str] = None) -> Dict[str, str]:
        """
        Fills the Assign Reviewer form:
        - Sets Date Assigned to present day date
        - Dynamically selects 1st valid option for Review Type
        - Dynamically selects 1st valid option for Reviewer
        - Dynamically selects 1st valid option for Role
        - Fills Instructions/Comments using dynamic Faker text
        Returns dictionary of populated values.
        """
        # 1. Date Assigned
        selected_date = self.select_present_day_date()

        # 2. Dropdown selections (1st valid option)
        review_type = self.select_first_valid_dropdown_option(self.review_type_id)
        self.logger.info("Selected 1st Review Type: %s", review_type)

        reviewer = self.select_first_valid_dropdown_option(self.reviewer_id)
        self.logger.info("Selected 1st Reviewer: %s", reviewer)

        role = self.select_first_valid_dropdown_option(self.role_id)
        self.logger.info("Selected 1st Role: %s", role)

        # 3. Instructions/Comments
        generated_comment = comments or f"Review Instructions: {fake.sentence(nb_words=6)}"
        self.logger.info("Populating Instructions/Comments: %s", generated_comment)
        self.comments_input.wait_for(state="visible", timeout=10000)
        self.comments_input.fill(generated_comment)

        return {
            "date": selected_date,
            "review_type": review_type,
            "reviewer": reviewer,
            "role": role,
            "comments": generated_comment,
        }

    def save_reviewer(self) -> None:
        """
        Clicks Save button, confirms 'Operation completed' modal dialog, and clicks OK.
        """
        self.logger.info("Clicking Save button on Reviewer form")
        self.save_button.click(force=True)
        self._wait_for_loader()

        self.logger.info("Verifying 'Operation completed' confirmation dialog")
        expect(self.operation_completed_popup).to_be_visible(timeout=15000)

        self.logger.info("Dismissing confirmation dialog by clicking OK")
        self.dialog_ok_button.click(force=True)
        self._wait_for_loader()

    def create_reviewer(self, comments: Optional[str] = None) -> Dict[str, str]:
        """
        High-level workflow:
        1. Clicks 'Add Reviewer'
        2. Populates form fields (present day date, 1st dropdown options, Faker comments)
        3. Saves form and confirms completion dialog
        Returns the data dictionary of assigned reviewer.
        """
        self.click_add_reviewer()
        data = self.fill_reviewer_form(comments=comments)
        self.save_reviewer()
        return data

    # -------------------------------------------------------------------------
    # Verification in Grid Table
    # -------------------------------------------------------------------------
    def verify_reviewer_in_grid(
        self,
        expected_reviewer: Optional[str] = None,
        expected_role: Optional[str] = None,
    ) -> Locator:
        """
        Verifies that the assigned reviewer appears in the Reviewers Assigned grid table.
        Returns the matching row locator.
        """
        self.logger.info("Verifying reviewer record in Reviewers Assigned grid")
        expect(self.grid_rows.first).to_be_visible(timeout=20000)

        rows = self.grid_rows
        if expected_reviewer:
            rows = rows.filter(has_text=expected_reviewer)
        if expected_role:
            rows = rows.filter(has_text=expected_role)

        expect(rows.first).to_be_visible(timeout=20000)
        matching_row = rows.last
        self.logger.info("Found matching reviewer row: %s", matching_row.inner_text().strip())
        return matching_row
