import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.Company.company_listing_page import CompanyListingPage


@allure.epic("Staff Portal")
@allure.feature("Company Management")
@allure.story("Company Listing Search & Header Verification Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.company
@pytest.mark.company_listing
@pytest.mark.regression
def test_company_listing_search_and_verify_headers(
    authenticated_company_listing: CompanyListingPage,
):
    """
    Test Case ID: TC_STAFF_COMPANY_002
    Continuous Workflow (Navigation, Search & Layout Verification):
    1. Navigate: Click 'Company' sidebar link -> 'Company Listing' link.
    2. Page Assertions: Verify 'Companies' heading, '.row.partition', and '.k-grid-content'.
    3. Search: Enter search term ('IDOTOAtest2') in '#Dealer_Name' and click Search button.
    4. Header Assertions: Scroll and verify section headers display upon navigation.
    """
    with allure.step("Execute Company Listing navigation, search, and header verification workflow"):
        result = authenticated_company_listing.execute_company_listing_workflow(
            search_term="IDOTOAtest2"
        )
        assert result["status"] == "Verified successfully", "Company Listing workflow execution failed"
