import pytest
import os
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.lot_Development_page import LotDevelopmentPage

def test_lot_development_flow(authenticated_page, faker):
    """
    Verifies the complete Lot Development and Frontages workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Lot Development/Frontages tab and verify layout.
    3. Add a new Land Use entry with randomized units.
    4. Add a Spacing entry with randomized dimensions.
    5. Attach a dummy PDF document and add a communication log.
    6. Generate a document package from the attachments.
    7. Trigger and cancel the email transmission.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    lot_dev_page = LotDevelopmentPage(authenticated_page)
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))
    
    # Generate dynamic test values using Faker
    units_val = str(faker.random_int(min=1, max=10))
    lot_size_val = str(faker.random_int(min=1, max=10))
    frontage_val = str(faker.random_int(min=1, max=10))
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

    # 3. Transition to Lot Development tab and verify initial layout
    lot_dev_page.navigate_to_lot_development()
    lot_dev_page.verify_initial_layout()

    # 4. Add Land Use Entry
    lot_dev_page.add_land_use(units=units_val)

    # 5. Add Spacing Entry
    lot_dev_page.add_spacing(size=lot_size_val, frontage=frontage_val)

    # 6. Attach Document & Add Communication Log
    lot_dev_page.attach_document(file_path=dummy_pdf_path, subject=doc_subject, description=doc_desc)
    lot_dev_page.add_communication(subject=comm_subject, description=comm_desc)

    # 7. Create Package
    lot_dev_page.create_package_and_verify()

    # 8. Send Email & Cancel
    lot_dev_page.send_email_and_verify()
