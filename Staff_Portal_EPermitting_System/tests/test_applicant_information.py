import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.applicant_information_page import ApplicantInformationPage

def test_applicant_information_flow(authenticated_page):
    """
    Verifies the complete Applicant/Permittee tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Applicant/Permittee tab and verify layout.
    3. Link a contact matching query "HCL".
    4. Edit the first contact and save the contact details form.
    """
    # 1. Initialize Page Objects
    listing_page = PermitListingPage(authenticated_page)
    applicant_page = ApplicantInformationPage(authenticated_page)
    
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

    # 3. Transition to Applicant/Permittee tab and verify initial layout
    applicant_page.navigate_to_applicant_info()
    applicant_page.verify_initial_layout()

    # 4. Link Contact to Permit
    applicant_page.link_contact_to_permit(query="HWL")

    # 5. Edit Contact and Save details
    applicant_page.edit_first_contact_and_save()
