import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.Appeal_page import AppealPage

def test_appeal_flow(authenticated_page, faker):
    """
    Verifies the complete Appeal tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Appeal tab and verify initial layout.
    3. Fill out the Appeal form fields, select dates, enter comments, and click Save.
    4. Verify that the Documents and Log section becomes visible.
    5. Attach a dummy PDF document and add a communication log entry.
    6. Generate a document package from the attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    appeal_page = AppealPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
        
    # Generate dynamic test data using Faker
    comments_text = f"Auto Appeal Comment - {faker.sentence()}"
    doc_subject = f"Auto Appeal Doc - {faker.word()}"
    doc_desc = f"Auto Appeal Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Appeal Comm - {faker.word()}"
    comm_desc = f"Auto Appeal Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Appeal tab and verify initial layout
    appeal_page.navigate_to_appeal()
    appeal_page.verify_initial_layout()

    # 4. Fill and save Appeal details
    appeal_page.fill_appeal_details(comments=comments_text)

    # 5. Perform Documents & Log integration test (attach document, add communication)
    appeal_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    appeal_page.add_communication(subject=comm_subject, description=comm_desc)

    # 6. Create document package and verify success
    appeal_page.create_package_and_verify()
