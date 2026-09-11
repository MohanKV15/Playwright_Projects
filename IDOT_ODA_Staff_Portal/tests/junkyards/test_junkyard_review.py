import allure
import pytest
from IDOT_ODA_Staff_Portal.pages.junkyards.review_page import JunkyardReviewPage


@allure.epic("Staff Portal")
@allure.feature("Junkyards")
@allure.story("Junkyard Reviewers Assignment & Form Verification")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.junkyards
@pytest.mark.junkyard_review
@pytest.mark.regression
def test_junkyard_review_full_workflow(
    authenticated_junkyard_review: JunkyardReviewPage,
):
    """
    Test Case ID: TC_STAFF_JUNKYARD_REVIEW_001
    Workflow:
    1. Authenticate and navigate to 'Junkyard/Permit Search' via sidebar menu.
    2. Search permit records by company name ('IDOTOAtest2') and select 1st record row.
    3. Navigate to Review page via Junkyards sidebar menu.
    4. Verify page elements ('Junkyard Details Permit', 'Reviewers Assigned', grid content).
    5. Click 'Add Reviewer', set present day date, populate Review Type ('Amendment'), Reviewer ('Bill Siders'), Role ('Director - Outdoor Advertising').
    6. Fill Instructions/Comments with dynamic Faker library string and submit form.
    7. Assert 'Operation completed', confirm OK popup, and verify #ReviewAssignmentsList grid.
    """
    page_obj = authenticated_junkyard_review

    with allure.step("1-3. Search company, select record, and navigate to Junkyard Review"):
        record_info = page_obj.navigate_to_junkyard_review(company_name="IDOTOAtest2")
        assert record_info, "Failed to select 1st record row to activate permit context"

    with allure.step("4. Assert Reviewers Assigned listing page elements"):
        page_obj.verify_junkyard_review_page_loaded()

    with allure.step("5-7. Click Add Reviewer, set present day date & Faker comment, save form, and confirm OK popup"):
        reviewer_data = page_obj.create_reviewer(
            review_type_name="Amendment",
            reviewer_name="Bill Siders",
            role_name="Director - Outdoor Advertising",
        )
        assert reviewer_data["review_type"], "Review Type selection failed"
        assert reviewer_data["reviewer"], "Reviewer selection failed"
