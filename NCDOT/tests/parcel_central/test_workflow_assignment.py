import allure
import pytest
from pages.parcel_central.workflow_assignment_page import WorkflowAssignmentPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_WORKFLOW_001 - Assign Workflow Role and Staff")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_assign_workflow_role_and_staff(workflow_assignment_page: WorkflowAssignmentPage):
    """
    Test Case ID: TC_NCDOT_WORKFLOW_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Workflow Assignment,
    and creating a new workflow assignment with Role and Staff dropdown selections:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Workflow Assignment sub-menu in left sidebar.
      7. Open '+ Add New' Workflow Assignment modal.
      8. Select Role ('A/G Assigned Attorney' or option from list).
      9. Confirm/Select Staff Type ('Internal Staff of this Role Type').
      10. Select Staff ('A Ravi' or option from list).
      11. Save workflow assignment, handle duplicate alert with 'OK' if present, and verify dialog closes.
    """
    target_project_id = "2224761"
    target_parcel_id = "111"
    target_role = "A/G Assigned Attorney"
    target_staff = "A Ravi"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        workflow_assignment_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        workflow_assignment_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        workflow_assignment_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        workflow_assignment_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        workflow_assignment_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Workflow Assignment sub-menu"):
        workflow_assignment_page.navigate_to_workflow_assignment()

    with allure.step(f"7. Add Workflow Assignment (Role: '{target_role}', Staff: '{target_staff}')"):
        workflow_assignment_page.add_workflow_assignment(
            role_name=target_role,
            staff_type="Internal Staff of this Role Type",
            staff_name=target_staff,
        )

