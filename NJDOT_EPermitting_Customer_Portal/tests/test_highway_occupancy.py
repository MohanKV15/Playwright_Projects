from NJDOT_EPermitting_Customer_Portal.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_Customer_Portal.pages.submit_application.highway_occupancy_page import HighwayOccupancyPage
from NJDOT_EPermitting_Customer_Portal.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_Customer_Portal.pages.payment_page import PaymentPage
from NJDOT_EPermitting_Customer_Portal.utils.json_reader import load_json
from NJDOT_EPermitting_Customer_Portal.utils.framework_utilities import handle_payment_test, ensure_valid_session

TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))
faker = Faker()
logger = logging.getLogger("test_highway_occupancy")


def _build_owner_info() -> dict:
    """Generate random applicant information using faker."""
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


@pytest.mark.order(8)
@pytest.mark.authenticated
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_highway_occupancy(authenticated_page):
    """End-to-end Highway Occupancy application test flow."""
    script_name = Path(__file__).stem
    dashboard = DashboardPage(authenticated_page, script_name=script_name)
    dashboard.click_submit_application()

    highway_page = HighwayOccupancyPage(authenticated_page, script_name=script_name)
    highway_page.assert_applications_page_loaded()

    highway_page.select_highway_occupancy()
    highway_page.click_apply_button()
    highway_page.assert_highway_occupancy_page_loaded()

    # Build and fill applicant information
    owner_info = _build_owner_info()
    highway_page.fill_owner_info(owner_info)
    highway_page.upload_authorization_certificate()

    # Fill location information
    highway_page.fill_location_information()

    # Fill Highway Occupancy permit-specific information (Type, Location, Description)
    highway_page.fill_permit_information()

    # Upload required attachments and check for issues
    highway_page.fill_remaining_required_fields()
    highway_page.upload_street_attachments()

    # Ensure Continue to Payment is ready and proceed
    # highway_page.ensure_continue_to_payment_ready(timeout_ms=45000)
    highway_page.click_continue_to_payment()

    # Payment flow using shared PaymentPage
    payment = PaymentPage(highway_page.page)
    payment.select_credit_debit_card()
    payment.fill_customer_information()
    payment.fill_card_details()
    payment.submit_payment()
    payment.verify_payment_success()

    # Return home and assert dashboard
    highway_page.click_return_home_and_assert_dashboard()
    logger.info("✅ Highway Occupancy application flow completed successfully.")
