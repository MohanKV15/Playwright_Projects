import os
import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.log_page import LogPage
from pages.document_page import DocumentPage


def test_log_flow(authenticated_page, faker):
    """
    Verifies the complete Log menu workflow:
    1. Search for permit by company "HCL" and open in Edit mode.
    2. Click Log menu item in Application/Permit Info sidebar.
    3. Verify Documents and Log header & grid layout.
    4. Attach document, add communication entry, and create package.
    """
    listing_page = PermitListingPage(authenticated_page)
    log_page = LogPage(authenticated_page)
    doc_page = DocumentPage(authenticated_page)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    doc_subject = f"Auto Log Doc - {faker.word()}"
    doc_desc = f"Auto Log Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Log Comm - {faker.word()}"
    comm_desc = f"Auto Log Comm Description - {faker.sentence()}"

    # Search and open permit
    listing_page.search_and_edit_permit("HCL")

    # Navigate to Log and verify layout
    log_page.navigate_to_log()
    log_page.verify_initial_layout()

    # Perform Document & Log actions
    doc_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    log_page.add_communication(subject=comm_subject, description=comm_desc)
    doc_page.create_package_and_verify()
