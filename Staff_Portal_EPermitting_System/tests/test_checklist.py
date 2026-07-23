import os
import pytest
from playwright.sync_api import expect
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.checklist_page import ChecklistPage


def test_checklist_flow(authenticated_page, faker):
    """
    Verifies the complete Checklist tab workflow:

    1.  Search for permit by company "HCL" and open the first matching record.
    2.  Navigate to the Checklist tab and verify the initial page layout.
    3.  Open the first condition row in the Non-Other grid and click Update.
    4.  Paginate the Non-Other conditions grid forward (up to 2 pages).
    5.  Select the Optional condition radio (div:nth-child(2)) and verify the optional grid appears.
    6.  Paginate the Optional conditions grid forward (up to 2 pages).
    7.  Verify the Documents and Log section is visible.
    8.  Attach a document to the Documents and Log section.
    9.  Add a communication log entry.
    10. Create a document package from existing attachments and verify success.
    """
    # ── 1. Initialise Page Objects ──────────────────────────────────────────
    listing_page  = PermitListingPage(authenticated_page)
    checklist_page = ChecklistPage(authenticated_page)

    # Dynamic test data via Faker to avoid conflicts between test runs
    current_dir    = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    doc_subject  = f"Auto Doc - {faker.word()}"
    doc_desc     = f"Auto Doc Description - {faker.sentence()}"
    comm_subject = f"Auto Comm - {faker.word()}"
    comm_desc    = f"Auto Comm Description - {faker.sentence()}"

    # ── 2. Search for permit and enter Edit mode ────────────────────────────
    listing_page.search_and_edit_permit("HCL")

    # ── 3. Navigate to Checklist tab and verify layout ──────────────────────
    checklist_page.navigate_to_checklist()
    checklist_page.verify_initial_layout()

    # ── 4. Interact with the first Non-Other condition row ──────────────────
    checklist_page.open_first_condition_row()
    checklist_page.click_update()

    # ── 5. Paginate Non-Other conditions grid forward (up to 2 pages) ──────────────
    checklist_page.paginate_non_other_to_last_page()

    # ── 6. Switch to Optional conditions and verify grid ───────────────────
    checklist_page.select_optional_condition_radio()

    # ── 7. Paginate Optional conditions grid forward (up to 2 pages) ───────────────
    checklist_page.paginate_optional_to_last_page()

    # ── 8. Verify Documents and Log section ─────────────────────────────────
    checklist_page.verify_documents_and_log_section()

    # ── 9. Attach a document ─────────────────────────────────────────────────
    checklist_page.attach_document(
        file_path=dummy_pdf_path,
        subject=doc_subject,
        description=doc_desc,
    )

    # ── 10. Add a communication log entry ────────────────────────────────────
    checklist_page.add_communication(
        subject=comm_subject,
        description=comm_desc,
    )

    # ── 11. Create document package and verify success ───────────────────────
    checklist_page.create_package_and_verify()
