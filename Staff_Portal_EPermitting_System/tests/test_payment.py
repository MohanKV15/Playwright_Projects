import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.payment_listing_page import PaymentListingPage


def test_payment_flow(authenticated_page, faker):
    """
    Verifies the complete Payments tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Click Payments menu and verify initial layout.
    3. Click 'Add New Payment', select 1st dropdown option for Payment Type, Method Of Payment,
       and Payment Sub Type, and populate Requested Amount (1 to 100) and Comments using Faker.
    4. Save payment details and verify 'Documents and Log' heading becomes visible.
    5. Attach a dummy PDF document and add a communication log entry.
    6. Generate a document package from the attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    payment_page = PaymentListingPage(authenticated_page)

    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    # Generate dynamic test data using Faker (Requested Amount between 1 and 100)
    amount_val = str(faker.random_int(min=1, max=100))
    comments_text = f"Auto Payment Comment - {faker.sentence()}"
    doc_subject = f"Auto Payment Doc - {faker.word()}"
    doc_desc = f"Auto Payment Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Payment Comm - {faker.word()}"
    comm_desc = f"Auto Payment Comm Description - {faker.sentence()}"

    # 2. Search permit by company "HCL" and open permit page
    listing_page.search_and_edit_permit("HCL")

    # 3. Click Payments menu link and verify initial layout
    payment_page.navigate_to_payments()
    payment_page.verify_initial_layout()

    # 4. Fill and save Payment details using 1st dropdown options and Faker data
    payment_page.add_payment_details(
        amount=amount_val,
        comments=comments_text
    )

    # 5. Continue flow: Attach document and add communication log
    payment_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    payment_page.add_communication(subject=comm_subject, description=comm_desc)

    # 6. Generate document package and verify success
    payment_page.create_package_and_verify()
