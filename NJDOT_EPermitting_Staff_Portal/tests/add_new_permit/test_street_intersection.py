from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.street_intersection_page import StreetIntersectionPage

def test_create_street_intersection_permit(authenticated_page, faker):
    """
    Independent test case for creating a Street Intersection permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    street_page = StreetIntersectionPage(authenticated_page)

    # 1. Navigation to Permit Listing and Modal
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Select Street Intersection
    listing_page.select_application_type("Street Intersection")
    
    # 3. Fill and Save
    test_data = {
        "project_name": f"StrInt-{faker.random_int(1000, 9999)}",
    }
    
    street_page.create_street_intersection_permit(test_data)
