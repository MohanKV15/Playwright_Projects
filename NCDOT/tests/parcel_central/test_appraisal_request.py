import allure
import pytest
from pages.parcel_central.appraisal_request_page import AppraisalRequestPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_APPRAISAL_001 - End-to-End Appraisal Request Flow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_appraisal_request_flow(appraisal_request_page: AppraisalRequestPage):
    """
    Test Case ID: TC_NCDOT_APPRAISAL_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Appraisal Request,
    and verifying page navigation, form additions, and saves across all subtabs without error:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Appraisal Request sub-menu (#navigationMenu2).
      7. Land Tab: Edit Engineering Parcel options (radios) and save.
      8. Improvements Tab: Add new improvement form, select owner dropdown, and save.
      9. Documents Tab: Verify navigation and container visibility without error.
      10. Log Tab: Add Call Data entry and Notes entry, save each, and verify without error.
    """
    target_project_id = "2224761"
    target_parcel_id = "111"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        appraisal_request_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        appraisal_request_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        appraisal_request_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        appraisal_request_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        appraisal_request_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Appraisal Request sub-menu (#navigationMenu2)"):
        appraisal_request_page.navigate_to_appraisal_request()

    with allure.step("7. Land Tab: Edit Engineering Parcel options (radios) and save"):
        appraisal_request_page.edit_engineering_parcel_options()

    with allure.step("8. Improvements Tab: Add new improvement record and save"):
        appraisal_request_page.navigate_to_improvements_and_add_record()

    with allure.step("9. Documents Tab: Verify navigation without error"):
        appraisal_request_page.navigate_to_documents_tab()

    with allure.step("10. Log Tab: Add Call Data & Notes entries, save and verify"):
        appraisal_request_page.navigate_to_log_tab_and_add_entries()
