import pytest
from playwright.sync_api import Page
from pages.violations.add_violation_page import AddViolationPage


class TestAddViolation:

    def test_add_violation_flow(self, authenticated_page: Page):
        """
        Verifies the complete Add Violation flow:
        1. Navigates to Violations Listing.
        2. Clicks Add Violation.
        3. Fills out status & inspector, then clicks Save.
        4. Links to Permit & links to Dealer for 'vansh'.
        5. Assesses violation reasons (checks first checkbox).
        6. Enters Sign Details (Face Height=4, Face Width=5, Sign Type=Roof, Material=Pylon).
        7. Adds an Inspection (Inspector=Cassandra Gallagher, Status=Corrected).
        8. Verifies Historic Violations modal layout.
        9. Sets Removal Information dates to current date and saves the entire form.
        10. Navigates back, searches by dealer name, and verifies it is in the list.
        """
        add_page = AddViolationPage(authenticated_page)

        # 1. Navigate to Violations Listing
        add_page.navigate_to_violations_listing()

        # 2. Click Add Violation
        add_page.click_add_violation()

        # 3. Fill Status & Inspector, and Save to initialize details view
        add_page.fill_violation_status(status="Final Notice Issued", inspector="Andrew Feller")

        # 4. Link to Permit & Dealer
        add_page.link_to_permit(dealer_name="vansh")
        add_page.link_to_dealer(dealer_name="vansh")

        # 5. Add Violation Reason
        add_page.add_violation_reason()

        # 6. Fill Sign Details
        add_page.fill_sign_details(height="4", width="5", sign_type="Roof", material="Pylon")

        # 7. Add Inspection Info
        add_page.add_inspection(inspector="Cassandra Gallagher", status="Corrected")

        # 8. Link Historic Violations
        add_page.verify_historic_violations_modal()

        # 9. Fill Removal dates and Save final record
        add_page.fill_removal_info_and_save()

        # 10. Return to list and verify the record is displayed successfully
        add_page.go_back_and_verify_record_listed(dealer_name="vansh")
