import allure
import pytest
from pages.dashboard.add_new_project_page import AddNewProjectPage
from testdata.test_data_factory import TestDataFactory


@allure.epic("NCDOT ROW Portal")
@allure.feature("Project Management")
@allure.story("TC_NCDOT_PRJ_001 - End-to-End Add New Project and Configuration Flow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.projects
@pytest.mark.regression
def test_add_new_project_flow(add_new_project_page: AddNewProjectPage):
    """
    Test Case ID: TC_NCDOT_PRJ_001
    Verifies complete end-to-end Project creation and configuration:
      1. Asserts initial Project Listing filter container visibility.
      2. Opens 'Add New Project' modal and inputs Faker project ID, 1st division, 1st letting type, and present date.
      3. Verifies Project Information view and updates STIP / Acquisition Type using 1st options.
      4. Creates a new WBS using mandatory system pattern 'ABC12.1.ADE' and 1st division/county.
      5. Navigates to Parcels tab and adds a new parcel record with Faker data.
      6. Navigates to Role Assignment tab and verifies tab display.
      7. Navigates to Task Assignment tab and verifies tab display.
      8. Navigates to Log tab and verifies audit display.
    """
    # Generate dynamic test data using Faker (maintains required WBS format 'ABC12.1.ADE')
    project_data = TestDataFactory.get_new_project_data()

    with allure.step("1. Navigate to AccountEntra, authenticate, wait for page load & table button"):
        add_new_project_page.login_and_navigate_to_projects()

    with allure.step(f"2. Open 'Add New Project' modal and create Project ID #{project_data['project_id']}"):
        add_new_project_page.open_add_new_project_modal()
        add_new_project_page.fill_and_save_new_project(
            project_id=project_data["project_id"]
        )

    with allure.step("3. Verify Project Information and edit STIP / Acquisition Type (1st options)"):
        add_new_project_page.verify_project_information_visible()
        add_new_project_page.edit_project_information()

    with allure.step(f"4. Add WBS code strictly formatted as '{project_data['wbs']}'"):
        add_new_project_page.add_wbs(
            wbs_code=project_data["wbs"]
        )

    with allure.step(f"5. Navigate to Parcels tab and create Parcel #{project_data['parcel_no']}"):
        add_new_project_page.navigate_to_parcels_tab()
        add_new_project_page.add_parcel(
            parcel_no=project_data["parcel_no"],
            property_tax_id=project_data["property_tax_id"],
            deed_book_page=project_data["deed_book_page"],
        )

    with allure.step("6. Navigate to Role Assignment tab"):
        add_new_project_page.navigate_to_role_assignment_tab()

    with allure.step("7. Navigate to Task Assignment tab"):
        add_new_project_page.navigate_to_task_assignment_tab()

    with allure.step("8. Navigate to Log tab and verify audit records"):
        add_new_project_page.navigate_to_log_tab()
