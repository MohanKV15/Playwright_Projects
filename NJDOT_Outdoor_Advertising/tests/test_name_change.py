import pytest
from pages.submit_application.submit_application_page import SubmitApplicationPage
from pages.submit_application.name_change_page import NameChangePage

def test_name_change_flow(authenticated_page):
    """
    Validates clicking 'Name Change', filling the form, submitting it,
    and verifying the success screen.
    """
    # 1. Initialize pages
    submit_app_page = SubmitApplicationPage(authenticated_page)
    name_change_page = NameChangePage(authenticated_page)
    
    # 2. Open the 'Submit Application' panel
    submit_app_page.click_submit_application()
    
    # 3. Click the 'Name Change' button
    name_change_page.click_name_change()
    
    # 4. Fill and submit the name change form
    name_change_page.fill_name_change_form()
    
    # 5. Verify the success screen and return to dashboard
    name_change_page.verify_success_and_return()
    
    print("[INFO] Name Change flow completed successfully!")
