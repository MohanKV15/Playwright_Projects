from pathlib import Path
from pytest_bdd import scenarios, given, when, then
import pytest
from NJDOT_EPermitting_System.pages.login import LoginPage
from NJDOT_EPermitting_System.utils.json_reader import load_json
from NJDOT_EPermitting_System.config import PROJECT_ROOT

# 1. Load all scenarios from the feature file
# pytest-bdd will automatically turn these scenarios into pytest tests!
scenarios("../features/login.feature")

# --- Fixtures / Setup ---
TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "login_data.json"
try:
    data = load_json(str(TEST_DATA_PATH))
except FileNotFoundError as e:
    pytest.skip(f"Test data file not found. Error: {e}", allow_module_level=True)


# --- Given Steps ---
@given("I have a valid authenticated session", target_fixture="valid_authenticated_session")
def setup_valid_authenticated_session(authenticated_page):
    """
    Relies on the existing `authenticated_page` pytest fixture from conftest.py.
    This runs exactly like your original test_login_valid!
    """
    return authenticated_page

@given("I navigate to the login page", target_fixture="login_page_context")
def navigate_to_login(page):
    url = data["professional"]["url"]
    login_page = LoginPage(page)
    login_page.goto(url)
    return login_page


# --- When Steps ---
@when("I submit invalid credentials")
def submit_invalid_credentials(login_page_context):
    email = data["invalid_login"]["email"]
    password = data["invalid_login"]["password"]
    login_page_context.login(email, password)

@when("I submit empty credentials")
def submit_empty_credentials(login_page_context):
    email = data["empty_login"]["email"]
    password = data["empty_login"]["password"]
    login_page_context.login(email, password)


# --- Then Steps ---
@then("I should see the dashboard loaded successfully")
def dashboard_loaded(valid_authenticated_session):
    login_page = LoginPage(valid_authenticated_session)
    login_page.wait_for_dashboard(timeout=20000)

@then("I should remain on the login page")
def remain_on_login(page):
    url = data["professional"]["url"]
    assert page.url == url

@then("the login form should still be visible")
def login_form_visible(page):
    login_page = LoginPage(page)
    login_page.assert_login_form_visible(timeout=10000)