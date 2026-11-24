import allure
import pytest
from pages.parcel_central.offer_negotiations_page import OfferNegotiationsPage


@allure.epic("NCDOT ROW Portal")
@allure.feature("Parcel Central")
@allure.story("TC_NCDOT_OFFER_NEGOTIATIONS_001 - End-to-End Offer/Negotiations Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parcels
@pytest.mark.regression
def test_offer_negotiations_flow(offer_negotiations_page: OfferNegotiationsPage):
    """
    Test Case ID: TC_NCDOT_OFFER_NEGOTIATIONS_001
    Verifies searching project '2224761', opening details, navigating to Parcels tab,
    selecting parcel record '111' to enter Parcel Central, navigating to Offer/Negotiations,
    managing negotiation details, and verifying subtabs across Offers, Admin Adjustment,
    Encumbrances, Recording, Documents, and Log without error:
      1. Login & navigate to Project Listing.
      2. Filter project by ID '2224761' and refresh table.
      3. Open project details.
      4. Navigate to Parcels tab.
      5. Select parcel record ('111' or 1st available) to open Parcel Central (#btnGeneralParcelPrjEdit).
      6. Navigate to Offer/Negotiations sub-menu and verify Landing page.
      7. Ensure Negotiation Details view is open (adds new record if none exists).
      8. Edit Offer Details (Recommendation dropdowns) and save.
      9. Offers Subtab: Add new offer (Offer Type, Date) and save.
      10. Admin Adjustment Subtab: Edit admin adjustment details and save.
      11. Encumbrances Subtab: Add new encumbrance (Type, Grantor, Grantee, Easement Type) and save.
      12. Recording Subtab: Add new recording entry (Instrument Type) and save.
      13. Documents Subtab: Verify navigation and container visibility.
      14. Log Subtab:
          * Add Call Data entry and save.
          * Add Notes entry and save.
          * Add Attachment (1st Document Type, upload dummy file, fill Subject, save).
    """
    target_project_id = "2224761"
    target_parcel_id = "111"

    with allure.step("1. Authenticate and navigate to Project Listing"):
        offer_negotiations_page.login_and_navigate_to_projects()

    with allure.step(f"2. Search for Project ID '{target_project_id}' and refresh table"):
        offer_negotiations_page.search_project_by_id(project_id=target_project_id)

    with allure.step(f"3. Open details for Project #{target_project_id}"):
        offer_negotiations_page.open_project_details()

    with allure.step("4. Navigate to Parcels tab"):
        offer_negotiations_page.navigate_to_parcels_tab()

    with allure.step(f"5. Open parcel '{target_parcel_id}' in Parcel Central via edit action (#btnGeneralParcelPrjEdit)"):
        offer_negotiations_page.open_parcel_in_parcel_central(parcel_identifier=target_parcel_id, row_index=0)

    with allure.step("6. Navigate to Offer/Negotiations sub-menu and verify Landing page"):
        offer_negotiations_page.navigate_to_offer_negotiations()

    with allure.step("7. Ensure Negotiation Details view is open"):
        offer_negotiations_page.ensure_negotiation_details_open()

    with allure.step("8. Edit Offer Details and save"):
        offer_negotiations_page.edit_offer_details()

    with allure.step("9. Offers Subtab: Add new offer and save"):
        offer_negotiations_page.navigate_to_offers_tab()
        offer_negotiations_page.add_new_offer()

    with allure.step("10. Admin Adjustment Subtab: Edit and save"):
        offer_negotiations_page.navigate_to_admin_adjustment_tab()
        offer_negotiations_page.edit_and_save_admin_adjustment()

    with allure.step("11. Encumbrances Subtab: Add new encumbrance and save"):
        offer_negotiations_page.navigate_to_encumbrances_tab()
        offer_negotiations_page.add_new_encumbrance()

    with allure.step("12. Recording Subtab: Add new recording entry and save"):
        offer_negotiations_page.navigate_to_recording_tab()
        offer_negotiations_page.add_new_recording()

    with allure.step("13. Documents Subtab: Verify navigation and container visibility"):
        offer_negotiations_page.navigate_to_documents_tab()

    with allure.step("14. Log Subtab: Navigate and add Call Data, Notes, and Attachment"):
        offer_negotiations_page.navigate_to_log_tab()
        offer_negotiations_page.add_call_data()
        offer_negotiations_page.add_notes()
        offer_negotiations_page.add_attachment()

