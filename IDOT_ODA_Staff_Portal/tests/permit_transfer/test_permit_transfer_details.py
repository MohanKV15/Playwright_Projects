import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.permit_transfer.permit_transfer_details_page import PermitTransferDetailsPage


@allure.epic("Staff Portal")
@allure.feature("Permit Transfer")
@allure.story("Permit Transfer Search & Record Selection Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.permit_transfer
@pytest.mark.regression
def test_permit_transfer_details_workflow(authenticated_page):
    """
    Test Case ID: TC_STAFF_PERMIT_TRANSFER_DETAILS_001
    Workflow:
    1. Navigate: Click 'Permit Transfer' sidebar link and verify listing page elements.
    2. Search: Fill '#PermitForTransfer' with '016-503386' and click Search.
    3. Select Record: Always click #btnStfEdit on the 1st record in #PermitTransferTable.
    4. Headings Verification: Validate 'Permit Transfer Details Save', 'Permit Transfer Transfer',
       and 'Select Permits to transfer' headings are visible.
    """
    permit_transfer_details_pg = PermitTransferDetailsPage(authenticated_page)
    with allure.step("Execute Permit Transfer Details search and 1st record selection workflow"):
        result = permit_transfer_details_pg.execute_permit_transfer_details_workflow(
            permit_number="016-503386",
            row_index=0,
        )
        assert result["status"] == "Verified successfully", "Permit Transfer details workflow failed"
        assert result["permit_number"] == "016-503386", "Permit number mismatch"
        assert result["selected_row_index"] == 0, "Selected row index was not 0 (1st record)"
