import pytest
import logging
from playwright.sync_api import Page
from pages.renewals.license_renewal_page import LicenseRenewalPage

logger = logging.getLogger(__name__)

class TestLicenseRenewal:

    def test_license_renewal_flow(self, authenticated_page: Page):
        """
        Verifies the complete License Renewal workflow:
        1. Navigation and initial heading validations.
        2. Generate Pre-Renewal document & dismissal of confirmation alerts.
        3. Generate Renewal documents & confirmation alerts.
        4. Generate Late Notices & confirmation alerts.
        5. Triggering Status Updates ('License Not' and 'License Cancelled').
        6. Setting Date Range filters to 3 months back dynamically.
        7. Filtering by Type 'Document'.
        8. Reading the first record title dynamically and performing a precise Search filter validation.
        9. Triggering the Document View popup and closing the window successfully.
        10. Clicking Edit on the log entry, verifying Log Details form loaded, and saving.
        """
        renewal_page = LicenseRenewalPage(authenticated_page)

        # 1. Navigate to License Renewal
        renewal_page.navigate_to_license_renewal()

        # 2. Generate Pre-Renewal
        renewal_page.generate_pre_renewal()

        # 3. Generate Renewal
        renewal_page.generate_renewal()

        # 4. Generate Late Notices
        renewal_page.generate_late_notices()

        # 5. Status Updates
        renewal_page.status_update_license_not()
        renewal_page.status_update_license_cancelled()

        # 6. Select Date Range (three months ago to current date)
        renewal_page.select_date_range_three_months_ago()

        # 7. Filter by Type "Document"
        renewal_page.filter_by_type_document()

        # 8. Dynamic Name Search & Validation
        # First search by 'russ media' as shown in codegen, then verify dynamically
        logger.info("Performing initial search for 'russ media'")
        renewal_page.search_by_name("russ media")
        
        first_name = renewal_page.get_first_record_name()
        logger.info(f"Filtering grid dynamically by record name: '{first_name}'")
        renewal_page.search_by_name(first_name)
        
        searched_name = renewal_page.get_first_record_name()
        assert first_name in searched_name or searched_name in first_name, \
            f"Grid search mismatch: expected record to match '{first_name}', got '{searched_name}'"

        # 9. View popup and close it
        renewal_page.view_and_close_first_record_document()

        # 10. Edit and save first record details
        renewal_page.edit_and_save_first_record()
