import pytest
from datetime import datetime
from faker import Faker
from IDOT_ODA_Staff_Portal.pages.dashboard.dashboard_page import DashboardPage
from IDOT_ODA_Staff_Portal.pages.add_paper_application.interstate_highway_page import InterstateHighwayPage

fake = Faker()


@pytest.mark.add_paper_application
@pytest.mark.smoke
def test_create_interstate_highway_paper_application(
    authenticated_dashboard: DashboardPage,
    authenticated_interstate_highway: InterstateHighwayPage,
):
    """
    Test Case ID: TC_STAFF_INTERSTATE_APP_001
    Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Click 'Add Paper Application' & select 'Interstate Highway' application type (#btnInterState).
    3. Search company using 'test' and select 'IDOTOAtest2' if available (or first result).
    4. Fill Sign Information with current date & time, dimensions, and structure type.
    5. Fill Location Information (District, County, Route).
    6. Fill Property Owner Information dynamically using Faker.
    7. Upload dummy PDF attachment.
    8. Click Save, extract generated Application Number from confirmation popup, and click OK.
    9. Verify saved data and created Application Number display on #partial-form.
    """
    # Generate realistic test data with Faker
    owner_name = f"{fake.first_name()} {fake.last_name()}"
    owner_address1 = fake.street_address()
    owner_address2 = fake.secondary_address()
    city = fake.city()

    # 1. Navigate to Add Paper Application & Select Interstate Highway
    authenticated_interstate_highway.navigate_to_add_paper_application()
    authenticated_interstate_highway.select_interstate_highway_type()

    # 2. Search and select Company ('IDOTOAtest2' if present, else first available)
    authenticated_interstate_highway.search_and_select_company(company_name="test", preferred_company="IDOTOAtest2")

    # 3. Fill Sign Information with current date/time and dimensions
    authenticated_interstate_highway.fill_sign_information(
        structure_type="Fence Mounted",
        face_width="10",
        face_height="10",
        received_datetime=datetime.now(),
    )

    # 4. Fill Location Information
    authenticated_interstate_highway.fill_location_information(
        district="District 1",
        county="Cook",
        route="100th St",
    )

    # 5. Fill Property Owner Information via Faker
    authenticated_interstate_highway.fill_property_owner_information(
        owner_name=owner_name,
        address1=owner_address1,
        address2=owner_address2,
        city=city,
    )

    # 6. Upload dummy PDF attachment
    authenticated_interstate_highway.upload_attachments()

    # 7. Save and extract generated Application Number from confirmation popup
    created_app_number = authenticated_interstate_highway.save_and_get_application_number()
    assert created_app_number, "Failed to extract Application Number from confirmation popup dialog"

    # 8. Verify that saved data and created application number display
    authenticated_interstate_highway.verify_application_saved(
        expected_app_number=created_app_number,
        expected_owner_name=owner_name,
        expected_city=city,
    )
