import os
import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.administrative_process_page import AdministrativeProcessPage


def test_administrative_process_flow(authenticated_page, faker):
    """
    Verifies the complete Administrative Process workflow:
    1. Search for permit by company "HCL" and open 1st record.
    2. Navigate to Administrative Process tab and verify sub-tabs on 1st record.
    3. Click 'Next' button to navigate to 2nd record.
    4. Verify and process sub-tabs on 2nd record.
    """
    listing_page = PermitListingPage(authenticated_page)
    admin_page = AdministrativeProcessPage(authenticated_page)

    # 1. Search permit by company "HCL" and open 1st record
    listing_page.search_and_edit_permit("HCL")

    # 2. Navigate to Administrative Process tab and verify initial layout for 1st record
    admin_page.navigate_to_administrative_process()
    admin_page.verify_initial_layout()

    # 3. Process sub-tabs for 1st record
    admin_page.process_general_information()
    admin_page.process_initial_review()
    admin_page.process_loac()
    admin_page.process_lola()
    admin_page.process_payment_subtab()
    admin_page.process_revision()
    admin_page.process_appeal()

    # 4. Click 'Next' button to navigate to 2nd record and process sub-tabs
    admin_page.navigate_to_next_record()
    admin_page.verify_initial_layout()

    admin_page.process_general_information()
    admin_page.process_initial_review()
    admin_page.process_loac()
    admin_page.process_lola()
    admin_page.process_payment_subtab()
    admin_page.process_revision()
    admin_page.process_appeal()
