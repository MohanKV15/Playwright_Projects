import allure
import pytest
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.login.create_an_account_page import CreateAnAccountPage
from IDOT_ODA_Customer_Portal.testdata import (
    generate_company_registration_data,
)


@allure.epic("Customer Portal")
@allure.feature("Registration")
@allure.story("Create an Account Registration and Back Navigation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.login
@pytest.mark.regression
def test_create_account_registration_and_back_navigation(
    login_page: LoginPage,
    create_account_page: CreateAnAccountPage,
):
    """
    Test Case ID: TC_REG_001
    Verifies navigating to 'Create an Account', filling mandatory form fields
    using Faker generated test data, clicking 'Back', and verifying redirection
    back to the Login page.
    """
    with allure.step("1. Navigate to Login page and verify branding"):
        login_page.navigate_to_login()
        login_page.verify_login_page_elements()

    with allure.step("2. Click 'Create an Account' button"):
        login_page.click_create_account()

    with allure.step("3. Fill security PIN if prompted"):
        login_page.fill_pin_if_prompted(pin="11")

    with allure.step("4. Verify Company Registration page loaded"):
        create_account_page.verify_company_registration_loaded()

    with allure.step("5. Generate dynamic test data and fill Company Registration form"):
        registration_data = generate_company_registration_data()
        create_account_page.fill_full_registration_form(registration_data)

    with allure.step("6. Click 'Back' button"):
        create_account_page.click_back_button()

    with allure.step("7. Verify redirection back to Login page"):
        assert "Accounts/Account" in create_account_page.page.url or login_page.heading_link.is_visible()
