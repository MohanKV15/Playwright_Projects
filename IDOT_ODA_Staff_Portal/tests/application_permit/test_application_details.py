import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Application Search & Details Verification")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.application_permit
@pytest.mark.smoke
def test_company_search_and_application_details_flow(
    authenticated_application_details: ApplicationDetailsPage,
):
    """
    Test Case ID: TC_STAFF_APP_DETAILS_001
    Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Search applications by Company Name ('IDOTOAtest2') using reusable search method.
    3. Select the 1st record row in the table, click action button, and navigate to Application Details.
    4. Verify all Application Details sections and informational headings.
    5. Save application details (.float-right) and confirm OK on popup dialog.
    """
    with allure.step("1. Search applications by company name"):
        authenticated_application_details.search_by_company(company_name="IDOTOAtest2")

    with allure.step("2. Select 1st record from results and open Application Details"):
        record_info = authenticated_application_details.select_first_record_and_open_details()
        assert record_info, "No valid record was selected from the search results table"

    with allure.step("3. Verify all page headings and form sections are visible"):
        authenticated_application_details.verify_all_application_details_sections()

    with allure.step("4. Save application and confirm dialog"):
        authenticated_application_details.save_and_confirm_application()

