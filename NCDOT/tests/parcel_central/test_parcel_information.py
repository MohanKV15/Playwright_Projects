import allure
import pytest
from faker import Faker
from pages.parcel_central.parcel_information_page import ParcelInformationPage

fake = Faker("en_US")


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_PARCEL_001 - Add New Parcel Information")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_add_new_parcel_flow(parcel_information_page: ParcelInformationPage):
    """
    Test Case ID: TC_NCDOT_PARCEL_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    and creating a new parcel record with dynamic Faker data and dropdown selections:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Open Add New Parcel form.
      6. Fill Parcel No *, Property Tax ID *, and Deed Book/Page * with dynamic Faker data.
      7. Select Parcel Type ('Agricultural').
      8. Select County ('Greene').
      9. Select Acquisition Status ('Appraisal Received').
      10. Save parcel record and verify persistence.
    """
    target_project_id = "2224761"
    dynamic_parcel_no = str(fake.random_int(10000, 99999))
    dynamic_tax_id = str(fake.random_int(100000, 999999))
    dynamic_deed_page = str(fake.random_int(1000, 9999))

    with allure.step("1. Authenticate and navigate to Project Listing"):
        parcel_information_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        parcel_information_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        parcel_information_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        parcel_information_page.navigate_to_parcels_tab()

    with allure.step("5. Open '+ Add New' Parcel form"):
        parcel_information_page.open_add_new_parcel_form()

    with allure.step(f"6. Fill details: Parcel #{dynamic_parcel_no}, Tax ID #{dynamic_tax_id}, Deed #{dynamic_deed_page}"):
        parcel_information_page.fill_parcel_details(
            parcel_no=dynamic_parcel_no,
            property_tax_id=dynamic_tax_id,
            deed_book_page=dynamic_deed_page,
        )

    with allure.step("7. Select Parcel Type ('Agricultural')"):
        parcel_information_page.select_parcel_type(option_name="Agricultural")

    with allure.step("8. Select County ('Greene')"):
        parcel_information_page.select_county(option_name="Greene")

    with allure.step("9. Select Acquisition Status ('Appraisal Received')"):
        parcel_information_page.select_acquisition_status(option_name="Appraisal Received")

    with allure.step("10. Save parcel record"):
        parcel_information_page.save_parcel()

