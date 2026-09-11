import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.inspection_page import JunkyardInspectionPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Inspection Lifecycle & Form Verification")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_inspection
@pytest.mark.regression
def test_junkyard_inspection_full_workflow(
    authenticated_junkyard_inspection: JunkyardInspectionPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_INSPECTION_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2') and select the 1st record row.
    3. Navigate to Inspection page via Junkyards sidebar menu.
    4. Verify Inspection listing page elements ('Junkyard Details Permit', 'Inspection Log', #InspectionList).
    5. Click 'New Entry', verify form elements ('Application Details Permit', 'Inspection Inspected By'),
       populate dropdowns ('Billy Ovalle', 'Annual'), submit entry, and handle OK popups.
    6. Generate Inspection Report, verify #mainCanvas on popup window, close popup window, and confirm OK popup.
    7. Attach Document: click 'Attach Document', select date, upload dummy PDF, fill title/desc, save, confirm OK.
    8. Add Communication: click 'Add Communication', select date, fill subject/desc, save, confirm OK.
    9. Send Email: click 'Send Email', verify 'To:* CC:', click Cancel, confirm OK.
    10. Verify listing grid (.k-grid-content) visibility.
    """
    page_obj = authenticated_junkyard_inspection

    with allure.step("1-3. Search company, select record, and navigate to Junkyard Inspection"):
        record_info = page_obj.navigate_to_junkyard_inspection(company_name="IDOTOAtest2")
        assert record_info, "Failed to select 1st record row to activate permit context"

    with allure.step("4. Assert Inspection Log listing page elements"):
        page_obj.verify_junkyard_inspection_page_loaded()

    with allure.step("5. Create New Inspection Entry using first dropdown items and current date"):
        entry_data = page_obj.create_new_inspection_entry()
        assert entry_data["inspected_by"], "Inspected By selection failed"
        assert entry_data["inspection_date"], "Inspection date was not set to today"

    with allure.step("6. Generate Inspection Report, verify popup canvas, and confirm OK popup"):
        report_generated = page_obj.generate_inspection_report()
        assert report_generated, "Inspection report generation failed"

    with allure.step("7. Attach Document (upload PDF, fill Faker title/description, save, and confirm OK)"):
        doc_data = page_obj.attach_document()
        assert doc_data["title"], "Attach document failed"

    with allure.step("8. Add Communication (fill Faker subject/description, save, and confirm OK)"):
        comm_data = page_obj.add_communication()
        assert comm_data["subject"], "Add communication failed"

    with allure.step("9. Send Email (verify modal, click Cancel, and confirm OK)"):
        page_obj.open_and_cancel_send_email()

    with allure.step("10. Verify listing grid (.k-grid-content) visibility"):
        page_obj.verify_grid_content_visible()
