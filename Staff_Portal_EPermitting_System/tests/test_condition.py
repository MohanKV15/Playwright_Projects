import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.condition_page import ConditionPage

def test_condition_flow(authenticated_page, faker):
    """
    Verifies the complete Conditions tab workflow:
    1. Search for permit by company "HCL" and open the first record in Edit mode.
    2. Transition to Conditions tab and verify initial layout.
    3. Interact with radio options, validate grid, perform pagination navigation.
    4. Verify that the Documents and Log section becomes visible.
    5. Attach a dummy PDF document and add a communication log entry.
    6. Generate a document package from the attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    condition_page = ConditionPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
        
    # Generate dynamic test data using Faker
    doc_subject = f"Auto Condition Doc - {faker.word()}"
    doc_desc = f"Auto Condition Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Condition Comm - {faker.word()}"
    comm_desc = f"Auto Condition Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Conditions tab and verify initial layout
    condition_page.navigate_to_conditions()
    condition_page.verify_initial_layout()

    # 4. Interact with Conditions radio options, grid, and pagination
    condition_page.fill_condition_details()

    # 5. Perform Documents & Log integration test (attach document, add communication)
    condition_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    condition_page.add_communication(subject=comm_subject, description=comm_desc)

    # 6. Create document package and verify success
    condition_page.create_package_and_verify()
