import pytest
from playwright.sync_api import Page
from pages.violations.appeals_page import ViolationAppealsPage


class TestViolationAppeal:

    def test_violation_appeal_flow(self, authenticated_page: Page):
        """
        Verifies the complete Violation Appeal workflow:
        1. Navigates to Violations Listing.
        2. Searches by dealer name 'vansh'.
        3. Edits the first matching record.
        4. Navigates to the Appeals tab.
        5. Fills the appeal details using Faker and the current date.
        6. Saves the appeal.
        """
        appeal_page = ViolationAppealsPage(authenticated_page)

        # 1. Navigate to Violations Listing
        appeal_page.navigate_to_violations_listing()

        # 2. Search by dealer name 'vansh'
        appeal_page.search_by_dealer_name(dealer_name="vansh")

        # 3. Edit first record
        appeal_page.click_edit_on_first_record()

        # 4. Navigate to Appeals tab
        appeal_page.navigate_to_appeals()

        # 5. Fill appeal details (assignee "Andrew Feller", default Faker comments, current dates)
        appeal_page.fill_appeal_details(assignee_name="Andrew Feller")

        # 6. Save the appeal form (double-save action)
        appeal_page.save_appeal()
