import pytest
from faker import Faker
from playwright.sync_api import Page
from pages.license.add_license_application_page import AddLicenseApplicationPage


class TestAddLicenseApplication:

    def test_add_license_application_flow(self, authenticated_page: Page):
        """Verify adding a license application, saving it, and verifying it in the listing."""
        add_license_page = AddLicenseApplicationPage(authenticated_page)
        fake = Faker()

        # 1. Navigate to License Listing
        add_license_page.navigate_to_license_listing()

        # 2. Click Add License Application
        add_license_page.click_add_license_application()

        # 3. Search and select dealer in modal
        add_license_page.search_and_select_dealer_in_modal(dealer_name="vansh")

        # 4. Fill agent and non-resident details using Faker
        add_license_page.fill_agent_and_non_resident_details(
            address_2=fake.secondary_address(),
            city=fake.city(),
            state="Alaska",
            zip_code=fake.postcode()[:5],
            first_name=fake.first_name(),
            phone=fake.numerify("###-###-####")
        )

        # 5. Fill license details (dates & status)
        add_license_page.fill_license_details(status="VALID")

        # 6. Click Save and handle popups
        add_license_page.click_save()
        add_license_page.handle_save_popups()

        # 7. Re-navigate, search, and verify result in grid
        add_license_page.search_dealer_and_verify_result(dealer_name="vansh", cell_value="Vansh tech pvt ltd")
