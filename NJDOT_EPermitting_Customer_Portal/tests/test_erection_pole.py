from NJDOT_EPermitting_Customer_Portal.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_Customer_Portal.pages.submit_application.erection_pole_page import ErectionPolePage
from NJDOT_EPermitting_Customer_Portal.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_Customer_Portal.pages.payment_page import PaymentPage
from NJDOT_EPermitting_Customer_Portal.utils.json_reader import load_json
from NJDOT_EPermitting_Customer_Portal.utils.framework_utilities import handle_payment_test, ensure_valid_session


TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))

faker = Faker()
logger = logging.getLogger("test_erection_pole")


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
@pytest.mark.order(12)
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_erection_pole(authenticated_page):
    script_name = Path(__file__).stem
    dashboard = DashboardPage(authenticated_page, script_name=script_name)
    dashboard.click_submit_application()

    page = ErectionPolePage(authenticated_page, script_name=script_name)
    page.assert_applications_page_loaded()

    # Select erection pole application
    page.select_erection_pole()
    page.click_apply_button()
    page.assert_erection_pole_page_loaded()

    # Fill applicant information
    owner_info = _build_owner_info()
    page.fill_owner_info(owner_info)
    page.upload_authorization_certificate()

    # Fill location information
    page.fill_location_information()

    page.fill_additional_details()

    # Fill attachments and select today's date
    page.select_today_date()
    page.upload_erection_pole_attachments()

    # Upload required attachments and check acknowledgement
    page.fill_remaining_required_fields()

    # Continue to payment
    # page.ensure_continue_to_payment_ready(timeout_ms=45000)
    page.click_continue_to_payment()

    # Payment flow
    payment = PaymentPage(page.page)
    payment.select_credit_debit_card()
    payment.fill_customer_information()
    payment.fill_card_details()
    payment.submit_payment()
    payment.verify_payment_success()
 
    # Return to dashboard
    page.click_return_home_and_assert_dashboard()

    logger.info("Erection Pole application flow completed.") 