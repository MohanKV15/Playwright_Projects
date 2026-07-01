import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.customer_communication_page import CustomerCommunicationPage

def test_customer_communication_flow(authenticated_page, faker):
    """
    Verifies the complete Customer Communications tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Customer Communications tab and verify layout.
    3. Add a new customer communication details log and send.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    comms_page = CustomerCommunicationPage(authenticated_page)
    
    # Generate dynamic test values using Faker to avoid state conflict
    test_message = f"Auto Msg - {faker.sentence()}"
    
    # 2. Search for company "HCL" and open the record in Edit mode
    max_retries = 3
    for attempt in range(max_retries):
        try:
            listing_page.navigate_to_permit_listing()
            listing_page.search_by_company("HCL")
            listing_page.navigate_to_next_page_and_edit_first_record()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"\n[RETRY] Search/Edit failed: {e}. Retrying attempt {attempt + 1}/{max_retries}...")
            authenticated_page.wait_for_timeout(5000)

    # 3. Transition to Customer Communications tab and verify initial layout
    comms_page.navigate_to_customer_communications()
    comms_page.verify_initial_layout()

    # 4. Add Customer Communication details
    comms_page.add_customer_communication(
        comm_type="Additional Info Requested",
        comm_status="Waiting for Response",
        review_person="Steve Ruskan",
        message=test_message
    )
