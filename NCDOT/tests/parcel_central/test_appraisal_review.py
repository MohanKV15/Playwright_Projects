import allure
import pytest
from pages.parcel_central.appraisal_review_page import AppraisalReviewPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_APPRAISAL_REVIEW_001 - End-to-End Appraisal Review Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_appraisal_review_flow(appraisal_review_page: AppraisalReviewPage):
    """
    Test Case ID: TC_NCDOT_APPRAISAL_REVIEW_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Appraisal Review,
    opening row review details, editing and saving, navigating to Log tab, and performing
    log additions (Call Data, Notes, Attachment):
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Appraisal Review sub-menu and verify Landing page (#partialForm #partial-form).
      7. Open Appraisal Review Details via row edit button (#tcAppraisalReviewEditIPV).
      8. Click Edit (#btnEditReviewDetailsTab) and Save (#btnSaveReviewDetailsTab).
      9. Navigate to Log tab on #AppraisalReviewTabs and verify table display.
      10. Log Tab: Add Call Data entry, save, and return via #btnBacknotes.
      11. Log Tab: Add Notes entry, save, and return via #btnBacknotes.
      12. Log Tab: Add Attachment (select 1st Document Type, upload dummy file, fill Subject, and save).
    """
    target_project_id = "2224761"
    target_parcel_id = "111"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        appraisal_review_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        appraisal_review_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        appraisal_review_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        appraisal_review_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        appraisal_review_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Appraisal Review sub-menu and verify Landing page"):
        appraisal_review_page.navigate_to_appraisal_review()

    with allure.step("7. Open Appraisal Review Details via row edit button (#tcAppraisalReviewEditIPV)"):
        appraisal_review_page.open_appraisal_review_details()

    with allure.step("8. Click Edit and Save on Review Details"):
        appraisal_review_page.edit_and_save_review_details()

    with allure.step("9. Log Tab: Navigate to Log subtab and verify table display"):
        appraisal_review_page.navigate_to_log_tab()

    with allure.step("10. Log Tab: Add Call Data entry and save"):
        appraisal_review_page.add_call_data()

    with allure.step("11. Log Tab: Add Notes entry and save"):
        appraisal_review_page.add_notes()

    with allure.step("12. Log Tab: Add Attachment (1st Document Type, upload dummy file, save)"):
        appraisal_review_page.add_attachment()

