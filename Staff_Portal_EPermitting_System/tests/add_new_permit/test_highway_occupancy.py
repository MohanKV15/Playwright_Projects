from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.highway_occupancy_page import HighwayOccupancyPage

def test_create_highway_occupancy_permit(authenticated_page, faker):
    """
    Independent test case for creating a Highway Occupancy permit (Erection of Pole).
    """
    listing_page = PermitListingPage(authenticated_page)
    highway_page = HighwayOccupancyPage(authenticated_page)

    # 1. Navigation to Permit Listing and Modal
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Select Highway Occupancy
    listing_page.select_application_type("Highway Occupancy")
    
    # 3. Fill and Save
    test_data = {
        "loc_ref": f"Pole Loc: {faker.address()}",
        "utility_co": f"Utility Co: {faker.company()}",
        "appurtenance": f"Appurtenance: {faker.word()} and {faker.word()}",
    }
    
    highway_page.create_highway_occupancy_permit(test_data)
