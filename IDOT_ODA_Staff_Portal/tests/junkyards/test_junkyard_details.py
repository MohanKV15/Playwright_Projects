import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.junkyard_details_page import JunkyardDetailsPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Details and Edit Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_details
@pytest.mark.regression
def test_junkyard_details_search_and_verify_headers_workflow(
    authenticated_junkyard_details: JunkyardDetailsPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_DETAILS_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2').
    3. Assert search results page title, Permits header, and grid table container (#ListingScreenPermitsGrid).
    4. Click 'Edit' button on 1st permit record row.
    5. Verify Junkyard Details form section headers:
       - Applicant Permit Number
       - Yard Information
       - Location Information
       - Industrial Activity (1,000 feet)
       - Property Owner Information
    """
    with allure.step("1. Navigate to Junkyard/Permit Search, filter by company name, edit 1st permit record, and verify details headings"):
        results = authenticated_junkyard_details.execute_search_and_verify_details_workflow(
            company_name="IDOTOAtest2"
        )
        assert results["company_name"] == "IDOTOAtest2", "Company name search filter mismatch"
        assert results["record_info"], "Target permit record details were not retrieved"
        assert results["status"] == "Verified successfully", "Junkyard details verification workflow failed"
