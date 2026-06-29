import pytest
from playwright.sync_api import Page
from pages.permit_transfer.add_permit_transfer_details_page import AddPermitTransferDetailsPage


class TestAddPermitTransfer:

    def test_add_permit_transfer_details_flow(self, authenticated_page: Page, faker):
        """
        Verifies the complete Add Permit Transfer Details workflow:
        1. Navigates to Permit Transfer Listing.
        2. Clicks Add Permit Transfer.
        3. Fills Permit Number '700912' and searches details.
        4. Searches Dealer 'vansh', selects it, and accepts popup.
        5. Fills out form description utilizing Faker.
        6. Saves and confirms popup.
        7. Clicks 'Find' on listing, searches and selects Dealer 'vansh'.
        8. Executes Search in grid and verifies results are displayed.
        """
        add_transfer_page = AddPermitTransferDetailsPage(authenticated_page)

        # 1. Navigate to Permit Transfer
        add_transfer_page.navigate_to_permit_transfer()

        # 2. Click Add Permit Transfer
        add_transfer_page.click_add_permit_transfer()

        # 3. Enter Permit Number
        add_transfer_page.search_transfer_details(permit_no="700912")

        # 4. Search and Select Dealer
        add_transfer_page.search_and_select_dealer(dealer_name="vansh")

        # 5. Fill Details Form using Faker content
        from_dealer_text = f"Faker Transfer Description: {faker.sentence()}"
        add_transfer_page.fill_details_form(from_text=from_dealer_text)

        # 6. Save and Confirm
        add_transfer_page.save_and_confirm()

        # 7. Find and Select Transfer Dealer on returned list view
        add_transfer_page.find_and_select_transfer_dealer(dealer_name="vansh")

        # 8. Trigger grid search and verify output
        add_transfer_page.execute_grid_search()
