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
    with allure.step("1. Execute full Payment Listing workflow (navigate, add payment, fill details, save, verify)"):
        payment_data = authenticated_payment_listing.create_new_payment_full_workflow(company_name="IDOTOAtest2")
        assert payment_data["comments"], "Payment comments were not generated"
        assert payment_data["payment_type"] == "Permit Application Fee"
        assert payment_data["payment_method"] == "Credit Card"
