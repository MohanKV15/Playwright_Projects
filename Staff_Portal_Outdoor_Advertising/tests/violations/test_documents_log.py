import os
import tempfile
import pytest
from playwright.sync_api import Page
from pages.violations.documents_and_log_page import ViolationDocumentsAndLogPage


class TestViolationDocumentsAndLog:

    def test_documents_and_log_flow(self, authenticated_page: Page, faker):
        """
        Verifies the complete Violation Documents and Log workflow:
        1. Navigates to Violations Listing.
        2. Filters by dealer name 'vansh'.
        3. Edits the first matching record ('2026-618 Vansh tech pvt ltd').
        4. Navigates to the 'Documents and Log' tab.
        5. Attaches a document with today's date using Faker title and description.
        6. Verifies the attached document title is displayed in the table.
        7. Adds a communication entry with today's date using Faker subject and description.
        8. Verifies the communication subject is displayed in the table.
        9. Clicks Send Email, verifies fields overlay, and cancels.
        10. Clicks view communication details button (nth(5)), verifies overlay, and cancels.
        """
        docs_log_page = ViolationDocumentsAndLogPage(authenticated_page)

        # 1. Navigate to Violations Listing
        docs_log_page.navigate_to_violations_listing()

        # 2. Search by dealer name 'vansh'
        docs_log_page.search_by_dealer_name(dealer_name="vansh")

        # 3. Edit first record
        docs_log_page.click_edit_on_first_record()

        # 4. Navigate to Documents and Log tab
        docs_log_page.navigate_to_documents_log()

        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test violation attachment document contents.")
            temp_file_path = f.name

        # Generate custom dynamic test data using Faker
        doc_title = f"Doc-{faker.word()}-{faker.random_int(100, 999)}"
        doc_desc = faker.sentence()
        comm_subject = f"Comm-{faker.sentence(nb_words=2)}"
        comm_desc = faker.paragraph(nb_sentences=1)

        try:
            # 5. Attach document
            docs_log_page.attach_document(temp_file_path, title=doc_title, desc=doc_desc)

            # 6. Verify attached document is visible in grid
            docs_log_page.verify_record_in_grid(doc_title)

            # 7. Add communication entry
            docs_log_page.add_communication(subject=comm_subject, description=comm_desc)

            # 8. Verify communication subject is visible in grid
            docs_log_page.verify_record_in_grid(comm_subject)

            # 9. Click Send Email, verify overlay, and cancel
            docs_log_page.click_send_email_and_cancel()

            # 10. Click view communication details, verify overlay, and cancel
            docs_log_page.click_view_communication_details_and_cancel()

        finally:
            # Clean up the temp file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
