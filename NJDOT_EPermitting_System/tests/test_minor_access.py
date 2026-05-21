from NJDOT_EPermitting_System.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_System.pages.submit_application import MinorAccessPage, MajorPlanningPage
from NJDOT_EPermitting_System.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_System.pages.payment_page import PaymentPage
from NJDOT_EPermitting_System.utils.json_reader import load_json
from NJDOT_EPermitting_System.utils.framework_utilities import handle_payment_test, ensure_valid_session

TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))
faker = Faker()
logger = logging.getLogger("test_minor_access")


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


@pytest.mark.order(6)
@pytest.mark.authenticated
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_minor_access(authenticated_page):

    script_name = Path(__file__).stem
    dashboard = DashboardPage(authenticated_page, script_name=script_name)

    # rely on `ensure_clean_dashboard` autouse fixture; avoid redundant goto
    logger.info("Dashboard already prepared by fixture.")

    # Start Minor Access flow
    dashboard.click_submit_application()

    minor_page = MinorAccessPage(authenticated_page, script_name=script_name)
    minor_page.assert_applications_page_loaded()

    minor_page.select_minor_access()
    minor_page.click_apply_button()

    minor_page.assert_minor_access_page_loaded()

    owner_info = _build_owner_info()

    minor_page.fill_owner_info(owner_info)
    minor_page.upload_authorization_certificate()
    minor_page.fill_location_information()
    minor_page.fill_land_use_information()
    minor_page.fill_spacing_information()
    minor_page.fill_remaining_required_fields()

    # minor_page.ensure_continue_to_payment_ready(timeout_ms=45000)
    minor_page.click_continue_to_payment()

    # Reuse the PaymentPage for all payment steps
    payment = PaymentPage(minor_page.page)
    payment.select_credit_debit_card()
    payment.fill_customer_information()
    payment.fill_card_details()
    payment.submit_payment()
    payment.verify_payment_success()

    # Click return home using the application page object (keeps navigation assertions centralized)
    minor_page.click_return_home_and_assert_dashboard()