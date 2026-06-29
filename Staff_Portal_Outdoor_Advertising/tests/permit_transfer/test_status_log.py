import pytest
from playwright.sync_api import Page
from pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage
from pages.permit_transfer.status_log_page import PermitTransferStatusLogPage


class TestPermitTransferStatusLog:

    def test_permit_transfer_status_log_flow(self, authenticated_page: Page):
        """
        Verifies the Permit Transfer Status Log workflow:
        1. Navigates to Permit Transfer Listing and opens record '700912' for dealer 'vansh'.
        2. Navigates to the Status Log tab and asserts layout elements.
        3. Navigates to the Documents and Log tab.
        """
        details_page = PermitTransferDetailsPage(authenticated_page)
        log_page = PermitTransferStatusLogPage(authenticated_page)

        # 1. Navigate and open Permit Transfer Details
        details_page.navigate_to_permit_transfer()
        details_page.search_permit_transfer(permit_number="700912", from_dealer_name="vansh")

        # 2. Transition to Status Log tab
        log_page.navigate_to_status_log()

        # 3. Transition to Documents and Log tab
        log_page.navigate_to_documents_log()
