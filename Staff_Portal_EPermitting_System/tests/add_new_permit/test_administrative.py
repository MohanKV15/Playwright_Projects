from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.administrative_page import AdministrativePage

def test_create_administrative_permit(authenticated_page, faker):
    """
    Independent test case for creating an Administrative permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    admin_page = AdministrativePage(authenticated_page)

    # 1. Navigation
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()
    
    # 2. Selection
    listing_page.select_application_type("Administrative")
    
    # 3. Form Entry (Modular sections for better debugging)
    test_data = {
        "design_job": f"{faker.word().upper()}-{faker.random_int(100, 999)}",
        "upc": f"UPC-{faker.random_number(digits=6)}",
        "milepost": "0"
    }
    
    admin_page.fill_general_information(test_data)
    admin_page.fill_location_information(test_data)
    admin_page.save_permit()
    admin_page.verify_administrative_details(test_data)
    admin_page.close_permit_page()
