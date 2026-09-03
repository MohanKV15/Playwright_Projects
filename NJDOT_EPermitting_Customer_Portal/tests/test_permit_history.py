import pytest
from pages.applications_list.permit_history_page import PermitHistoryPage


@pytest.mark.authenticated
def test_permit_history_flow(authenticated_page):

    permit_page = PermitHistoryPage(authenticated_page)

    # Step 1: Navigate
    permit_page.open_permit_history()

    # Step 2: Verify page
    permit_page.verify_history_visible()

    # Step 3: Filter + search
    permit_page.apply_filter_and_search(filter_value="months", keyword="highway")

    # Step 4: Validate records
    has_records = permit_page.verify_records_present()
    if not has_records:
        pytest.skip("⚠️ No permit history records exist for this user/search constraint. Skipping downstream pagination & export assertions.")

    # Step 5: Pagination
    permit_page.validate_pagination()

    # Step 6: Export
    file_path = permit_page.export_file()

    # Step 7: File validation
    assert file_path.exists(), "❌ File not downloaded"
    assert file_path.stat().st_size > 0, "❌ File is empty"