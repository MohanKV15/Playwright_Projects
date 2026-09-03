from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.lot_consolidation_page import LotConsolidationPage

def test_create_lot_consolidation_permit(authenticated_page, faker):
    """
    Independent test case for creating a Lot Consolidation permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    lot_page = LotConsolidationPage(authenticated_page)

    # 1. Navigation to Permit Listing and Modal
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Select Lot Consolidation
    listing_page.select_application_type("Lot Consolidation")
    
    # 3. Fill and Save
    test_data = {
        "project_name": f"LotCon-{faker.random_int(1000, 9999)}",
    }
    
    lot_page.create_lot_consolidation_permit(test_data)
