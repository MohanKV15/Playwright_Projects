import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.inspection_page import InspectionPage

def test_inspection_flow(authenticated_page, faker):
    """
    Verifies the complete Inspection tab workflow:
    1. Search for permit by company "HCL" and open the first record in Edit mode.
    2. Transition to Inspection tab and verify initial layout.
    3. Fill out Inspection form details, select dropdown options, set dates, enter dynamic comments using Faker, and Save.
    4. Trigger report generation popups gracefully.
    5. Add and edit Inspection Review entry.
    6. Verify that the Documents and Log section becomes visible.
    7. Attach a dummy PDF document and add a communication log entry.
    8. Generate a document package from the attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    inspection_page = InspectionPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
        
    # Generate dynamic test data using Faker
    comments_text = f"Auto Inspection Comment - {faker.sentence()}"
    review_comments = f"Auto Inspection Review - {faker.sentence()}"
    doc_subject = f"Auto Inspection Doc - {faker.word()}"
    doc_desc = f"Auto Inspection Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Inspection Comm - {faker.word()}"
    comm_desc = f"Auto Inspection Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Inspection tab and verify initial layout
    inspection_page.navigate_to_inspection()
    inspection_page.verify_initial_layout()

    # 4. Fill and save Inspection details
    inspection_page.fill_inspection_details(comments=comments_text)

    # 5. Generate Inspection reports
    inspection_page.generate_inspection_reports()

    # 6. Add and edit Inspection Review
    inspection_page.add_inspection_review(comments=review_comments)

    # 7. Perform Documents & Log integration test (attach document, add communication)
    inspection_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    inspection_page.add_communication(subject=comm_subject, description=comm_desc)

    # 8. Create document package and verify success
    inspection_page.create_package_and_verify()
