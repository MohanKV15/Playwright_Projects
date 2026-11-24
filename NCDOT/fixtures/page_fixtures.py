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
from pages.parcel_central.workflow_assignment_page import WorkflowAssignmentPage
from pages.parcel_central.task_assignment_page import TaskAssignmentPage
from pages.parcel_central.owner_tenant_page import OwnerTenantPage
from pages.parcel_central.appraisal_request_page import AppraisalRequestPage
from pages.parcel_central.appraisal_page import AppraisalPage
from pages.parcel_central.appraisal_review_page import AppraisalReviewPage
from pages.parcel_central.offer_negotiations_page import OfferNegotiationsPage


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


@pytest.fixture(scope="function")
def workflow_assignment_page(page: Page) -> WorkflowAssignmentPage:
    """Fixture providing an initialized WorkflowAssignmentPage instance."""
    return WorkflowAssignmentPage(page)


@pytest.fixture(scope="function")
def task_assignment_page(page: Page) -> TaskAssignmentPage:
    """Fixture providing an initialized TaskAssignmentPage instance."""
    return TaskAssignmentPage(page)


@pytest.fixture(scope="function")
def owner_tenant_page(page: Page) -> OwnerTenantPage:
    """Fixture providing an initialized OwnerTenantPage instance."""
    return OwnerTenantPage(page)


@pytest.fixture(scope="function")
def appraisal_request_page(page: Page) -> AppraisalRequestPage:
    """Fixture providing an initialized AppraisalRequestPage instance."""
    return AppraisalRequestPage(page)


@pytest.fixture(scope="function")
def appraisal_page(page: Page) -> AppraisalPage:
    """Fixture providing an initialized AppraisalPage instance."""
    return AppraisalPage(page)


@pytest.fixture(scope="function")
def appraisal_review_page(page: Page) -> AppraisalReviewPage:
    """Fixture providing an initialized AppraisalReviewPage instance."""
    return AppraisalReviewPage(page)


@pytest.fixture(scope="function")
def offer_negotiations_page(page: Page) -> OfferNegotiationsPage:
    """Fixture providing an initialized OfferNegotiationsPage instance."""
    return OfferNegotiationsPage(page)


