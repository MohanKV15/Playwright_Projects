import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.inspection_page import InspectionPage


@pytest.mark.application_permit
@pytest.mark.inspection
@pytest.mark.smoke
def test_inspection_full_workflow(
    authenticated_inspection: InspectionPage,
):
    """
    Test Case ID: TC_STAFF_INSPECTION_001
    Workflow:
    1. Authenticate into IDOT Outdoor Advertising Staff Portal via fixture.
    2. Search applications by Company Name ('IDOTOAtest2') and select the 1st record row.
    3. Navigate to Inspection page via Application/Permits sidebar menu.
    4. Verify Inspection page elements (#InspectionList, headings, New Entry button).
    5. Click 'New Entry', populate form choosing the 1st valid option from each dropdown dynamically,
       select date, near radio, submit entry, and confirm 'Record saved successfully'.
    6. Generate Inspection Report, verify popup canvas and 'Generated successfully' modal.
    7. Attach Document with dummy PDF file upload and Faker-generated title and description.
    8. Add Communication log with Faker-generated subject and description, and save.
    9. Verify that once saved, the record displays inside the table (#LogListGrid).
    10. Open Send Email dialog and cancel it.
    11. Click Cancel on details page, verify redirection to listing, and verify saved entry in #InspectionList.
    """
    # 1-3. Search company, select 1st record, navigate to Inspection
    record_info = authenticated_inspection.navigate_to_inspection(company_name="IDOTOAtest2")
    assert record_info, "Failed to select 1st record row to activate permit context"

    # 4. Verify Inspection page loaded
    authenticated_inspection.verify_inspection_page_loaded()

    # 5. Create New Inspection Entry (always uses 1st dropdown options)
    entry_data = authenticated_inspection.create_new_inspection_entry()
    assert entry_data["inspected_by"], "Inspected By dropdown selection failed"
    assert entry_data["report_type"], "Report Type dropdown selection failed"

    # 6. Generate Inspection Report and verify popup canvas
    report_generated = authenticated_inspection.generate_inspection_report()
    assert report_generated, "Inspection report generation failed"

    # 7. Attach Document using dummy file and Faker metadata
    doc_data = authenticated_inspection.attach_document()
    assert doc_data["title"], "Document title was not generated"

    # 8. Add Communication log using Faker
    comm_data = authenticated_inspection.add_communication()
    assert comm_data["subject"], "Communication subject was not generated"

    # 9. Verify saved communication record displays inside the table
    authenticated_inspection.verify_record_in_table(expected_text=comm_data["subject"])

    # 10. Open Send Email modal and cancel
    authenticated_inspection.open_and_cancel_send_email()

    # 11. Click Cancel on details page, verify redirect and verify saved details in InspectionList table
    authenticated_inspection.cancel_details_and_verify_inspection_list(expected_status=entry_data)

