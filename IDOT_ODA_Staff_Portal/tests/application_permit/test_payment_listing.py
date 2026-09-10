import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.payment_listing_page import PaymentListingPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Payment Listing & Add New Payment")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.payment_listing
@pytest.mark.smoke
def test_payment_listing_full_workflow(
    authenticated_payment_listing: PaymentListingPage,
):
    """
    Test Case ID: TC_STAFF_PAYMENT_LISTING_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Payments' via sidebar menu link and verify page elements.
    3. Click 'Add New Payment' button and verify form container.
    4. Fill payment type ('Permit Application Fee'), payment method ('Credit Card'), and Faker comments.
    5. Save form, verify 'Record updated successfully.' confirmation modal, click OK, and verify return to listing view.
    """
    payment_pg = authenticated_payment_listing

    with allure.step("1. Activate permit session and navigate to Payment Listing page"):
        payment_pg.navigate_to_payment_listing(company_name="IDOTOAtest2")

    with allure.step("2. Verify Payment Listing page headers, grid wrapper, and action elements loaded"):
        payment_pg.verify_payment_listing_page_loaded()

    with allure.step("3. Click 'Add New Payment' button and verify form container"):
        payment_pg.click_add_new_payment()

    with allure.step("4. Fill payment details (Permit Application Fee, Credit Card, Faker comments) and submit"):
        payment_data = payment_pg.fill_and_submit_payment_details()
        assert payment_data["comments"], "Payment comments were not generated"
        assert payment_data["payment_type"] == "Permit Application Fee"
        assert payment_data["payment_method"] == "Credit Card"
