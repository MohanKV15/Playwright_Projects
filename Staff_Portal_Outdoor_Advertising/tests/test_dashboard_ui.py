import pytest
from playwright.sync_api import Page, expect
from pages.dashboard.dashboard_page import DashboardPage

class TestDashboardUI:
    
    def test_search_by_dealer_name(self, authenticated_page: Page):
        """
        Verifies that a user can successfully search by Dealer Name 
        on the dashboard and that the results grid appears.
        """
        # The authenticated_page fixture handles the login and state injection automatically!
        dashboard_page = DashboardPage(authenticated_page)
        
        # 1. Ensure the Dashboard has fully loaded
        dashboard_page.assert_dashboard_loaded()
        
        # 2. Execute the Dealer Name search as requested by codegen
        dashboard_page.search_by_dealer_name("vansh")
        
        # 3. Assert the Permit List Grid becomes visible with the results
        dashboard_page.assert_search_results_visible()
