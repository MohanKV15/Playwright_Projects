import pytest
from IDOT_ODA_Staff_Portal.pages.application_permit.review_page import ReviewPage


@pytest.mark.application_permit
@pytest.mark.review
@pytest.mark.smoke
def test_review_full_workflow(
    authenticated_review: ReviewPage,
):
    """
    Test Case: Review and Reviewers Assigned Workflow

    Workflow:
    1. Authenticate and search Company Name ('IDOTOAtest2') to activate permit context.
    2. Navigate to 'Review' via sidebar menu link.
    3. Verify listing page loads with 'Application Details Permit', 'Reviewers Assigned' heading, and .k-grid-content.
    4. Click 'Add Reviewer' and verify 'Assign Reviewer Date Assigned' form loads.
    5. Set Date Assigned using present day date.
    6. Dynamically select the 1st valid dropdown options for:
       - Review Type (#Text_PlaceHolder1)
       - Reviewer (#Review_By)
       - Role (#Review_Unit)
    7. Populate 'Instructions/Comments' using dynamic Faker text.
    8. Click 'Save' and verify 'Operation completed' confirmation dialog appears.
    9. Click 'OK' to dismiss the confirmation dialog.
    10. Verify the newly assigned reviewer is displayed in the Reviewers Assigned grid table.
    """
    review_page = authenticated_review

    # 1. Activate permit session and navigate to Review
    review_page.navigate_to_review(company_name="IDOTOAtest2")

    # 2. Create and assign reviewer (present date, 1st dropdown options, Faker comments, save, OK)
    reviewer_data = review_page.create_reviewer()
    assert all(reviewer_data.values()), f"Reviewer assignment data was incomplete: {reviewer_data}"

    # 3. Verify newly assigned reviewer appears in Reviewers Assigned grid table
    matching_row = review_page.verify_reviewer_in_grid(
        expected_reviewer=reviewer_data["reviewer"],
        expected_role=reviewer_data["role"],
    )
    assert matching_row, f"Assigned reviewer '{reviewer_data['reviewer']}' was not found in grid"

