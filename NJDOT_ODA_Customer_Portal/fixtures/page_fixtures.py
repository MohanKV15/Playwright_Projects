"""
NJDOT ODA Customer Portal - Page Object Model Fixtures
Provides decoupled dependency injection for customer portal pages.
"""

import pytest
from playwright.sync_api import Page
from pages.login.login_page import LoginPage
from pages.submit_application.submit_application_page import SubmitApplicationPage
from pages.submit_application.permit_application_page import PermitApplicationPage
from pages.submit_application.license_application_page import LicenseApplicationPage
from pages.submit_application.permit_transfer_page import PermitTransferPage
from pages.submit_application.name_change_page import NameChangePage
from pages.submit_application.payment_page import PaymentPage
from pages.action_items.action_items_page import ActionItemsPage
from pages.applications_history.applications_history_page import ApplicationsHistoryPage
from pages.payment_activity.payment_activity_page import PaymentActivityPage
from pages.create_account.create_account_page import CreateAccountPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def submit_application_page(page: Page) -> SubmitApplicationPage:
    """Returns an initialized SubmitApplicationPage instance."""
    return SubmitApplicationPage(page)


@pytest.fixture(scope="function")
def customer_dashboard(authenticated_page: Page) -> SubmitApplicationPage:
    """Provides an authenticated SubmitApplicationPage instance."""
    return SubmitApplicationPage(authenticated_page)


@pytest.fixture(scope="function")
def permit_application_page(page: Page) -> PermitApplicationPage:
    """Returns an initialized PermitApplicationPage instance."""
    return PermitApplicationPage(page)


@pytest.fixture(scope="function")
def license_application_page(page: Page) -> LicenseApplicationPage:
    """Returns an initialized LicenseApplicationPage instance."""
    return LicenseApplicationPage(page)


@pytest.fixture(scope="function")
def permit_transfer_page(page: Page) -> PermitTransferPage:
    """Returns an initialized PermitTransferPage instance."""
    return PermitTransferPage(page)


@pytest.fixture(scope="function")
def name_change_page(page: Page) -> NameChangePage:
    """Returns an initialized NameChangePage instance."""
    return NameChangePage(page)


@pytest.fixture(scope="function")
def payment_page(page: Page) -> PaymentPage:
    """Returns an initialized PaymentPage instance."""
    return PaymentPage(page)


@pytest.fixture(scope="function")
def action_items_page(page: Page) -> ActionItemsPage:
    """Returns an initialized ActionItemsPage instance."""
    return ActionItemsPage(page)


@pytest.fixture(scope="function")
def applications_history_page(page: Page) -> ApplicationsHistoryPage:
    """Returns an initialized ApplicationsHistoryPage instance."""
    return ApplicationsHistoryPage(page)


@pytest.fixture(scope="function")
def payment_activity_page(page: Page) -> PaymentActivityPage:
    """Returns an initialized PaymentActivityPage instance."""
    return PaymentActivityPage(page)


@pytest.fixture(scope="function")
def create_account_page(page: Page) -> CreateAccountPage:
    """Returns an initialized CreateAccountPage instance."""
    return CreateAccountPage(page)

