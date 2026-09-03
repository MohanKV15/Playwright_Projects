from NJDOT_EPermitting_Customer_Portal.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_Customer_Portal.pages.submit_application.preapplication_meeting_page import PreApplicationMeetingPage
from NJDOT_EPermitting_Customer_Portal.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_Customer_Portal.utils.json_reader import load_json
from NJDOT_EPermitting_Customer_Portal.utils.framework_utilities import handle_payment_test, ensure_valid_session


TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))

faker = Faker()
logger = logging.getLogger("test_pre_application_meeting")


def _build_owner_info() -> dict:
    return {
        "company": faker.company(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "primary_phone": faker.phone_number(),
        "email": faker.email(),
        "address": faker.street_address(),
        "city": faker.city(),
        "zip_code": faker.zipcode(),
    }


@pytest.mark.authenticated
@pytest.mark.order(15)
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_pre_application_meeting(authenticated_page):
    script_name = Path(__file__).stem
    dashboard = DashboardPage(authenticated_page, script_name=script_name)
    dashboard.wait_for_dashboard_to_load()
    dashboard.assert_dashboard_url()
    logger.info("Authenticated dashboard loaded.")

    # Step 1: Click Submit Application Tile
    dashboard.click_submit_application()

    page = PreApplicationMeetingPage(authenticated_page, script_name=script_name)
    page.assert_applications_page_loaded()

    # Step 2: Select Pre-Application Meeting and enter application form
    page.select_pre_application_meeting()
    page.click_apply_button()
    page.assert_pre_application_meeting_page_loaded()

    # Step 3: Build and fill Owner/Applicant Information
    owner_info = _build_owner_info()
    page.fill_owner_info(owner_info)

    # Step 4: Upload Authorization Certificate (inherited)
    page.upload_authorization_certificate()

    # Step 5: Fill Location Information
    page.fill_location_information()
    page.fill_land_use_information()
    page.fill_spacing_information()

    # Step 6: Fill Lot/Development/Frontage Information
    page.fill_lot_development_frontage_information()

    # Step 7: Upload Pre-App Attachments (Pre-Application Meeting docs + Checklist)
    page.upload_pre_app_attachments()

    # Step 8: Fill Remaining Required Fields (representative, acknowledgment)
    page.fill_remaining_required_fields()

    # Step 9: Click Submit Request
    page.click_submit_request()

    # Step 10: Handle success popup (click OK and verify dashboard redirect)
    page.handle_success_popup()
    logger.info("Pre-Application Meeting application flow completed successfully.")
