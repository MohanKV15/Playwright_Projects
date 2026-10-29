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
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.primary_highway_page import (
    PrimaryHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.interstate_highway_page import (
    InterstateHighwayPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.directional_sign_page import (
    DirectionalSignPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_application.junkyard_page import (
    JunkyardPage,
)
from IDOT_ODA_Customer_Portal.pages.dashboard.submit_application.permit_transfer.permit_transfer_page import (
    PermitTransferPage,
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


@pytest.fixture(scope="function")
def interstate_highway_page(page: Page) -> InterstateHighwayPage:
    """Fixture providing an initialized InterstateHighwayPage instance."""
    return InterstateHighwayPage(page)


@pytest.fixture(scope="function")
def directional_sign_page(page: Page) -> DirectionalSignPage:
    """Fixture providing an initialized DirectionalSignPage instance."""
    return DirectionalSignPage(page)


@pytest.fixture(scope="function")
def junkyard_page(page: Page) -> JunkyardPage:
    """Fixture providing an initialized JunkyardPage instance."""
    return JunkyardPage(page)


@pytest.fixture(scope="function")
def permit_transfer_page(page: Page) -> PermitTransferPage:
    """Fixture providing an initialized PermitTransferPage instance."""
    return PermitTransferPage(page)


