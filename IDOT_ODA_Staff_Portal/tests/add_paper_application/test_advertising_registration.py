import pytest
from IDOT_ODA_Staff_Portal.pages.add_paper_application.advertising_registration_page import AdvertisingRegistrationPage


@pytest.mark.add_paper_application
@pytest.mark.smoke
def test_navigate_to_advertising_registration_application(
    authenticated_advertising_registration: AdvertisingRegistrationPage,
):
    """
    Test Case ID: TC_STAFF_ADV_REG_001
    Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Click 'Add Paper Application' button.
    3. Click '#btnAdvRegistration' to open Advertising Registration application form.
    4. Verify 'Applicant Application Number' is visible on the page.
    """
    # 1. Navigate to Add Paper Application
    authenticated_advertising_registration.navigate_to_add_paper_application()

    # 2. Select Advertising Registration type and verify form loaded
    authenticated_advertising_registration.select_advertising_registration_type()

    # 3. Assert Applicant Application Number is visible
    authenticated_advertising_registration.verify_advertising_registration_form_visible()
