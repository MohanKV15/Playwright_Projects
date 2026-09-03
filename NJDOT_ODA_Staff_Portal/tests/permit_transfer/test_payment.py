import pytest
from playwright.sync_api import Page
from pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage
from pages.permit_transfer.payment_page import PermitTransferPaymentPage


class TestPermitTransferPayment:

    def test_permit_transfer_payment_flow(self, authenticated_page: Page, faker):
        """
        Verifies the Permit Transfer Payment workflow:
        1. Navigates to Permit Transfer Listing and opens record '700912' for dealer 'vansh'.
        2. Navigates to the Payments tab.
        3. Clicks 'Add Paper Check' to open details form.
        4. Fills out check and refund details utilizing Faker.
        5. Saves check and asserts returned listing grid container.
        """
        details_page = PermitTransferDetailsPage(authenticated_page)
        payment_page = PermitTransferPaymentPage(authenticated_page)

        # 1. Navigate and open Permit Transfer Details
        details_page.navigate_to_permit_transfer()
        details_page.search_permit_transfer(permit_number="700912", from_dealer_name="vansh")

        # 2. Transition to Payments tab
        payment_page.navigate_to_payments()

        # 3. Click Add Paper Check
        payment_page.click_add_paper_check()

        # 4. Fill form details using Faker
        check_no = f"PTCHK-{faker.random_int(1000, 9999)}"
        comments = f"Automated Check Comments: {faker.word()}"
        payable = faker.company()
        refund_no = str(faker.random_int(10, 99))
        
        payment_page.fill_payment_details(
            check_number=check_no,
            comments=comments,
            payable_to=payable,
            refund_check_number=refund_no
        )

        # 5. Save and verify grid container
        payment_page.save_payment()
