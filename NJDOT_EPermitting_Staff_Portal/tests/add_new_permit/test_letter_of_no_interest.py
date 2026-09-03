import pytest
from pages.application_permit_info.permit_listing_page import PermitListingPage
from pages.application_permit_info.add_new_permit.letter_of_no_interest_page import LetterOfNoInterestPage


def test_create_letter_of_no_interest_permit(authenticated_page):
    """
    Independent test case for creating a Letter of No Interest permit per user codegen flow:
    1. Navigate to Permit Listing and open 'Add New Permit' modal.
    2. Select 'Letter of No Interest' application type.
    3. Fill General Information (Department, Case Manager - 1st option for dropdowns).
    4. Fill Location Information (Route, Milepost Start, Milepost End, Suffix, Direction - 1st option for dropdowns).
    5. Click Save, verify no validation errors, and check post-save page containers.
    """
    listing_page = PermitListingPage(authenticated_page)
    add_loni_page = LetterOfNoInterestPage(authenticated_page)

    # 1. Navigation
    listing_page.navigate_to_permit_listing()
    listing_page.open_add_new_permit_modal()

    # 2. Application Type Selection
    listing_page.select_application_type("Letter of No Interest")

    # 3. Form Entry using dynamic Faker data
    test_data = {
        "milepost_start": "1",
        "milepost_end": "2"
    }

    add_loni_page.create_letter_of_no_interest_permit(test_data)
