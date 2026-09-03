import pytest
from pages.submit_application.submit_application_page import SubmitApplicationPage
from pages.submit_application.permit_application_page import PermitApplicationPage
from pages.submit_application.payment_page import PaymentPage

@pytest.mark.smoke
def test_permit_application_popup_flow(authenticated_page):
    """
    Validates clicking 'Permit Application' launches the warning alert dialog,
    verifies it displays the domain name, and dismisses it successfully.
    """
    # 1. Initialize pages
    submit_app_page = SubmitApplicationPage(authenticated_page)
    permit_app_page = PermitApplicationPage(authenticated_page)
    payment_page = PaymentPage(authenticated_page)
    
    # 2. Open the 'Submit Application' panel
    submit_app_page.click_submit_application()
    
    # 3. Click the 'Permit Application' button (#btnPermitApp)
    permit_app_page.click_permit_application()
    
    # 4. Verify the domain dialog is visible
    permit_app_page.verify_domain_dialog_visible()
    
    # 5. Dismiss the dialog
    permit_app_page.dismiss_dialog()

    # 6. Fill and submit the permit application form
    permit_app_page.fill_permit_application_form()
    
    # 7. Verify navigation to the payment gateway
    authenticated_page.wait_for_url("**/CommonCheckout/**", timeout=30000)
    
    # 8. Complete Payment Gateway steps
    print("\n[INFO] Starting payment gateway flow...")
    payment_page.select_credit_debit_card()
    payment_page.fill_customer_information()
    payment_page.fill_card_details()
    payment_page.submit_payment()
    payment_page.verify_payment_success()
    print("[INFO] Payment gateway flow completed successfully!")
