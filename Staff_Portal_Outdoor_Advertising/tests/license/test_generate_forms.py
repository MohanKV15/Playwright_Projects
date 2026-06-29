import pytest
from playwright.sync_api import Page
from pages.license.generate_forms_page import LicenseGenerateFormsPage


class TestLicenseGenerateForms:

    def test_generate_forms_flow(self, authenticated_page: Page):
        """Verify navigation to License Listing, editing the first record, and verifying Generate Forms tab layout."""
        generate_forms_page = LicenseGenerateFormsPage(authenticated_page)

        # 1. Navigate to License Listing
        generate_forms_page.navigate_to_license_listing()

        # 2. Search for dealer "vansh" and edit the first matching row
        generate_forms_page.search_and_edit_first_license(dealer_name="vansh")

        # 3. Navigate to Generate Forms tab and verify layout/headings
        generate_forms_page.navigate_to_generate_forms()

        # 4. Verify that all expected document/form templates are present in the grid
        expected_docs = [
            "Dealers - License",
            "License - Non Renewal Letter",
            "License - Outdoor License Application",
            "Licenses - Notice of Renewal License"
        ]
        generate_forms_page.verify_documents_in_grid(expected_docs)

