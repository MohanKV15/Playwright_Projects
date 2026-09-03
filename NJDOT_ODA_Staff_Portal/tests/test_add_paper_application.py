import pytest
from playwright.sync_api import Page
from pages.dashboard.add_paper_application_page import AddPaperApplicationPage

class TestAddPaperApplication:
    
    def test_create_new_paper_application(self, authenticated_page: Page):
        """
        Verifies that a user can successfully create a new Paper Application
        using randomized Faker data, whilst strictly asserting the Dealer "vansh".
        """
        paper_app_page = AddPaperApplicationPage(authenticated_page)
        
        # 1. Open the form from the dashboard
        paper_app_page.open_paper_application_form()
        
        # 2. Select the specific Dealer "vansh" as requested
        paper_app_page.select_dealer(dealer_name="vansh")
        
        # 3. Fill the randomized application and property owner details using Faker
        paper_app_page.fill_application_details()
        paper_app_page.fill_property_owner_details()
        
        # 4. Save and assert success
        paper_app_page.save_application()
