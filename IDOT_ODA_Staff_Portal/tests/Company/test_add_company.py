import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.Company.add_company_page import AddCompanyPage


@allure.epic("Staff Portal")
@allure.feature("Company Management")
@allure.story("Add Company, Contact, and Name Change Continuous Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.company
@pytest.mark.add_company
@pytest.mark.regression
def test_add_company_full_workflow(
    authenticated_add_company: AddCompanyPage,
):
    """
    Test Case ID: TC_STAFF_COMPANY_001
    Single Continuous End-to-End Workflow:
    1. Navigate: Click 'Company' link -> 'Company Listing' link -> 'Add Company' button.
    2. Corporation Checkbox Toggle Verification:
       - Click 'Select if Company is a Corporation' checkbox and assert officer fields appear.
       - Uncheck checkbox and assert officer fields hide.
    3. Initial Details Form & Save:
       - Fill initial Company Details form (Company Name, Mailing Address 1, City, Zip Code, Phone, Email) using Faker.
       - Click 'Save' button, confirm 'Operation Completed' popup, and verify post-save details.
    4. Add Company Contact Subform:
       - Click 'Add Contact' button.
       - Fill contact details (First Name, Last Name, Email '#dealerEmail', Phone '#com_phone') using Faker.
       - Click Save ('#btnDealerDetailsProfileSave'), confirm 'Record saved successfully' popup.
    5. Add Company Name Change Request Subform:
       - Click 'Add Request' button.
       - Pick date, fill 'New Company Name *' using Faker, select created contact as applicant.
       - Click '#btnAddDealerName', verify row added to '#NameChange > .k-grid-content'.
       - Click main 'Save' button, confirm 'Operation completed' popup, and verify final Company Details view.
    """
    with allure.step("Execute single continuous Add Company workflow"):
        result = authenticated_add_company.execute_add_company_full_workflow()
        assert result["status"] == "Verified successfully", "Add Company workflow execution failed"
        assert result["company_data"]["company_name"], "Company name missing in generated data"
        assert result["contact_data"]["first_name"], "Contact first name missing in generated data"
        assert result["name_change_data"]["new_company_name"], "New company name missing in generated data"
