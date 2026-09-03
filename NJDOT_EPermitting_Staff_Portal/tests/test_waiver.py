import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.waiver_page import WaiverPage


def test_waiver_flow(authenticated_page, faker):
    """
    Verifies the complete Waiver tab workflow per codegen steps:
    1. Search for permit by company "HCL" and open the first record in Edit mode.
    2. Transition to Waiver tab and verify initial layout headers and grid container.
    3. Click 'Add New' to open Waiver Details form.
    4. Fill out text placeholder and comment placeholder fields.
    5. Save waiver form and verify grid container updates.
    6. Click '#editWaiver', verify partial form, and click Save.
    7. Perform Documents & Log integration test (attach document, add communication).
    8. Generate a document package from attachments and verify success.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    waiver_page = WaiverPage(authenticated_page)

    # Define file paths for attachments
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "testdata", "dummy.pdf"))
    if not os.path.exists(dummy_pdf_path):
        dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    # Generate dynamic test data using Faker
    text_data = f"Auto Waiver Text - {faker.word()}"
    comment_data = f"Auto Waiver Comment - {faker.sentence()}"
    doc_subject = f"Auto Waiver Doc - {faker.word()}"
    doc_desc = f"Auto Waiver Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Waiver Comm - {faker.word()}"
    comm_desc = f"Auto Waiver Comm Description - {faker.sentence()}"

    # 2. Navigate to Listing, search by company "HCL", and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Waiver tab and verify initial layout
    waiver_page.navigate_to_waiver()
    waiver_page.verify_initial_layout()

    # 4. Click 'Add New' to open Waiver Details form
    waiver_page.click_add_new_waiver()

    # 5. Fill out form and save
    waiver_page.fill_waiver_details(text_val=text_data, comment_val=comment_data)
    waiver_page.save_waiver()

    # 6. Edit Waiver and save changes
    waiver_page.edit_waiver()

    # 7. Perform Documents & Log integration test (attach document, add communication)
    waiver_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    waiver_page.add_communication(subject=comm_subject, description=comm_desc)

    # 8. Create document package and verify success
    waiver_page.create_package_and_verify()
