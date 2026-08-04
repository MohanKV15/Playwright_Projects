from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.pre_application_meeting_page import PreApplicationMeetingPage

def test_create_pre_application_meeting_permit(authenticated_page, faker):
    """
    Independent test case for creating a Pre-Application Meeting permit.
    """
    listing_page = PermitListingPage(authenticated_page)
    pre_app_page = PreApplicationMeetingPage(authenticated_page)

    # 1. Navigation
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()

    # 2. Selection
    listing_page.select_application_type("Pre-Application Meeting")

    # 3. Form Entry (Modular sections for clear debugging)
    test_data = {
        "milepost": "1"
    }

    pre_app_page.fill_general_information(test_data)
    pre_app_page.fill_location_information(test_data)
    pre_app_page.save_permit()
    pre_app_page.verify_pre_application_meeting_details(test_data)
    pre_app_page.close_permit_page()
