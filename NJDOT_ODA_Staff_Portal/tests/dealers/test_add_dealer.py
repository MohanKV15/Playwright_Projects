import pytest
import uuid
from faker import Faker
from playwright.sync_api import Page
from pages.dealers.add_details_dealer_page import AddDetailsDealerPage

class TestAddDealer:
    
    def test_add_dealer_flow(self, authenticated_page: Page):
        """
        Verifies that a user can:
        1. Navigate to Dealers -> Dealer Listing -> Add Dealer.
        2. Fill in the Dealer details form (including Billing Address details).
        3. Save the record successfully and dismiss the Kendo success dialog.
        4. Verify that all saved details are correctly populated and displayed on the details page.
        """
        fake = Faker()
        dealer_page = AddDetailsDealerPage(authenticated_page)
        
        # 1. Generate dynamic test data using Faker and UUID to prevent database duplicates
        unique_id = uuid.uuid4().hex[:6]
        test_details = {
            "dealer_name": f"Test Dealer {fake.company()} {unique_id}"[:100],  # Truncate to safety limit if any
            "mailing_address": f"Mailing {fake.street_address()}"[:100],
            "city": fake.city()[:50],
            "zip_code": fake.zipcode(),
            "phone": fake.numerify("###-###-####"),
            "email": f"test_{unique_id}@{fake.free_email_domain()}",
            "is_corporation": False,
            "same_billing": False,  # Set to False to verify billing address fields workflow
            "billing_address": f"Billing {fake.street_address()}"[:100],
            "billing_city": fake.city()[:50],
            "billing_zip_code": fake.zipcode()
        }
        
        # 2. Navigate to the Add Dealer form
        dealer_page.navigate_to_add_dealer()
        
        # 3. Fill in the dealer details (the page object handles first option selection for dropdowns)
        final_saved_details = dealer_page.fill_dealer_details(test_details)
        
        # 4. Save and confirm
        dealer_page.save_dealer()
        
        # 5. Verify the saved details match the values populated on the form
        dealer_page.verify_saved_details(final_saved_details)
