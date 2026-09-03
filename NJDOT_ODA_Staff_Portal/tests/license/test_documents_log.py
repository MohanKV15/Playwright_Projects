import os
import tempfile
import pytest
from playwright.sync_api import Page
from pages.license.generate_forms_page import LicenseGenerateFormsPage
from pages.license.documents_and_log_page import LicenseDocumentsAndLogPage


class TestLicenseDocumentsAndLog:

    def test_documents_and_log_flow(self, authenticated_page: Page, faker):
        """Verify navigation, attaching document, adding communication, and compiling package."""
        generate_forms_page = LicenseGenerateFormsPage(authenticated_page)
        docs_log_page = LicenseDocumentsAndLogPage(authenticated_page)

        # 1. Navigate to License Listing
        generate_forms_page.navigate_to_license_listing()

        # 2. Search for dealer "vansh" and edit the first matching row
        generate_forms_page.search_and_edit_first_license(dealer_name="vansh")

        # 3. Navigate to Documents and Log tab
        docs_log_page.navigate_to_documents_log()

        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test attachment document contents.")
            temp_file_path = f.name

        # Generate custom dynamic test data using Faker
        doc_title = f"Doc-{faker.word()}-{faker.random_int(100, 999)}"
        doc_desc = faker.sentence()
        comm_subject = f"Comm-{faker.sentence(nb_words=2)}"
        comm_desc = faker.paragraph(nb_sentences=1)

        try:
            # 4. Attach document with today's date using Faker values
            docs_log_page.attach_document(temp_file_path, title=doc_title, desc=doc_desc)

            # 5. Add a communication entry using Faker values
            docs_log_page.add_communication(subject=comm_subject, description=comm_desc)

            # 6. Verify tab visual elements/headings
            docs_log_page.verify_headings()

            # 7. Create a document package
            docs_log_page.create_package()

        finally:
            # Clean up the temp file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
