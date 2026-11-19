import allure
import pytest
from faker import Faker
from pages.parcel_central.owner_tenant_page import OwnerTenantPage

fake = Faker("en_US")


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_OWNER_001 - Add New Owner/Tenant Information")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_add_new_owner_tenant_flow(owner_tenant_page: OwnerTenantPage):
    """
    Test Case ID: TC_NCDOT_OWNER_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Owner/Tenant,
    and creating a new owner/tenant record with non-first Type option and dynamic Faker data:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Owner/Tenant sub-menu in left sidebar.
      7. Open '+ Add New' Owner/Tenant form.
      8. Select Type (non-first option, e.g. 'Mortgagee').
      9. Select Gender ('Male' or option in list).
      10. Fill 'Name for Signature Line *' using dynamic Faker data.
      11. Save record without error.
      12. Click 'Back' and verify return to listing container.
    """
    target_project_id = "2224761"
    target_parcel_id = "111"
    target_type = "Mortgagee"
    target_gender = "Male"
    dynamic_signature_name = f"{fake.first_name()} {fake.last_name()}"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        owner_tenant_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        owner_tenant_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        owner_tenant_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        owner_tenant_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        owner_tenant_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Owner/Tenant sub-menu"):
        owner_tenant_page.navigate_to_owner_tenant()

    with allure.step("7. Open '+ Add New' Owner/Tenant form"):
        owner_tenant_page.open_add_new_owner_tenant_form()

    with allure.step(f"8. Select Type (non-first option: '{target_type}')"):
        owner_tenant_page.select_type(type_name=target_type)

    with allure.step(f"9. Select Gender ('{target_gender}')"):
        owner_tenant_page.select_gender(gender=target_gender)

    with allure.step(f"10. Fill 'Name for Signature Line *' with '{dynamic_signature_name}'"):
        owner_tenant_page.fill_signature_name(name=dynamic_signature_name)

    with allure.step("11. Click Save button"):
        owner_tenant_page.click_save()

    with allure.step("12. Click Back button and verify return to listing view"):
        owner_tenant_page.click_back()
