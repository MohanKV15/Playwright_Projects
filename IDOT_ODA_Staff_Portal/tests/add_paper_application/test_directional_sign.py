import pytest
from faker import Faker
from IDOT_ODA_Staff_Portal.pages.add_paper_application.directional_sign_page import DirectionalSignPage

fake = Faker()


@pytest.mark.add_paper_application
@pytest.mark.smoke
def test_create_directional_sign_paper_application(
    authenticated_directional_sign: DirectionalSignPage,
):
    """
    Test Case ID: TC_STAFF_DIR_SIGN_001
    Streamlined Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Navigate to 'Add Paper Application' & select 'Directional Sign' type (#btnDirectionalSign).
    3. Fill complete application form (Company, Sign Info, Location, Owner, Attachment) and Save.
    4. Verify saved data and created Application Number on #partial-form.
    """
    # Generate realistic test data with Faker
    owner_name = f"{fake.first_name()} {fake.last_name()}"
    owner_address1 = fake.street_address()
    owner_address2 = fake.secondary_address()
    city = fake.city()

    # 1. Navigate to Add Paper Application & Select Directional Sign
    authenticated_directional_sign.navigate_to_add_paper_application()
    authenticated_directional_sign.select_directional_sign_type()

    # 2. Fill full application details and submit
    created_app_number = authenticated_directional_sign.fill_and_submit_application(
        company_name="test",
        preferred_company="IDOTOAtest2",
        owner_name=owner_name,
        owner_address1=owner_address1,
        owner_address2=owner_address2,
        city=city,
    )
    assert created_app_number, "Failed to extract Application Number from confirmation popup dialog"

    # 3. Verify that saved data and created application number display
    authenticated_directional_sign.verify_application_saved(
        expected_app_number=created_app_number,
        expected_owner_name=owner_name,
        expected_city=city,
    )
