import pytest
from playwright.sync_api import Page
from pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage
from pages.permit_transfer.customer_action_items_page import PermitTransferCustomerActionItemsPage


class TestPermitTransferCustomerActionItems:

    def test_permit_transfer_customer_action_items_flow(self, authenticated_page: Page, faker):
        """
        Verifies the Permit Transfer Customer Action Items workflow:
        1. Navigates to Permit Transfer Listing and opens record '700912' for dealer 'vansh'.
        2. Navigates to the Customer Action Items tab.
        3. Clicks 'Add New' to open communications form.
        4. Fills details (dropdown triggers, Faker messages).
        5. Saves record and verifies returned grid listing.
        """
        details_page = PermitTransferDetailsPage(authenticated_page)
        action_page = PermitTransferCustomerActionItemsPage(authenticated_page)

        # 1. Navigate and open Permit Transfer Details
        details_page.navigate_to_permit_transfer()
        details_page.search_permit_transfer(permit_number="700912", from_dealer_name="vansh")

        # 2. Transition to Customer Action Items
        action_page.navigate_to_customer_action_items()

        # 3. Click Add New
        action_page.click_add_new()

        # 4. Fill communications using Faker
        message = f"Automated Communication: {faker.paragraph(nb_sentences=1)}"
        action_page.fill_communication_details(message=message)

        # 5. Save and confirm
        action_page.save_communication()
