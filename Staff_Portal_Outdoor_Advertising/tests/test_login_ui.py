import pytest
import json
from playwright.sync_api import Page, expect
from pages.login.login_page import LoginPage
from utils.config import Config

@pytest.fixture(scope="module")
def login_test_data():
    with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
        return json.load(f)

class TestLogin:
    
    def test_login_valid(self, page: Page, login_test_data):
        """
        Verify successful login with valid credentials.
        """
        valid_user = login_test_data["valid_users"][0]
        login_page = LoginPage(page)
        
        # Act
        login_page.load(Config.LOGIN_URL)
        login_page.login(valid_user["email"], valid_user["password"], pin=None)
        
        # Assert - wait for navigation to dashboard
        page.wait_for_url("**/Portal/Page/Index/**", timeout=Config.TIMEOUT, wait_until="domcontentloaded")
        expect(page).to_have_url(Config.DASHBOARD_URL, timeout=Config.TIMEOUT)
        
    @pytest.mark.parametrize("invalid_user_index", [0, 1])
    def test_login_invalid(self, page: Page, login_test_data, invalid_user_index):
        """
        Verify login fails correctly when provided invalid credentials.
        """
        invalid_user = login_test_data["invalid_users"][invalid_user_index]
        login_page = LoginPage(page)
        
        # Act
        login_page.load(Config.LOGIN_URL)
        login_page.login(invalid_user["email"], invalid_user["password"], pin=None)
        
        # Assert
        error_text = login_page.get_error_message()
        print(f"\n[DEBUG] Error for {invalid_user['email']}: {error_text}")
        
        # We check expected_error if it's defined in the JSON, otherwise just ensure it's not empty
        if "expected_error" in invalid_user:
            assert invalid_user["expected_error"] in error_text
        else:
            assert error_text != "", "Expected an error message for invalid login, but none was found."
        
        # Ensure we did NOT navigate away from the login page
        assert "LogOutUser" in page.url or "Account/Login" in page.url or "Account" in page.url

    def test_login_empty_fields(self, page: Page):
        """
        Verify mandatory field validations trigger when fields are left blank.
        """
        login_page = LoginPage(page)
        login_page.load(Config.LOGIN_URL)
        
        # Submit empty form
        login_page.login("", "", pin=None)
        
        # Assert field-level validations
        expect(page.get_by_text("Email is mandatory")).to_be_visible(timeout=5000)
        expect(page.get_by_text("Password is mandatory")).to_be_visible(timeout=5000)
