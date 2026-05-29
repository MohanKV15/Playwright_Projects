import pytest
from playwright.sync_api import Page
from utils.config import Config
from pages.create_account.create_account_page import CreateAccountPage

def test_create_account_dbe_yes(page: Page):
    """
    Validates the account creation flow when the user selects 'Yes' 
    for the Federal DBE/SBE question.
    """
    # 1. Navigate to the login portal where the "Create an Account" button lives
    page.goto(Config.LOGIN_URL)
    
    # 2. Initialize the CreateAccount POM
    create_account_page = CreateAccountPage(page)
    
    # 3. Start the flow, indicating 'Yes' for DBE
    create_account_page.start_account_creation(is_dbe=True)
    
    # 4. Fill out the registration form using Faker data
    create_account_page.fill_registration_form(is_dbe=True)
    
    # 5. Verify the submit button and back out
    create_account_page.submit_registration()


def test_create_account_dbe_no(page: Page):
    """
    Validates the account creation flow when the user selects 'No' 
    for the Federal DBE/SBE question.
    """
    # 1. Navigate to the login portal where the "Create an Account" button lives
    page.goto(Config.LOGIN_URL)
    
    # 2. Initialize the CreateAccount POM
    create_account_page = CreateAccountPage(page)
    
    # 3. Start the flow, indicating 'No' for DBE
    create_account_page.start_account_creation(is_dbe=False)
    
    # 4. Fill out the registration form using Faker data
    create_account_page.fill_registration_form(is_dbe=False)
    
    # 5. Verify the submit button and back out
    create_account_page.submit_registration()
