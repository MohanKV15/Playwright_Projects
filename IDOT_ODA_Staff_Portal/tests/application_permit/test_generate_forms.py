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
    gen_forms_pg = authenticated_generate_forms

    with allure.step("1. Activate permit session and navigate to Generate Forms page"):
        gen_forms_pg.navigate_to_generate_forms(company_name="IDOTOAtest2")

    with allure.step("2. Verify Generate Forms page headers and form container loaded"):
        gen_forms_pg.verify_generate_forms_page_loaded()

    with allure.step("3. Click 1st generate form button (nth(2)), verify popup canvas preview, and confirm OK alert"):
        first_popup = gen_forms_pg.generate_first_form()

    with allure.step("4. Click 2nd generate form button (nth(3)), verify popup canvas preview, close popups, and verify layout"):
        gen_forms_pg.generate_second_form(first_popup=first_popup)
