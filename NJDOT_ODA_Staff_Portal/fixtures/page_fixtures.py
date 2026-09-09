"""
NJDOT ODA Staff Portal - Page Object Model Fixtures
Provides decoupled dependency injection for POM fixtures.
"""

import pytest
from playwright.sync_api import Page
from pages.login.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Returns an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def authenticated_dashboard(authenticated_page: Page) -> DashboardPage:
    """Provides an authenticated DashboardPage instance."""
    return DashboardPage(authenticated_page)
