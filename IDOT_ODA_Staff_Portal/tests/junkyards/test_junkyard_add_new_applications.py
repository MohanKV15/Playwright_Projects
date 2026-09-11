import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_add_new_applications_page import JunkyardAddNewApplicationsPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Add Paper Application")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_add_new_applications
@pytest.mark.smoke
def test_junkyard_add_new_applications_full_workflow(
    authenticated_junkyard_add_new_applications: JunkyardAddNewApplicationsPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_ADD_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Verify page headers ('Junkyard/Permit Search', 'Permits') and grid table.
    3. Click 'Add Paper Application' and verify section headers.
    4. Open 'Select Company' modal, search company ('test'), select company row checkbox, and confirm OK.
    5. Select primary radio option (.k-radio-label).
    6. Automatically select 1st valid option from District and County Kendo UI DropDownLists.
    7. Populate Latitude and Longitude coordinates.
    8. Populate Property Owner Information (Name, Address 1, Address 2, City, Phone) using Faker library.
    9. Perform 1st Save & confirm 'Record updated successfully.' modal alert.
    10. Perform final Save & confirm 'Record Saved successfully.' modal alert.
    """
    with allure.step("1. Execute full Junkyard Add Paper Application workflow (navigate, company search, fill form with Faker & 1st dropdown options, save)"):
        results = authenticated_junkyard_add_new_applications.execute_junkyard_add_paper_application_full_workflow(company_name="test")
        assert results["owner_name"], "Property owner name was not generated"
        assert results["city"], "City was not generated"
        assert results["phone"], "Phone number was not generated"
        assert results["district"], "District dropdown option was not selected"
        assert results["county"], "County dropdown option was not selected"
