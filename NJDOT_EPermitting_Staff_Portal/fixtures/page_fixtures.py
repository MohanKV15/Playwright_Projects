"""
NJDOT EPermitting Staff Portal - Page Object Model Fixtures
Provides decoupled dependency injection for Page Object Models.
"""

import pytest
from playwright.sync_api import Page
from pages.login.login_page import LoginPage
from pages.dashboard.dashboard_page import DashboardPage
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.applicant_information_page import ApplicantInformationPage
from pages.application_permit_info.general_information_page import GeneralInformationPage
from pages.application_permit_info.inspection_page import InspectionPage
from pages.application_permit_info.checklist_page import ChecklistPage
from pages.application_permit_info.lot_development_page import LotDevelopmentPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Returns an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def permit_listing_page(page: Page) -> PermitListingPage:
    """Returns an initialized PermitListingPage instance."""
    return PermitListingPage(page)


@pytest.fixture(scope="function")
def applicant_information_page(page: Page) -> ApplicantInformationPage:
    """Returns an initialized ApplicantInformationPage instance."""
    return ApplicantInformationPage(page)


@pytest.fixture(scope="function")
def general_information_page(page: Page) -> GeneralInformationPage:
    """Returns an initialized GeneralInformationPage instance."""
    return GeneralInformationPage(page)


@pytest.fixture(scope="function")
def inspection_page(page: Page) -> InspectionPage:
    """Returns an initialized InspectionPage instance."""
    return InspectionPage(page)


@pytest.fixture(scope="function")
def checklist_page(page: Page) -> ChecklistPage:
    """Returns an initialized ChecklistPage instance."""
    return ChecklistPage(page)


@pytest.fixture(scope="function")
def lot_development_page(page: Page) -> LotDevelopmentPage:
    """Returns an initialized LotDevelopmentPage instance."""
    return LotDevelopmentPage(page)


@pytest.fixture(scope="function")
def authenticated_permit_listing(authenticated_page: Page) -> PermitListingPage:
    """Provides an authenticated PermitListingPage."""
    return PermitListingPage(authenticated_page)


@pytest.fixture(scope="function")
def authenticated_applicant_info(authenticated_page: Page) -> ApplicantInformationPage:
    """Provides an authenticated ApplicantInformationPage."""
    return ApplicantInformationPage(authenticated_page)
