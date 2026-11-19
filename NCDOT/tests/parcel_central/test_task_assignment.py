import allure
import pytest
from pages.parcel_central.task_assignment_page import TaskAssignmentPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_TASK_001 - Edit and Save Task Assignment")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_edit_and_save_task_assignment(task_assignment_page: TaskAssignmentPage):
    """
    Test Case ID: TC_NCDOT_TASK_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Task Assignment,
    selecting the 1st record in the table, clicking Edit, clicking Save, checking no errors,
    and clicking Back to return to the table:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Task Assignment sub-menu in left sidebar.
      7. Select 1st task assignment record in the grid (#btnTaskAssignEdit).
      8. Click 'Edit' button.
      9. Click 'Save' button.
      10. Verify task saved without errors and view container is visible.
      11. Click 'Back' button and verify return to Task Assignment table.
    """
    target_project_id = "2224761"
    target_parcel_id = "111"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        task_assignment_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        task_assignment_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        task_assignment_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        task_assignment_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        task_assignment_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Task Assignment sub-menu"):
        task_assignment_page.navigate_to_task_assignment()

    with allure.step("7. Select 1st record in Task Assignment table and open details"):
        task_assignment_page.select_task_record(row_index=0)

    with allure.step("8. Click 'Edit' button"):
        task_assignment_page.click_edit()

    with allure.step("9. Click 'Save' button and verify saved without error"):
        task_assignment_page.click_save()

    with allure.step("10. Click 'Back' button and verify return to Task Assignment table"):
        task_assignment_page.click_back()

