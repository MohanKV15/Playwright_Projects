import pytest
from playwright.sync_api import Page
from pages.renewals.permit_renewal_page import PermitRenewalPage

class TestPermitRenewal:

    def test_permit_renewal_flow(self, authenticated_page: Page):
        """
        Verifies the complete Permit Renewal workflow:
        1. Navigation and initial heading validations.
        2. Generate Pre-Renewal document & dismissal of Kendo alerts.
        3. Generate Renewal documents & error exception alerts handling.
        4. Generate Paper Renewal & warning popup handling.
        5. Triggering Status Updates ('Permit Not' and 'Permit Cancelled').
        6. Setting Date Range filters to 3 months back dynamically.
        7. Filtering by Type 'Document'.
        8. Reading the first record title dynamically and performing a precise Search filter validation.
        9. Triggering the Document View popup and closing the window successfully.
        10. Clicking Edit on the log entry, verifying Log Details form loaded, and saving.
        """
        renewal_page = PermitRenewalPage(authenticated_page)

        # 1. Navigate to Permit Renewal
        renewal_page.navigate_to_permit_renewal()

        # 2. Generate Pre-Renewal
        renewal_page.generate_pre_renewal()

        # 3. Generate Renewal
        renewal_page.generate_renewal()

        # 4. Generate Paper Renewal
        renewal_page.generate_paper_renewal()

        # 5. Status Updates
        renewal_page.status_update_permit_not()
        renewal_page.status_update_permit_cancelled()

        # 6. Select Date Range (three months ago to current date)
        renewal_page.select_date_range_three_months_ago()

        # 7. Filter by Type "Document"
        renewal_page.filter_by_type_document()

        # 8. Dynamic Name Search & Validation
        first_name = renewal_page.get_first_record_name()
        renewal_page.search_by_name(first_name)
        
        searched_name = renewal_page.get_first_record_name()
        assert first_name in searched_name or searched_name in first_name, \
            f"Grid search mismatch: expected record to match '{first_name}', got '{searched_name}'"

        # 9. View popup and close it
        renewal_page.view_and_close_first_record_document()

        # 10. Edit and save first record details
        renewal_page.edit_and_save_first_record()
