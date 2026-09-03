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
    
    # 2. Navigate to Listing, search, and enter Edit mode
    listing_page.search_and_edit_permit("HCL")

    # 3. Transition to Applicant/Permittee tab and verify initial layout
    applicant_page.navigate_to_applicant_info()
    applicant_page.verify_initial_layout()

    # 4. Link Contact to Permit
    applicant_page.link_contact_to_permit(query="HWL")

    # 5. Edit Contact and Save details
    applicant_page.edit_first_contact_and_save()
