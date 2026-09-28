import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.permit_transfer.add_permit_transfer_page import AddPermitTransferPage


@allure.epic("Staff Portal")
@allure.feature("Permit Transfer")
@allure.story("Add Permit Transfer & Form LA Generation Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.permit_transfer
@pytest.mark.regression
def test_add_permit_transfer_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_PERMIT_TRANSFER_001
    Workflow:
    1. Navigate: Click 'Permit Transfer' link and verify page elements.
    2. Add: Click 'Add Permit Transfer' button.
    3. Search Requested Permit: Fill 'Permit Number Requested for' with '016-503386' & click Search.
    4. Company Lookup: Search company 'test', select first row checkbox (#selectedChk), and confirm OK modal.
    5. Form Fill (Faker): Fill 'From Company Entered *' with dynamic Faker value and click Save.
    6. Transfer To Lookup: Click 'Find', search company 'test', select checkbox, click Save, and confirm OK.
    7. Form LA Popup: Click 'Generate form LA', verify canvas popup (#mainCanvas), close popup, and confirm completion popup.
    """
    permit_transfer_pg = AddPermitTransferPage(authenticated_page)
    with allure.step("Execute Add Permit Transfer full workflow"):
        result = permit_transfer_pg.execute_add_permit_transfer_full_workflow(
            permit_number="016-503386",
            search_company="test",
        )
        assert result["status"] == "Verified successfully", "Add Permit Transfer workflow execution failed"
        assert result["permit_number"] == "016-503386", "Permit number mismatch"
        assert result["from_company_entered"], "From Company Entered value was not populated"
