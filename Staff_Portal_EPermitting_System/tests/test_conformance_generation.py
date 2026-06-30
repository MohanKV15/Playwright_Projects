import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.conformance_generation_page import ConformanceGenerationPage

def test_conformance_generation_flow(authenticated_page, faker):
    """
    Verifies the complete Conformance/Trip Generation workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Conformance/Trip Generation tab and verify layout.
    3. Run Conformance and accept the warning dialog.
    4. Attach a dummy PDF document and add a communication log.
    5. Generate a document package from the attachments.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    conformance_page = ConformanceGenerationPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
    
    # Generate dynamic test values using Faker
    doc_subject = f"Auto Doc - {faker.word()}"
    doc_desc = f"Auto Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Comm - {faker.word()}"
    comm_desc = f"Auto Comm Description - {faker.sentence()}"

    # 2. Search for company "HCL" and open the record in Edit mode
    max_retries = 3
    for attempt in range(max_retries):
        try:
            listing_page.navigate_to_permit_listing()
            listing_page.search_by_company("HCL")
            listing_page.navigate_to_next_page_and_edit_first_record()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"\n[RETRY] Search/Edit failed: {e}. Retrying attempt {attempt + 1}/{max_retries}...")
            authenticated_page.wait_for_timeout(5000)

    # 3. Transition to Conformance/Trip Generation tab and verify initial layout
    conformance_page.navigate_to_conformance()
    conformance_page.verify_initial_layout()

    # 4. Run Conformance
    conformance_page.run_conformance_and_verify()

    # 5. Attach Document & Add Communication Log
    conformance_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    conformance_page.add_communication(subject=comm_subject, description=comm_desc)

    # 6. Create Package & Verify final layout
    conformance_page.create_package_and_verify()
