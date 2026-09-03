import pytest
from playwright.sync_api import Page
from pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage


class TestPermitTransfer:

    def test_permit_transfer_flow(self, authenticated_page: Page):
        """
        Verifies the complete Permit Transfer workflow:
        1. Navigates to the Permit Transfer tab.
        2. Searches by Permit Number "700912" and From Dealer Name "vansh".
        3. Verifies that all expected headers, dividers, and sections are visible.
        4. Saves and confirms the transaction popup.
        """
        permit_transfer_page = PermitTransferDetailsPage(authenticated_page)

        # 1. Navigate to the Permit Transfer tab
        permit_transfer_page.navigate_to_permit_transfer()

        # 2. Search using permit number and dealer name
        permit_transfer_page.search_permit_transfer(permit_number="700912", from_dealer_name="vansh")

        # 3. Verify page headings and form partitions
        permit_transfer_page.verify_layout()

        # 4. Click Save and accept the confirmation popup
        permit_transfer_page.save_and_confirm()
