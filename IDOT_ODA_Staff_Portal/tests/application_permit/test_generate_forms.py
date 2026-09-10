import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.generate_forms_page import GenerateFormsPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Generate Forms - Documents and Letters")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.generate_forms
@pytest.mark.smoke
def test_generate_forms_full_workflow(
    authenticated_generate_forms: GenerateFormsPage,
):
    """
    Test Case ID: TC_STAFF_GENERATE_FORMS_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit session context.
    2. Navigate to 'Generate Forms' via sidebar menu link and verify page elements.
    3. Click 1st document generation button (nth(2)), verify preview canvas (#mainCanvas) in popup window,
       confirm 'Generated successfully' modal, click 'OK', and verify 'Date Last Generated'.
    4. Click 2nd document generation button (nth(3)), verify preview canvas (#mainCanvas) in popup window,
       close popup windows, and verify section layout container (#partial-form > section > div > div).
    """
    with allure.step("1. Execute full Generate Forms workflow (navigate, generate 1st form preview, generate 2nd form preview, verify)"):
        authenticated_generate_forms.generate_forms_full_workflow(company_name="IDOTOAtest2")
