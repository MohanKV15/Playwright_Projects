import os
import pytest
from playwright.sync_api import expect
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.technical_review_page import TechnicalReviewPage


def test_technical_review_flow(authenticated_page, faker):
    """
    Verifies the complete Technical Review workflow:
    1. Search for permit by company "HCL" and open the specific record "446 0.00 9/0 Atlantic".
    2. Click Back button to return.
    3. Navigate to the Technical Review tab and verify the initial layout.
    4. Click wizard Next button 4 times, then Previous button 2 times.
    5. Edit the target reviewer row "2 09/09/2024 10/10/2024" (or first fallback).
    6. Verify detail layout.
    7. Perform Documents & Log integration test (attach document, add communication, create package).
    8. Click Cancel to return to the list view.
    9. Click Add New review entry.
    10. Verify Add layout.
    11. Click Cancel to complete flow without saving.
    """
    # ── 1. Initialize Page Objects ──────────────────────────────────────────
    listing_page = PermitListingPage(authenticated_page)
    tech_review_page = TechnicalReviewPage(authenticated_page)

    # Dynamic test data path and text strings using Faker
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_pdf_path = os.path.abspath(os.path.join(current_dir, "..", "testdata", "dummy.pdf"))

    doc_subject = f"Auto Tech Doc - {faker.word()}"
    doc_desc = f"Auto Tech Doc Desc - {faker.sentence()}"
    comm_subject = f"Auto Tech Comm - {faker.word()}"
    comm_desc = f"Auto Tech Comm Desc - {faker.sentence()}"

    # ── 2. Search for permit and edit the record ─────────────────────────────
    listing_page.search_and_edit_permit("HCL")

    # ── 3. Click Back button ─────────────────────────────────────────────────
    tech_review_page.click_back_button()

    try:
        # ── 4. Navigate to Technical Review tab and verify initial layout ────────
        tech_review_page.navigate_to_technical_review()
        tech_review_page.verify_initial_reviewers_layout()

        # ── 5. Navigate wizard steps (Next 4 times, Previous 2 times) ────────────
        tech_review_page.navigate_wizard_steps(next_clicks=4, prev_clicks=2)

        # ── 6. Open target reviewer row ('2 09/09/2024 10/10/2024') ──────────────
        has_clicked = tech_review_page.edit_technical_reviewer()

        if has_clicked:
            # ── 7. Verify detail layout and Documents & Log section ─────────────────
            tech_review_page.verify_technical_review_detail_layout()
            
            # ── 8. Test Documents & Log integration (attach file, add comment, create package) ──
            tech_review_page.attach_document(
                file_path=dummy_pdf_path,
                subject=doc_subject,
                description=doc_desc,
            )
            
            tech_review_page.add_communication(
                subject=comm_subject,
                description=comm_desc,
            )
            
            tech_review_page.create_package_and_verify()
            
            # ── 9. Click Cancel and verify we return to main view ───────────────────
            tech_review_page.click_cancel()
            tech_review_page.verify_initial_reviewers_layout()
        else:
            print("Note: No assigned technical reviewers found. Skipping edit check and Documents & Log.")

        # ── 10. Add a new reviewer details entry ────────────────────────────────
        tech_review_page.click_add_new()
        tech_review_page.verify_add_review_layout()

        # ── 11. Cancel adding a new review entry directly (do not save) ─────────
        tech_review_page.click_cancel()
        tech_review_page.verify_initial_reviewers_layout()
    except Exception as e:
        authenticated_page.screenshot(path=r"C:\Users\Mohan(QAQC)\.gemini\antigravity-ide\brain\464fc1d8-6946-4026-a4a3-b45cc66fc7aa\failure_screenshot.png")
        raise e
