import pytest
from playwright.sync_api import Page
from pages.license.customer_action_items_page import LicenseCustomerActionItemsPage


class TestLicenseCustomerActionItems:

    def test_add_customer_action_item_flow(self, authenticated_page: Page):
        """Verify adding a Customer Action Item, filling values with Faker, and verifying record displays in grid."""
        comm_page = LicenseCustomerActionItemsPage(authenticated_page)

        # 1. Navigate to License Listing
        comm_page.navigate_to_license_listing()

        # 2. Search for dealer "vansh" and edit the first matching row
        comm_page.search_and_edit_first_license(dealer_name="vansh")

        # 3. Navigate to Customer Action Items tab
        comm_page.navigate_to_customer_action_items()

        # 4. Click Add New
        comm_page.click_add_new()

        # 5. Populate details using Faker internally in POM (Option: "License Fee", Status: "Requested", Reviewer: "Charles Craddock")
        comm_page.fill_communication_details(
            option="License Fee",
            status="Requested",
            reviewer="Charles Craddock"
        )

        # 6. Click Save
        comm_page.click_save()

        # 7. Verify that the added communication message shows up in the results grid
        comm_page.verify_communication_record_in_grid("License Fee", "Requested")
