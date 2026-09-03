import pytest
from pages.payment_activity.payment_activity_page import PaymentActivityPage

def test_payment_activity_filters_and_export(authenticated_page):
    """
    Validates navigating to Payment Activity, interacting with the time period 
    filters, paginating, exporting records, and returning safely.
    """
    # 1. Initialize POM
    payment_page = PaymentActivityPage(authenticated_page)
    
    # 2. Open the Payment Activity module
    payment_page.open()
    
    # 3. Dynamically iterate through the first 3 dropdown filters (testing multiple states)
    payment_page.test_first_three_time_periods(max_records=3)
    
    # 3.5 Re-select the first dropdown option ('Last 6 months') to ensure there is a large dataset to paginate
    payment_page.select_time_period("Last 6 months")
    
    # 4. Paginate through all the records using fast navigation
    payment_page.go_to_last_page()
    
    # 5. Test the Export functionality (downloads file securely)
    payment_page.export_activity()
    
    # 6. Click back to return to the dashboard
    payment_page.go_back()
    
    print("[INFO] Payment Activity functionality tested successfully!")
