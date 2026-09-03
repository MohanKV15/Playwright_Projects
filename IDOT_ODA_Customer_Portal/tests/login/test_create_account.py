import pytest
from faker import Faker
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.login.create_an_account_page import CreateAnAccountPage

fake = Faker()


def generate_company_registration_data() -> dict:
    """Generates dynamic Company Registration test data using Faker."""
    email = f"test_{fake.hexify(text='^^^^^^')}@gmail.com"
    return {
        "company_name": f"Test {fake.company()[:20]} Corp",
        "address_1": fake.street_address(),
        "city": fake.city(),
        "zip_code": fake.zipcode()[:5],
        "phone": "999-999-9999",
        "email": email,
        "billing_address_1": fake.street_address(),
        "billing_city": fake.city(),
        "billing_zip_code": fake.zipcode()[:5],
        "poc_fname": fake.first_name(),
        "poc_lname": fake.last_name(),
        "poc_email": email,
        "com_phone": "999-999-9999",
    }


@pytest.mark.login
@pytest.mark.regression
def test_create_account_registration_and_back_navigation(
    login_page: LoginPage,
    create_account_page: CreateAnAccountPage
):
    """
    Test Case ID: TC_REG_001
    Verifies navigating to 'Create an Account', filling mandatory form fields
    using Faker generated test data, clicking 'Back', and verifying redirection
    back to the Login page.
    """
    # 1. Navigate to Login page
    login_page.navigate_to_login()
    login_page.verify_login_page_elements()

    # 2. Click 'Create an Account' button
    login_page.click_create_account()

    # 3. Fill security PIN if prompted
    login_page.fill_pin_if_prompted(pin="11")

    # 4. Verify Company Registration page loaded
    create_account_page.verify_company_registration_loaded()

    # 5. Generate dynamic test data using Faker
    registration_data = generate_company_registration_data()

    # 6. Fill mandatory Company Registration form fields
    create_account_page.fill_full_registration_form(registration_data)

    # 7. Click 'Back' button
    create_account_page.click_back_button()

    # 8. Verify redirection back to Login page
    assert "Accounts/Account" in create_account_page.page.url or login_page.heading_link.is_visible()
