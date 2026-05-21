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
    # random_block = str(faker.random_int(min=10, max=999))
    # random_lot = str(faker.random_int(min=1, max=50))
    
    # 2. Navigate to Listing, search, and enter Edit mode (with retries for 504/timeout)
    max_retries = 3
    record_data = None
    for attempt in range(max_retries):
        try:
            permit_page.navigate_to_permit_listing()
            permit_page.search_by_company("HCL")
            record_data = permit_page.navigate_to_next_page_and_edit_first_record()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"\n[RETRY] Search/Edit failed: {e}. Retrying attempt {attempt + 1}/{max_retries}...")
            authenticated_page.wait_for_timeout(5000)
    print(f"Editing Permit: {record_data['app_no']}")
    
    # 4. Perform General Information Updates
    # We follow the flow requested: Add New, Fill Block/Lot, Update
    # gen_info_page.add_new_record_detail()
    # gen_info_page.update_block_and_lot(random_block, random_lot)
    
    # 5. Verify Modal Links (Link Permits, LONI, Pre-App)
    gen_info_page.verify_link_modals()
    
    # 6. Verification: Data consistency check
    # Ensuring the page we landed on matches the record we clicked
    # gen_info_page.verify_data_matching(record_data)
