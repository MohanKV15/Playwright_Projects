import pytest
from pages.submit_application.submit_application_page import SubmitApplicationPage
from pages.submit_application.permit_transfer_page import PermitTransferPage
from pages.submit_application.payment_page import PaymentPage

def test_permit_transfer_payment_flow(authenticated_page):
    """
    Validates clicking 'Permit Transfer', filling the form, submitting it,
    and navigating through the payment gateway to completion.
    """
    # 1. Initialize pages
    submit_app_page = SubmitApplicationPage(authenticated_page)
    permit_transfer_page = PermitTransferPage(authenticated_page)
    payment_page = PaymentPage(authenticated_page)
    
    # 2. Open the 'Submit Application' panel
    submit_app_page.click_submit_application()
    
    # 3. Click the 'Permit Transfer' button
    permit_transfer_page.click_permit_transfer()
    
    # 4. Fill and submit the permit transfer form
    permit_transfer_page.fill_permit_transfer_form()
    
    # 5. Verify navigation to the payment gateway
    authenticated_page.wait_for_url("**/CommonCheckout/**", timeout=30000)
    
    # 6. Complete Payment Gateway steps
    print("\n[INFO] Starting payment gateway flow...")
    payment_page.select_credit_debit_card()
    payment_page.fill_customer_information()
    payment_page.fill_card_details()
    payment_page.submit_payment()
    payment_page.verify_payment_success()
    print("[INFO] Payment gateway flow completed successfully!")
