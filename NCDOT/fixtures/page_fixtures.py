"""
NCDOT ROW Portal - Page Object Model Fixtures
Provides decoupled dependency injection for portal pages.
"""

import pytest
from playwright.sync_api import Page
from pages.login.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage
from pages.projects.add_new_project_page import AddNewProjectPage
from pages.projects.project_listing_view_page import ProjectListingViewPage
from pages.parcel_central.parcel_information_page import ParcelInformationPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Fixture providing an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Fixture providing an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def add_new_project_page(page: Page) -> AddNewProjectPage:
    """Fixture providing an initialized AddNewProjectPage instance."""
    return AddNewProjectPage(page)


@pytest.fixture(scope="function")
def project_listing_view_page(page: Page) -> ProjectListingViewPage:
    """Fixture providing an initialized ProjectListingViewPage instance."""
    return ProjectListingViewPage(page)


@pytest.fixture(scope="function")
def parcel_information_page(page: Page) -> ParcelInformationPage:
    """Fixture providing an initialized ParcelInformationPage instance."""
    return ParcelInformationPage(page)
