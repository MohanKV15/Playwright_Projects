import pytest
from playwright.sync_api import Page
from pages.violations.customer_action_items_page import ViolationCustomerActionItemsPage


class TestViolationCustomerActionItems:

    def test_add_customer_communication_flow(self, authenticated_page: Page):
        """
        Verifies the complete Customer Action Items workflow for a Violation:
        1. Navigates to Violations Listing.
        2. Filters by dealer name 'vansh'.
        3. Edits the first matching record.
        4. Navigates to the 'Customer Action Items' tab.
        5. Clicks 'Add New' to open the details form.
        6. Fills the form details (always choosing 1st visible dropdown options and using Faker).
        7. Saves and verifies redirection back to grid listing successfully.
        """
        action_page = ViolationCustomerActionItemsPage(authenticated_page)

        # 1. Navigate to Violations Listing
        action_page.navigate_to_violations_listing()

        # 2. Search by dealer name 'vansh'
        action_page.search_by_dealer_name(dealer_name="vansh")

        # 3. Edit first record
        action_page.click_edit_on_first_record()

        # 4. Navigate to Customer Action Items
        action_page.navigate_to_customer_action_items()

        # 5. Click Add New
        action_page.click_add_new()

        # 6. Fill communication form
        action_page.fill_communication_details()

        # 7. Save communication
        action_page.save_communication()
