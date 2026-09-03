import json
from utils.config import Config
from pages.login.login_page import LoginPage
from pages.submit_application.submit_application_page import SubmitApplicationPage
from pages.submit_application.license_application_page import LicenseApplicationPage
from pages.submit_application.payment_page import PaymentPage

def test_license_application_payment_flow(page):
    """
    Validates clicking 'License Application', filling the form, submitting it,
    and navigating through the payment gateway to completion.
    Uses a dedicated account specifically for License Application.
    """
    # 1. Perform Dedicated Login
    login_page = LoginPage(page)
    
    login_data_path = Config.PROJECT_ROOT / "testdata" / "login_data.json"
    with open(login_data_path) as f:
        users = json.load(f)["valid_users"]
        # Find the license-specific user
        license_user = next((u for u in users if u.get("type") == "license"), users[0])
        
    login_page.load(Config.LOGIN_URL)
    login_page.login(email=license_user["email"], password=license_user["password"])
    
    # Wait for the main accounts portal link and click into Outdoor Advertising
    login_page.outdoor_advertising_link.wait_for(state="visible", timeout=Config.TIMEOUT)
    login_page.select_outdoor_advertising()

    # 2. Initialize pages
    submit_app_page = SubmitApplicationPage(page)
    license_app_page = LicenseApplicationPage(page)
    payment_page = PaymentPage(page)
    
    # 3. Open the 'Submit Application' panel
    submit_app_page.click_submit_application()
    
    # 4. Click the 'License Application' button
    license_app_page.click_license_application()
    
    # 5. Fill and submit the license application form
    license_app_page.fill_license_application_form()
    
    # 6. Verify navigation to the payment gateway
    page.wait_for_url("**/CommonCheckout/**", timeout=30000)
    
    # 7. Complete Payment Gateway steps
    print("\n[INFO] Starting payment gateway flow...")
    payment_page.select_credit_debit_card()
    payment_page.fill_customer_information()
    payment_page.fill_card_details()
    payment_page.submit_payment()
    payment_page.verify_payment_success()
    print("[INFO] Payment gateway flow completed successfully!")
