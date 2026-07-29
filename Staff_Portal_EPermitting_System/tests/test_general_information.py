import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.general_information_page import GeneralInformationPage


def test_permit_edit_and_general_info_flow(authenticated_page, faker):
    """
    Validates the end-to-end flow from selecting a permit in the listing
    to editing its General Information details.
    """
    # 1. Initialize Page Objects
    permit_page = PermitListingPage(authenticated_page)
    gen_info_page = GeneralInformationPage(authenticated_page)

    # Generate dynamic data using Faker
    random_block = str(faker.random_int(min=10, max=999))
    random_lot = str(faker.random_int(min=1, max=50))

    # 2. Navigate to Listing, search, and enter Edit mode
    record_data = permit_page.search_and_edit_permit("HCL")
    print(f"Editing Permit: {record_data['app_no']}")

    # 3. Perform General Information Updates (Fill Block/Lot & Update)
    gen_info_page.update_block_and_lot(random_block, random_lot)

    # 4. Verify Modal Links (Link Permits, LONI, Pre-App)
    gen_info_page.verify_link_modals()
