import logging
import pytest
from faker import Faker
from pages.account_management.account_management_page import AccountManagementPage

logger = logging.getLogger(__name__)
fake = Faker()


class TestAccountManagement:
    """
    Test suite for Account Management module in Staff Portal E-Permitting System.
    Validates navigation, searching firm records, adding applicants using dynamic Faker data,
    searching the 1st record in the table, clearing search (refreshing), and editing the 1st record.
    """

    def test_account_management_add_and_edit_applicant(self, authenticated_page):
        """
        Verifies the full Account Management workflow:
        1. Navigate to Account Management and verify initial layout.
        2. Perform firm search (" QA") and clear search filter.
        3. Click 'Add Applicant'.
        4. Fill applicant form with dynamic company/engineer name and city using Faker library.
        5. Save applicant details form.
        6. Dynamically extract 1st record name from table, search for 1st record, clear search filter (refresh), and click edit (#btnDelearListEdit).
        """
        account_page = AccountManagementPage(authenticated_page)

        # Step 1: Navigate to Account Management & Verify Page Layout
        account_page.navigate_to_account_management()
        account_page.verify_account_management_loaded()

        # Step 2: Search for Firm and Clear Search Filter
        account_page.search_firm(" QA")
        account_page.clear_search()

        # Step 3: Open Add Applicant Form
        account_page.click_add_applicant()

        # Step 4 & 5: Generate Dynamic Data with Faker, Fill Form, and Save
        company_name = f"QA_{fake.company()}"
        city = fake.city()
        logger.info(f"Faker generated Company Name: '{company_name}', City: '{city}'")

        account_page.fill_and_save_applicant(company_name=company_name, city=city)

        # Step 6: Dynamically search 1st record in table, clear search (refresh), and edit 1st record
        account_page.search_first_record_refresh_and_edit()
