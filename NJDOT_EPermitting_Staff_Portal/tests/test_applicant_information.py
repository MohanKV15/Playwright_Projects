import allure
import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.applicant_information_page import ApplicantInformationPage


@allure.epic("NJDOT E-Permitting")
@allure.feature("Application & Permit Information")
@allure.story("Applicant / Permittee Workflow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.applicant_information
@pytest.mark.smoke
@pytest.mark.authenticated
def test_applicant_information_flow(authenticated_page):
    """
    Test Case ID: TC_NJDOT_APPLICANT_001
    Verifies the complete Applicant/Permittee tab workflow:
    1. Search for permit by company "HCL" and open the first record.
    2. Transition to Applicant/Permittee tab and verify layout.
    3. Link a contact matching query "HWL".
    4. Edit the first contact and save the contact details form.
    """
    listing_page = PermitListingPage(authenticated_page)
    applicant_page = ApplicantInformationPage(authenticated_page)

    with allure.step("1. Search for permit by company 'HCL' and enter Edit mode"):
        listing_page.search_and_edit_permit("HCL")

    with allure.step("2. Transition to Applicant/Permittee tab and verify initial layout"):
        applicant_page.navigate_to_applicant_info()
        applicant_page.verify_initial_layout()

    with allure.step("3. Link contact to permit matching query 'HWL'"):
        applicant_page.link_contact_to_permit(query="HWL")

    with allure.step("4. Edit first contact and save contact details form"):
        applicant_page.edit_first_contact_and_save()

