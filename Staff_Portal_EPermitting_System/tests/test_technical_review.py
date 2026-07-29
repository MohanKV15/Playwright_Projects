import os
import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.technical_review_page import TechnicalReviewPage


def test_technical_review_flow(authenticated_page, faker):
    """
    Verifies Technical Review workflow strictly following codegen script:
    1. Search for permit by company "HCL" and open working record.
    2. Click 'Technical Review' link and verify headers (#LogAppHeader, 'Reviewers Assigned').
    3. Click 'Add New' button and verify form container.
    4. Click 'Edit' on ReviewUnitGrid, select 1st available dropdown option, click Update.
    5. Click 1st date picker, pick present date ('29'), click 2nd date picker, pick present date ('29'), click Save.
    6. Verify summary container, click #editTechReview, verify detail container, click Cancel.
    """
    # ── 1. Initialize Page Objects ──────────────────────────────────────────
    listing_page = PermitListingPage(authenticated_page)
    tech_review_page = TechnicalReviewPage(authenticated_page)

    # ── 2. Search for permit and edit the record ─────────────────────────────
    listing_page.search_and_edit_permit("HCL")

    # ── 3. Execute Technical Review workflow ─────────────────────────────────
    tech_review_page.execute_full_technical_review_codegen_flow()
