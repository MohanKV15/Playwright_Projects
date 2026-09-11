"""
IDOT Outdoor Advertising Staff Portal - Page Object Model Fixtures
Encapsulates all page instantiation and authenticated workflow fixtures,
keeping conftest.py clean and focused on browser infrastructure and reporting.
"""

import pytest
from playwright.sync_api import Page
from IDOT_ODA_Staff_Portal.pages.login.login_page import LoginPage
from IDOT_ODA_Staff_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Staff_Portal.pages.add_paper_application import (
    PrimaryHighwayPage,
    InterstateHighwayPage,
    AdvertisingRegistrationPage,
    DirectionalSignPage,
)
from IDOT_ODA_Staff_Portal.pages.GIS_navigation.GIS_page import GISPage
from IDOT_ODA_Staff_Portal.pages.application_permit import (
    ApplicationDetailsPage,
    InspectionPage,
    DocumentsAndLogPage,
    CustomerActionItemsPage,
    ReviewPage,
    AmendmentPage,
    PermitCompletionPage,
    OriginalPermitPage,
    PaymentListingPage,
    GenerateFormsPage,
    StatusLogPage,
)
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_add_new_applications_page import JunkyardAddNewApplicationsPage


# ---------------------------------------------------------------------------
# Page Object Model Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def status_log_page(page: Page) -> StatusLogPage:
    """Returns an initialized StatusLogPage instance."""
    return StatusLogPage(page)


@pytest.fixture(scope="function")
def authenticated_status_log(authenticated_dashboard: DashboardPage) -> StatusLogPage:
    """Provides an authenticated StatusLogPage positioned on the staff portal."""
    return StatusLogPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def generate_forms_page(page: Page) -> GenerateFormsPage:
    """Returns an initialized GenerateFormsPage instance."""
    return GenerateFormsPage(page)



@pytest.fixture(scope="function")
def authenticated_generate_forms(authenticated_dashboard: DashboardPage) -> GenerateFormsPage:
    """Provides an authenticated GenerateFormsPage positioned on the staff portal."""
    return GenerateFormsPage(authenticated_dashboard.page)

@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Returns an initialized LoginPage instance."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Returns an initialized DashboardPage instance."""
    return DashboardPage(page)


@pytest.fixture(scope="function")
def primary_highway_page(page: Page) -> PrimaryHighwayPage:
    """Returns an initialized PrimaryHighwayPage instance."""
    return PrimaryHighwayPage(page)


@pytest.fixture(scope="function")
def interstate_highway_page(page: Page) -> InterstateHighwayPage:
    """Returns an initialized InterstateHighwayPage instance."""
    return InterstateHighwayPage(page)


@pytest.fixture(scope="function")
def advertising_registration_page(page: Page) -> AdvertisingRegistrationPage:
    """Returns an initialized AdvertisingRegistrationPage instance."""
    return AdvertisingRegistrationPage(page)


@pytest.fixture(scope="function")
def directional_sign_page(page: Page) -> DirectionalSignPage:
    """Returns an initialized DirectionalSignPage instance."""
    return DirectionalSignPage(page)


@pytest.fixture(scope="function")
def gis_page(page: Page) -> GISPage:
    """Returns an initialized GISPage instance."""
    return GISPage(page)


@pytest.fixture(scope="function")
def application_details_page(page: Page) -> ApplicationDetailsPage:
    """Returns an initialized ApplicationDetailsPage instance."""
    return ApplicationDetailsPage(page)


@pytest.fixture(scope="function")
def authenticated_page(page: Page, login_page: LoginPage) -> Page:
    """Authenticates into the Staff Portal and returns the ready page."""
    from IDOT_ODA_Staff_Portal.conftest import _get_staff_credentials
    email, password, pin = _get_staff_credentials()
    login_page.navigate_to_login()
    login_page.login(email=email, password=password, pin=pin)
    return page


@pytest.fixture(scope="function")
def authenticated_staff_page(authenticated_page: Page) -> Page:
    """Alias for authenticated_page."""
    return authenticated_page


@pytest.fixture(scope="function")
def authenticated_dashboard(authenticated_page: Page) -> DashboardPage:
    """Provides an authenticated DashboardPage positioned on Application/Permit Search."""
    dash = DashboardPage(authenticated_page)
    dash.navigate_to_search()
    return dash



@pytest.fixture(scope="function")
def authenticated_primary_highway(authenticated_dashboard: DashboardPage) -> PrimaryHighwayPage:
    """Provides an authenticated PrimaryHighwayPage positioned on the application search view."""
    return PrimaryHighwayPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def authenticated_interstate_highway(authenticated_dashboard: DashboardPage) -> InterstateHighwayPage:
    """Provides an authenticated InterstateHighwayPage positioned on the application search view."""
    return InterstateHighwayPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def authenticated_advertising_registration(authenticated_dashboard: DashboardPage) -> AdvertisingRegistrationPage:
    """Provides an authenticated AdvertisingRegistrationPage positioned on the application search view."""
    return AdvertisingRegistrationPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def authenticated_directional_sign(authenticated_dashboard: DashboardPage) -> DirectionalSignPage:
    """Provides an authenticated DirectionalSignPage positioned on the application search view."""
    return DirectionalSignPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def authenticated_gis(authenticated_dashboard: DashboardPage) -> GISPage:
    """Provides an authenticated GISPage positioned on the staff portal."""
    return GISPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def authenticated_application_details(authenticated_dashboard: DashboardPage) -> ApplicationDetailsPage:
    """Provides an authenticated ApplicationDetailsPage positioned on Application/Permit search view."""
    return ApplicationDetailsPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def inspection_page(page: Page) -> InspectionPage:
    """Returns an initialized InspectionPage instance."""
    return InspectionPage(page)


@pytest.fixture(scope="function")
def authenticated_inspection(authenticated_dashboard: DashboardPage) -> InspectionPage:
    """Provides an authenticated InspectionPage positioned on the staff portal."""
    return InspectionPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def documents_and_log_page(page: Page) -> DocumentsAndLogPage:
    """Returns an initialized DocumentsAndLogPage instance."""
    return DocumentsAndLogPage(page)


@pytest.fixture(scope="function")
def authenticated_documents_and_log(authenticated_dashboard: DashboardPage) -> DocumentsAndLogPage:
    """Provides an authenticated DocumentsAndLogPage positioned on the staff portal."""
    return DocumentsAndLogPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def customer_action_items_page(page: Page) -> CustomerActionItemsPage:
    """Returns an initialized CustomerActionItemsPage instance."""
    return CustomerActionItemsPage(page)


@pytest.fixture(scope="function")
def authenticated_customer_action_items(authenticated_dashboard: DashboardPage) -> CustomerActionItemsPage:
    """Provides an authenticated CustomerActionItemsPage positioned on the staff portal."""
    return CustomerActionItemsPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def review_page(page: Page) -> ReviewPage:
    """Returns an initialized ReviewPage instance."""
    return ReviewPage(page)


@pytest.fixture(scope="function")
def authenticated_review(authenticated_dashboard: DashboardPage) -> ReviewPage:
    """Provides an authenticated ReviewPage positioned on the staff portal."""
    return ReviewPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def amendment_page(page: Page) -> AmendmentPage:
    """Returns an initialized AmendmentPage instance."""
    return AmendmentPage(page)


@pytest.fixture(scope="function")
def authenticated_amendment(authenticated_dashboard: DashboardPage) -> AmendmentPage:
    """Provides an authenticated AmendmentPage positioned on the staff portal."""
    return AmendmentPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def permit_completion_page(page: Page) -> PermitCompletionPage:
    """Returns an initialized PermitCompletionPage instance."""
    return PermitCompletionPage(page)


@pytest.fixture(scope="function")
def authenticated_permit_completion(authenticated_dashboard: DashboardPage) -> PermitCompletionPage:
    """Provides an authenticated PermitCompletionPage positioned on the staff portal."""
    return PermitCompletionPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def original_permit_page(page: Page) -> OriginalPermitPage:
    """Returns an initialized OriginalPermitPage instance."""
    return OriginalPermitPage(page)


@pytest.fixture(scope="function")
def authenticated_original_permit(authenticated_dashboard: DashboardPage) -> OriginalPermitPage:
    """Provides an authenticated OriginalPermitPage positioned on the staff portal."""
    return OriginalPermitPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def payment_listing_page(page: Page) -> PaymentListingPage:
    """Returns an initialized PaymentListingPage instance."""
    return PaymentListingPage(page)


@pytest.fixture(scope="function")
def authenticated_payment_listing(authenticated_dashboard: DashboardPage) -> PaymentListingPage:
    """Provides an authenticated PaymentListingPage positioned on the staff portal."""
    return PaymentListingPage(authenticated_dashboard.page)


@pytest.fixture(scope="function")
def junkyard_add_new_applications_page(page: Page) -> JunkyardAddNewApplicationsPage:
    """Returns an initialized JunkyardAddNewApplicationsPage instance."""
    return JunkyardAddNewApplicationsPage(page)


@pytest.fixture(scope="function")
def authenticated_junkyard_add_new_applications(authenticated_dashboard: DashboardPage) -> JunkyardAddNewApplicationsPage:
    """Provides an authenticated JunkyardAddNewApplicationsPage positioned on the staff portal."""
    return JunkyardAddNewApplicationsPage(authenticated_dashboard.page)



