import pytest
from pages.submit_application.submit_application_page import SubmitApplicationPage

def test_submit_application_options_visibility(authenticated_page):
    """
    Validates that the 'Submit Application' panel displays all options
    (Permit Application, License Application, Permit Transfer, Name Change).
    """
    # 1. Initialize SubmitApplicationPage
    submit_app_page = SubmitApplicationPage(authenticated_page)
    
    # 2. Open the 'Submit Application' panel
    submit_app_page.click_submit_application()
    
    # 3. Verify the options are visible
    submit_app_page.verify_application_options_visible()
