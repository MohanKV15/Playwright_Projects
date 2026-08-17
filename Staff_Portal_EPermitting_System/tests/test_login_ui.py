import json
import pytest
from pages.login.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage
from playwright.sync_api import expect
from utils.config import Config

# Load JSON Data
with open(Config.PROJECT_ROOT / "testdata" / "login_data.json") as f:
    test_data = json.load(f)

class TestLogin:

    @pytest.mark.smoke
    @pytest.mark.parametrize("user", test_data["valid_users"])
    def test_login_valid(self, page, user):
        """Verifies successful login flow into the Dashboard with verified credentials."""
        login_page = LoginPage(page)
        dashboard_page = DashboardPage(page)

        login_page.load(Config.LOGIN_URL)
        login_page.login(email=user["email"], password=user["password"], pin="11")
        
        # Verify codegen's specified Dashboard validations
        dashboard_page.assert_dashboard_loaded()

    @pytest.mark.parametrize("user", test_data["invalid_users"])
    def test_login_invalid(self, page, user):
        """Verifies failed login flow gracefully handles incorrect credentials without routing."""
        login_page = LoginPage(page)
        
        login_page.load(Config.LOGIN_URL)
        login_page.login(email=user["email"], password=user["password"], pin="11")
        
        # Ensure application correctly halts the user state and displays the specified error popup
        # Professional tip: Use a partial match for the error message to be more resilient
        expect(page.get_by_text("invalid username or password")).to_be_visible(timeout=10000)
        assert page.url == Config.LOGIN_URL or "LogOutUser" in page.url

    def test_login_empty(self, page):
        """Verifies the login form prevents empty submission."""
        login_page = LoginPage(page)
        
        login_page.load(Config.LOGIN_URL)
        login_page.login(email="", password="", pin="")
        
        # Ensure that no routing to dashboard takes place
        assert "LogOutUser" in page.url or "Login" in page.url
        
        # Explicitly validate the field-level error messages
        expect(page.get_by_text("Email is mandatory")).to_be_visible(timeout=5000)
        expect(page.get_by_text("Password is mandatory")).to_be_visible(timeout=5000)
        
