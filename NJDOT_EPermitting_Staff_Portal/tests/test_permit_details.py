import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.permit_details_page import PermitDetailsPage

def test_permit_details_flow(authenticated_page, faker):
    """
    Verifies the complete Permit Details tab workflow:
    1. Search for permit by company "HCL" and open the first record in Edit mode.
    2. Transition to Permit Details tab and verify initial layout.
    3. Fill out Permit Details form fields, select dropdown options, set dates, enter dynamic comments, and Save.
    4. Verify that the Documents and Log section becomes visible.
    5. Attach a dummy PDF document and add a communication log entry.
    6. Generate a document package from the attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    permit_details_page = PermitDetailsPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
        
    # Generate dynamic test data using Faker
    comments_text = f"Auto Permit Details Comment - {faker.sentence()}"
    doc_subject = f"Auto Permit Doc - {faker.word()}"
    doc_desc = f"Auto Permit Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Permit Comm - {faker.word()}"
    comm_desc = f"Auto Permit Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Permit Details tab and verify initial layout
    permit_details_page.navigate_to_permit_details()
    permit_details_page.verify_initial_layout()

    # 4. Fill and save Permit Details form
    permit_details_page.fill_permit_details(comments=comments_text)

    # 5. Perform Documents & Log integration test (attach document, add communication)
    permit_details_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    permit_details_page.add_communication(subject=comm_subject, description=comm_desc)

    # 6. Create document package and verify success
    permit_details_page.create_package_and_verify()
