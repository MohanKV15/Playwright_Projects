import allure
import pytest
from faker import Faker
from pages.projects.project_listing_view_page import ProjectListingViewPage

fake = Faker()


@allure.epic("NCDOT ROW Portal")
@allure.feature("Project Listing & Tab Operations")
@allure.story("TC_NCDOT_PRJ_002 - Filter Project 2224761 and Perform Tab Actions")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.projects
@pytest.mark.regression
def test_project_listing_view_operations(project_listing_view_page: ProjectListingViewPage):
    """
    Test Case ID: TC_NCDOT_PRJ_002
    Verifies searching for project '2224761', opening details, and executing
    tab operations across Parcels, Role Assignment, Task Assignment, and Log:
      1. Login & navigate to Project Listing.
      2. Search Project ID '2224761' and refresh.
      3. Open project details view.
      4. Verify Project Information view is displayed.
      5. Parcels tab: Click 'Add New', focus 'Parcel No *', click 'Cancel'.
      6. Role Assignment tab: Navigate to tab and verify display.
      7. Task Assignment tab: Navigate to tab and verify display.
      8. Log tab: Add Call Data & Notes using dynamic Faker data, then close page.
    """
    target_project_id = "2224761"
    dynamic_call_subject = f"Call {fake.word().capitalize()} {fake.random_int(100, 999)}"
    dynamic_notes_subject = f"Note {fake.word().capitalize()} {fake.random_int(100, 999)}"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        project_listing_view_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        project_listing_view_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        project_listing_view_page.open_project_details()

    with allure.step("4. Verify Project Information view is displayed"):
        project_listing_view_page.verify_project_information_visible()

    with allure.step("5. Parcels tab: Click 'Add New', focus 'Parcel No *', click 'Cancel'"):
        project_listing_view_page.open_parcels_tab_and_cancel_add_new()

    with allure.step("6. Role Assignment tab: Navigate to tab and verify display"):
        project_listing_view_page.navigate_to_role_assignment_tab()

    with allure.step("7. Task Assignment tab: Navigate to tab and verify display"):
        project_listing_view_page.navigate_to_task_assignment_tab()

    with allure.step(f"8. Log tab: Add Call Data ('{dynamic_call_subject}') and Notes ('{dynamic_notes_subject}') using Faker, then close"):
        project_listing_view_page.open_log_tab_and_add_call_data_and_notes(
            call_data_subject=dynamic_call_subject,
            notes_subject=dynamic_notes_subject,
            close_page_when_done=True,
        )
