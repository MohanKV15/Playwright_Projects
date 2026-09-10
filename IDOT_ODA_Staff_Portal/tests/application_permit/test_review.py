import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.review_page import ReviewPage


@allure.epic("Staff Portal")
@allure.feature("Application & Permits")
@allure.story("Reviewers Assigned")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.application_permit
@pytest.mark.review
@pytest.mark.smoke
def test_review_full_workflow(
    authenticated_review: ReviewPage,
):
    """
    Test Case ID: TC_STAFF_REV_001
    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit context.
    2. Navigate to 'Review' via sidebar menu link and verify listing elements.
    3. Create and assign reviewer (present date, 1st dropdown options, Faker comments, save, OK).
    4. Verify newly assigned reviewer appears in Reviewers Assigned grid table.
    """
    with allure.step("1. Activate permit session and navigate to Review"):
        authenticated_review.navigate_to_review(company_name="IDOTOAtest2")

    with allure.step("2. Create and assign reviewer with dynamic role and Faker comments"):
        reviewer_data = authenticated_review.create_reviewer()
        assert all(reviewer_data.values()), f"Reviewer assignment data was incomplete: {reviewer_data}"

    with allure.step("3. Verify newly assigned reviewer appears in Reviewers Assigned grid table"):
        matching_row = authenticated_review.verify_reviewer_in_grid(
            expected_reviewer=reviewer_data["reviewer"],
            expected_role=reviewer_data["role"],
        )
        assert matching_row, f"Assigned reviewer '{reviewer_data['reviewer']}' was not found in grid"


