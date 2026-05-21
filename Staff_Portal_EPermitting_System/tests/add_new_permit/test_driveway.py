from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.driveway_page import DrivewayPage

def test_create_driveway_permit(authenticated_page, faker):
    """
    Independent test case for creating a Driveway permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    driveway_page = DrivewayPage(authenticated_page)

    # 1. Navigation to Permit Listing
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Select Driveway Application Type
    listing_page.select_application_type("Driveway")
    
    # 3. Create Driveway Permit (Modular flow)
    # We pass dummy data (though currently mostly hardcoded as per logic)
    test_data = {
        "project_name": f"Driveway-Test-{faker.random_int(100, 999)}",
        "milepost": "0" 
    }
    
    driveway_page.create_driveway_permit(test_data)
