import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.completeness_check_page import CompletenessCheckPage

def test_completeness_check_flow(authenticated_page, faker):
    """
    Verifies the complete Completeness Check tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Completeness Check tab and verify initial layout.
    3. Save completeness details.
    4. Generate letters (Completeness Letter, 1st Info, 30 Day Follow-up) and verify popup canvases.
    5. Attach a dummy PDF document and add a communication log to test shared Documents and Log.
    6. Generate a document package from the attachments.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    completeness_page = CompletenessCheckPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
    
    # Generate dynamic test values using Faker to avoid state conflict
    doc_subject = f"Auto Doc - {faker.word()}"
    doc_desc = f"Auto Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Comm - {faker.word()}"
    comm_desc = f"Auto Comm Description - {faker.sentence()}"
    
    # 2. Navigate to Listing, search, and enter Edit mode using the unified retry helper
    listing_page.search_and_edit_permit("HCL")
    
    # 3. Transition to Completeness Check tab and verify layout
    completeness_page.navigate_to_completeness_check()
    completeness_page.verify_initial_layout()
    
    # 4. Save completeness details
    completeness_page.save_completeness_details()
    
    # 5. Generate completeness letters and verify popups
    completeness_page.generate_letters_and_verify_popups()
    
    # 6. Test inherited/shared Documents and Log functionality
    completeness_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    completeness_page.add_communication(subject=comm_subject, description=comm_desc)
    
    # 7. Create Package
    completeness_page.create_package_and_verify()
