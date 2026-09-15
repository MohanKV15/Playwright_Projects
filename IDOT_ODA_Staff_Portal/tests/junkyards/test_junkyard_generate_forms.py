import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.generate_forms_page import JunkyardGenerateFormsPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Generate Forms - Documents and Letters")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_generate_forms
@pytest.mark.regression
def test_junkyard_generate_forms_full_workflow(
    authenticated_junkyard_generate_forms: JunkyardGenerateFormsPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_GENERATE_FORMS_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2') and select the 1st record row.
    3. Navigate to 'Generate Forms' menu link under Junkyards sidebar menu.
    4. Assert page elements ('Junkyard Details Permit', 'Documents and Letters').
    5. Execute form generation steps (1st form preview canvas, confirm OK modal, 2nd form preview canvas, close popups).
    """
    page_obj = authenticated_junkyard_generate_forms

    with allure.step("1-4. Search company, select record, navigate to Junkyard Generate Forms, and verify headers"):
        record_info = page_obj.navigate_to_junkyard_generate_forms(company_name="IDOTOAtest2")
        assert record_info, "Failed to select 1st record row to activate permit context"

    with allure.step("5. Generate 1st form preview, confirm OK popup, generate 2nd form preview, and verify layout"):
        first_popup = page_obj.generate_first_form()
        page_obj.generate_second_form(first_popup=first_popup)
