import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.generate_documents_page import GenerateDocumentsPage


def test_generate_documents_flow(authenticated_page, faker):
    """
    Verifies the complete Generate Documents / Generate Forms tab workflow per codegen steps:
    1. Search for permit by company "HCL" and open the first record in Edit mode.
    2. Transition to Generate Documents tab and verify initial layout headers.
    3. Click generate form button, expect popup, and verify #mainCanvas report viewer is visible in popup.
    4. Validate that 'Last Date Generated' column in grid updates and displays present day date.
    5. Click second generate form button, expect popup, and verify #mainCanvas report viewer is visible in popup.
    6. Perform Documents & Log integration test (attach document, add communication).
    7. Generate a document package from attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    gen_doc_page = GenerateDocumentsPage(authenticated_page)

    # Define file paths for attachments
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    # Generate dynamic test data using Faker
    doc_subject = f"Auto GenDoc Doc - {faker.word()}"
    doc_desc = f"Auto GenDoc Doc Description - {faker.sentence()}"
    comm_subject = f"Auto GenDoc Comm - {faker.word()}"
    comm_desc = f"Auto GenDoc Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Generate Documents tab and verify initial layout
    gen_doc_page.navigate_to_generate_documents()
    gen_doc_page.verify_initial_layout()

    # 4. Generate first form and verify #mainCanvas in popup window
    popup1 = gen_doc_page.generate_form_and_verify_popup()
    popup1.close()

    # 5. Verify 'Last Date Generated' column displays present day date
    gen_doc_page.verify_last_date_generated()

    # 6. Generate second form and verify #mainCanvas in second popup window
    popup2 = gen_doc_page.generate_second_form_and_verify_popup()
    popup2.close()

    # 7. Perform Documents & Log integration test (attach document, add communication)
    gen_doc_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    gen_doc_page.add_communication(subject=comm_subject, description=comm_desc)

    # 8. Create document package and verify success
    gen_doc_page.create_package_and_verify()
