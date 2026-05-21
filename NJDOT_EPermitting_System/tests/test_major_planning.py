from NJDOT_EPermitting_System.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_System.pages.submit_application import MajorPlanningPage
from NJDOT_EPermitting_System.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
from NJDOT_EPermitting_System.utils.json_reader import load_json
from NJDOT_EPermitting_System.utils.framework_utilities import handle_payment_test, ensure_valid_session

TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))
faker = Faker()
logger = logging.getLogger("test_major_planning")


# This test drives the end-to-end flow through page-object assertion methods.
# Pytest and conftest hooks capture failures, screenshots, and HTML reporting.
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


@pytest.mark.order(5)
@pytest.mark.authenticated
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_major_with_planning(authenticated_page):
    script_name = Path(__file__).stem
    dashboard = DashboardPage(authenticated_page, script_name=script_name)
    
    # rely on `ensure_clean_dashboard` autouse fixture; avoid redundant goto
    dashboard.wait_for_dashboard_to_load()
    dashboard.assert_dashboard_url()
    logger.info("Authenticated dashboard loaded for Major with Planning.")

    # Step 1: Click Submit Application Tile.
    dashboard.click_submit_application()
    
    planning_page = MajorPlanningPage(authenticated_page, script_name=script_name)
    planning_page.assert_applications_page_loaded()

    # Step 2: Click Apply for Major with Planning.
    planning_page.click_apply_for_major_with_planning()
    planning_page.assert_major_with_planning_page_loaded()

    # Step 3: Build Owner Information Test Data.
    owner_info = _build_owner_info()

    # Step 4: Fill Applicant/Owner Information.
    planning_page.fill_owner_info(owner_info)

    # Step 5: Upload Authorization Certificate.
    planning_page.upload_authorization_certificate()

    # Step 6: Fill Location Information.
    planning_page.fill_location_information()

    # Step 7: Fill Land Use Information.
    planning_page.fill_land_use_information()

    # Step 8: Fill Spacing Information.
    planning_page.fill_spacing_information()

    # Step 9: Fill Remaining Required Fields.
    planning_page.fill_remaining_required_fields()

    # Step 10: Ensure Continue To Payment Is Enabled.
    # planning_page.ensure_continue_to_payment_ready(timeout_ms=45000)

    # Step 11: Continue To Payment.
    planning_page.click_continue_to_payment()

    payment = PaymentPage(planning_page.page)
    payment.select_credit_debit_card()
    payment.fill_customer_information()
    payment.fill_card_details()
    payment.submit_payment()
    payment.verify_payment_success()

    planning_page.click_return_home_and_assert_dashboard()