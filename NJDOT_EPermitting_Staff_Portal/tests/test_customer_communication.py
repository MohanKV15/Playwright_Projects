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
    
    # 2. Navigate to Listing, search, and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Customer Communications tab and verify initial layout
    comms_page.navigate_to_customer_communications()
    comms_page.verify_initial_layout()

    # 4. Add Customer Communication details
    comms_page.add_customer_communication(
        comm_type="Permit Communication",
        comm_status="Waiting for Response",
        review_person="Steve Ruskan",
        message=test_message
    )
