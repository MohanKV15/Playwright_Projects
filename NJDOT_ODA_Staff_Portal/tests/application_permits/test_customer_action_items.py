import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.customer_action_items_page import CustomerActionItemsPage

class TestCustomerActionItems:
    
    def test_add_customer_action_item_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Customer Action Items tab, add a new customer action item,
        and then navigate to the Permit Completion tab.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        customer_page = CustomerActionItemsPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Customer Action Items Tab
        customer_page.navigate_to_customer_action_items()
        
        # 3. Add new Customer Action Item with Faker details
        customer_page.add_customer_action_item()
        
        # 4. Navigate to Permit Completion Tab
        customer_page.navigate_to_permit_completion()
