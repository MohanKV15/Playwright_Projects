import pytest
import datetime
from playwright.sync_api import Page
from pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage
from pages.permit_transfer.documents_and_log_page import PermitTransferDocumentsAndLogPage


from utils.config import Config


class TestPermitTransferDocumentsAndLog:

    def test_permit_transfer_documents_log_flow(self, authenticated_page: Page, faker):
        """
        Verifies the Permit Transfer Documents and Log workflow:
        1. Navigates to Permit Transfer Listing and opens record '700912' for dealer 'vansh'.
        2. Navigates to the Documents and Log tab.
        3. Uploads an attachment document (using dummy.pdf) filled with Faker values and the present day.
        4. Clicks 'Add Communication', enters subject and description with Faker values and the present day, and saves.
        5. Clicks 'Create Package' and verifies Select Attachments popup, then closes it.
        6. Clicks 'Send Email', verifies Cancel button, and cancels.
        """
        details_page = PermitTransferDetailsPage(authenticated_page)
        doc_log_page = PermitTransferDocumentsAndLogPage(authenticated_page)

        # Compute the present day dynamically
        present_day = str(datetime.datetime.now().day)

        # 1. Navigate and open Permit Transfer Details
        details_page.navigate_to_permit_transfer()
        details_page.search_permit_transfer(permit_number="700912", from_dealer_name="vansh")

        # 2. Transition to Documents and Log tab
        doc_log_page.navigate_to_documents_log()

        # 3. Attach a document using Faker values and present day
        dummy_pdf_path = str(Config.PROJECT_ROOT / "testdata" / "dummy.pdf")
        doc_title = f"Doc {faker.word().capitalize()} Test"
        doc_desc = f"Automated upload description: {faker.sentence()}"
        doc_log_page.attach_document(
            file_path=dummy_pdf_path,
            title=doc_title,
            desc=doc_desc,
            date_day=present_day
        )

        # 4. Add a new communication log entry using Faker values and present day
        comm_subject = f"Comm {faker.word().capitalize()} Subject"
        comm_desc = f"Automated communication details: {faker.paragraph(nb_sentences=2)}"
        doc_log_page.add_communication(
            subject=comm_subject,
            description=comm_desc,
            date_day=present_day
        )

        # 5. Create package and verify the modal overlays, then close
        doc_log_page.verify_and_close_package_modal()

        # 6. Send email and click cancel
        doc_log_page.verify_send_email_and_cancel()
