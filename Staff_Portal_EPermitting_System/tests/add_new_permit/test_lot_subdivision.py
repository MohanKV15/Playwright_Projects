from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.lot_subdivision_page import LotSubdivisionPage

def test_create_lot_subdivision_permit(authenticated_page, faker):
    """
    Independent test case for creating a Lot Subdivision permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    lot_page = LotSubdivisionPage(authenticated_page)

    # 1. Navigation to Permit Listing and Modal
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Select Lot Subdivision
    listing_page.select_application_type("Lot Subdivision")
    
    # 3. Fill and Save
    test_data = {
        "project_name": f"LotSub-{faker.random_int(1000, 9999)}",
    }
    
    lot_page.create_lot_subdivision_permit(test_data)
