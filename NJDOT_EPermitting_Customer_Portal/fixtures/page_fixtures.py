"""
NJDOT EPermitting Customer Portal - Page Object Model Fixtures
Provides decoupled dependency injection for customer portal pages.
"""

import pytest
from playwright.sync_api import Page
from pages.login.login_page import LoginPage
from pages.dashboard_page import DashboardPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def customer_dashboard(authenticated_page: Page) -> DashboardPage:
    """Provides an authenticated customer DashboardPage instance."""
    return DashboardPage(authenticated_page)
