import allure
import pytest
from pages.parcel_central.appraisal_page import AppraisalPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_APPRAISAL_002 - End-to-End Appraisal Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_appraisal_flow(appraisal_page: AppraisalPage):
    """
    Test Case ID: TC_NCDOT_APPRAISAL_002
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Appraisal,
    opening row appraisal details, and verifying Documents and Log operations:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Appraisal sub-menu and verify Landing page ('Appraisal Drop Zone').
      7. Open Appraisal Details by clicking row action button (#appraisalDetails).
      8. Documents Tab: Verify navigation and container visibility without error.
      9. Log Tab: Navigate to Log subtab and verify table display.
      10. Log Tab: Add Call Data entry, save, and return via #btnBacknotes.
      11. Log Tab: Add Notes entry, save, and return via #btnBacknotes.
      12. Log Tab: Add Attachment (select 1st Document Type, upload dummy file, fill Subject, and save).
    """
    target_project_id = "2224761"
    target_parcel_id = "111"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        appraisal_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        appraisal_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        appraisal_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        appraisal_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        appraisal_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Appraisal sub-menu and verify Landing page"):
        appraisal_page.navigate_to_appraisal()

    with allure.step("7. Open Appraisal Details by clicking row action button"):
        appraisal_page.open_appraisal_details(row_name="Brad Bass", row_index=0)

    with allure.step("8. Documents Tab: Verify navigation and container visibility"):
        appraisal_page.navigate_to_documents_tab()

    with allure.step("9. Log Tab: Navigate to Log subtab and verify table display"):
        appraisal_page.navigate_to_log_tab()

    with allure.step("10. Log Tab: Add Call Data entry and save"):
        appraisal_page.add_call_data()

    with allure.step("11. Log Tab: Add Notes entry and save"):
        appraisal_page.add_notes()

    with allure.step("12. Log Tab: Add Attachment (1st Document Type, upload dummy file, save)"):
        appraisal_page.add_attachment()

