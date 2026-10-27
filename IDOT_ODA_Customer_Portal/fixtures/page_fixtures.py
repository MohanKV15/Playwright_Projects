"""
IDOT ODA Customer Portal - Page Object Model Fixtures
Provides decoupled dependency injection for customer portal pages,
keeping conftest.py focused exclusively on browser infrastructure and reporting.
"""

import pytest
from playwright.sync_api import Page
from IDOT_ODA_Customer_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Customer_Portal.pages.login.create_an_account_page import CreateAnAccountPage
from IDOT_ODA_Customer_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.payment_page import PaymentPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Fixture providing an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def create_account_page(page: Page) -> CreateAnAccountPage:
    """Fixture providing an initialized CreateAnAccountPage instance."""
    return CreateAnAccountPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Fixture providing an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def primary_highway_page(page: Page) -> PrimaryHighwayPage:
    """Fixture providing an initialized PrimaryHighwayPage instance."""
    return PrimaryHighwayPage(page)


@pytest.fixture(scope="function")
def payment_page(page: Page) -> PaymentPage:
    """Fixture providing an initialized PaymentPage instance."""
    return PaymentPage(page)
