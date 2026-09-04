import pytest
from IDOT_ODA_Staff_Portal.pages.dashboard.dashboard_page import DashboardPage


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_search_and_application_details_flow(authenticated_dashboard: DashboardPage):
    """
    Test Case ID: TC_STAFF_DASH_001
    Verifies full staff dashboard workflow:
    1. Authenticates into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Navigates to the Application/Permit Search view and verifies page branding & controls.
    3. Performs dynamic status search:
       If records are not immediately displayed in the Permits table, systematically iterates through
       Application Status options until records are found.
    4. Extracts the 1st record's Permit # from the results table.
    5. Enters that 1st record's Permit # into the search field and clicks Search.
    6. Clicks the action/edit button on that matching record.
    7. Observes and verifies that the Application Details form and all core sections
       (Application Number, Sign Info, Airport Restrictions, Location, Property Owner, Attachments)
       are clearly displaying.
    """
    # 1. Verify Application/Permit Search view branding
    authenticated_dashboard.verify_search_page_elements()

    # 2. Dynamic Search: iterate statuses until records appear in Permits table
    records_found = authenticated_dashboard.search_until_records_found()
    assert records_found, "Failed to retrieve any permit records in Permits table across tested statuses"

    # 3. Extract 1st record's Permit # from table
    target_permit_number = authenticated_dashboard.get_first_record_permit_number()
    assert target_permit_number, "Permit number from first row was empty"

    # 4. Search specifically using the 1st record's Permit #
    authenticated_dashboard.search_by_permit_number(target_permit_number)

    # 5. Click Action/Edit button on the matching record
    authenticated_dashboard.click_first_record_action_button()

    # 6. Observe and verify all Application Details sections are clearly displaying
    authenticated_dashboard.verify_application_details_sections()
