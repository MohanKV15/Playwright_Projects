import pytest
from playwright.sync_api import Page
from pages.application.permit_Details_page import PermitDetailsPage
from pages.application.generate_forms_page import GenerateFormsPage

class TestGenerateForms:
    
    def test_generate_forms_flow(self, authenticated_page: Page):
        """
        Verifies that a user can search by Dealer Name "vansh", select the 1st record,
        navigate to the Generate Forms tab, generate a form, confirm success modal,
        verify the date in the grid, view/download the form, and paginate up to 10 pages.
        """
        permit_page = PermitDetailsPage(authenticated_page)
        gen_forms_page = GenerateFormsPage(authenticated_page)
        
        # 1. Search for Dealer "vansh" and open the 1st record
        permit_page.search_dealer_on_dashboard("vansh")
        permit_page.open_first_record()
        
        # 2. Navigate to Generate Forms Tab
        gen_forms_page.navigate_to_generate_forms_tab()
        
        # 3. Generate Form and Accept Success popup
        gen_forms_page.generate_form()
        
        # 4. Verify Generated Date in Grid
        gen_forms_page.verify_generated_date_in_grid()
        
        # 5. View Generated Form (nth(3) button / popup)
        gen_forms_page.view_generated_form()
        
        # 6. Paginate list up to 10 pages
        gen_forms_page.paginate_and_check_list(max_pages=10)
