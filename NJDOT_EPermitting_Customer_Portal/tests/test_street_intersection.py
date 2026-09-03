from NJDOT_EPermitting_Customer_Portal.config import PROJECT_ROOT
import logging
from pathlib import Path

import pytest
from faker import Faker

from NJDOT_EPermitting_Customer_Portal.pages.submit_application.street_intersection_page import StreetIntersectionPage
from NJDOT_EPermitting_Customer_Portal.pages.submit_application.permit_major_page import PermitMajorPage
from NJDOT_EPermitting_Customer_Portal.pages.dashboard_page import DashboardPage
from NJDOT_EPermitting_Customer_Portal.pages.payment_page import PaymentPage
from NJDOT_EPermitting_Customer_Portal.utils.json_reader import load_json
from NJDOT_EPermitting_Customer_Portal.utils.framework_utilities import handle_payment_test, ensure_valid_session

TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
data = load_json(str(TEST_DATA_PATH))
faker = Faker()
logger = logging.getLogger("test_street_intersection")


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


@pytest.mark.order(7)
@pytest.mark.authenticated
@ensure_valid_session
@handle_payment_test(
    allow_skips_for=["gateway_error", "timeout", "payment_failed", "administrator"]
)
def test_street_intersection(authenticated_page):
	script_name = Path(__file__).stem
	dashboard = DashboardPage(authenticated_page, script_name=script_name)
	dashboard.click_submit_application()

	street_page = StreetIntersectionPage(authenticated_page, script_name=script_name)
	street_page.assert_applications_page_loaded()

	# Select Street Intersection and begin application
	street_page.select_street_intersection()
	street_page.click_apply_button()
	street_page.assert_street_intersection_page_loaded()

	# Build and fill applicant information
	owner_info = _build_owner_info()
	street_page.fill_owner_info(owner_info)
	street_page.upload_authorization_certificate()

	# Fill location information
	street_page.fill_location_information()

	# Upload required attachments and check acknowledgement
	street_page.fill_remaining_required_fields()
	# Upload any extra attachments specific to Street Intersection
	street_page.upload_street_attachments()

	# Ensure Continue to Payment becomes enabled and proceed
	# street_page.ensure_continue_to_payment_ready(timeout_ms=45000)
	street_page.click_continue_to_payment()

	# Payment flow using shared PaymentPage
	payment = PaymentPage(street_page.page)
	payment.select_credit_debit_card()
	payment.fill_customer_information()
	payment.fill_card_details()
	payment.submit_payment()
	payment.verify_payment_success()

	# Return home and assert dashboard
	street_page.click_return_home_and_assert_dashboard()
	logger.info("Street Intersection application flow completed.")
