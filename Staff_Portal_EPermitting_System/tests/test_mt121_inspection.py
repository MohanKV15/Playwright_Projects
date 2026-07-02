import pytest
import os
from playwright.sync_api import expect
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.mt_121_page import MT121Page

def test_mt121_inspection_flow(authenticated_page, faker):
    """
    Verifies the complete MT-121 Inspection Report workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to MT-121 Inspection tab and verify initial layout.
    3. Fill out the report form (dates, times, dropdowns, checks, radio options).
    4. Save the inspection report and click OK on validation.
    5. Generate the Inspection Report and verify the popup canvas.
    6. Attach a dummy document and add communication log to test shared Documents and Log.
    7. Generate a document package from the attachments.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    mt121_page = MT121Page(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
    
    # Generate dynamic test values using Faker to avoid state conflict
    doc_subject = f"Auto Doc - {faker.word()}"
    doc_desc = f"Auto Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Comm - {faker.word()}"
    comm_desc = f"Auto Comm Description - {faker.sentence()}"
    
    # 2. Search and Edit permit by company "HCL"
    listing_page.search_and_edit_permit("HCL")
    
    # 3. Navigate to MT-121 tab and verify initial layout
    mt121_page.navigate_to_mt121()
    mt121_page.verify_initial_layout()
    
    # 4. Fill and save the inspection report
    mt121_page.fill_inspection_report()
    mt121_page.save_inspection_report()
    
    # 5. Generate Inspection Report PDF and verify the popup canvas
    mt121_page.generate_inspection_report_pdf()
    
    # 6. Test inherited/shared Documents and Log functionality
    expect(mt121_page.documents_log_heading).to_be_visible(timeout=15000)
    expect(mt121_page.complete_log_status).to_be_visible(timeout=15000)
    mt121_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    mt121_page.add_communication(subject=comm_subject, description=comm_desc)
    
    # 7. Create Package
    mt121_page.create_package_and_verify()
