import pytest
from datetime import datetime
from faker import Faker
from IDOT_ODA_Staff_Portal.pages.add_paper_application.advertising_registration_page import AdvertisingRegistrationPage

fake = Faker()


@pytest.mark.add_paper_application
@pytest.mark.smoke
def test_create_advertising_registration_paper_application(
    authenticated_advertising_registration: AdvertisingRegistrationPage,
):
    """
    Test Case ID: TC_STAFF_ADV_REG_001
    Streamlined Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Navigate to 'Add Paper Application' & select 'Advertising Registration' type (#btnAdvRegistration).
    3. Fill complete application form (Company, Sign Info, Location, Owner, Attachment) and Save.
    4. Verify saved data and created Application Number on #partial-form.
    """
    # Generate realistic test data with Faker
    owner_name = f"{fake.first_name()} {fake.last_name()}"
    owner_address1 = fake.street_address()
    owner_address2 = fake.secondary_address()
    city = fake.city()

    # 1. Navigate to Add Paper Application & Select Advertising Registration
    authenticated_advertising_registration.navigate_to_add_paper_application()
    authenticated_advertising_registration.select_advertising_registration_type()

    # 2. Fill full application details and submit
    created_app_number = authenticated_advertising_registration.fill_and_submit_application(
        company_name="test",
        preferred_company="IDOTOAtest2",
        owner_name=owner_name,
        owner_address1=owner_address1,
        owner_address2=owner_address2,
        city=city,
    )
    assert created_app_number, "Failed to extract Application Number from confirmation popup dialog"

    # 3. Verify that saved data and created application number display
    authenticated_advertising_registration.verify_application_saved(
        expected_app_number=created_app_number,
        expected_owner_name=owner_name,
        expected_city=city,
    )
