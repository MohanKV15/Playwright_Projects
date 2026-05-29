import logging
from playwright.sync_api import Page, expect
from faker import Faker
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class PermitTransferPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation
        self.permit_transfer_button = page.locator("#btnPermitTransfer")
        
        # Headings
        self.main_heading = page.get_by_role("heading", name="Permit Transfer Application")
        self.app_info_heading = page.get_by_role("heading", name="Application Information")
        
        # Form Fields
        self.permit_no = page.locator("#Appl_Transfer_Permit_No")
        self.permit_from = page.locator("#Appl_Transfer_Permit_From")
        
        # Checkboxes
        self.ack_checkbox_1 = page.locator(".k-checkbox-label").first
        self.ack_checkbox_2 = page.locator("div:nth-child(3) > .form-check > .k-checkbox-label")
        self.ack_checkbox_3 = page.locator("div:nth-child(5) > div:nth-child(2) > .form-check > .k-checkbox-label")
        
        # Signature
        self.signer_name = page.locator("#SignName")
        self.signer_title = page.locator("#SignTitle")
        
        # Submission
        self.complete_payment_btn = page.get_by_role("button", name=" Complete Payment")
        self.ok_button = page.get_by_role("button", name="OK")

    def click_permit_transfer(self) -> None:
        """Clicks the 'Permit Transfer' button to begin submission."""
        import pytest
        logger.info("Clicking '#btnPermitTransfer' button to start permit transfer application")
        self.permit_transfer_button.click()
        
        # Handle the potential STOP dialog for existing issues (similar to license app)
        try:
            stop_dialog_ok = self.page.get_by_role("button", name="OK")
            # Quickly check if a blocking dialog appeared
            stop_dialog_ok.wait_for(state="visible", timeout=3000)
            logger.warning("STOP dialog detected. Clicking OK...")
            stop_dialog_ok.click()
            pytest.skip("Skipping test: The account is blocked from submitting this application.")
        except Exception as e:
            if "Skipping test" in str(e):
                raise e
            pass
            
        logger.info("Validating page headings...")
        expect(self.main_heading).to_be_visible(timeout=10000)
        expect(self.app_info_heading).to_be_visible(timeout=10000)

    def fill_permit_transfer_form(self, file_path: str = r"C:\Users\Mohan(QAQC)\Downloads\Smallpdf.pdf") -> None:
        """Fills the permit transfer form with dynamic Faker test data."""
        fake = Faker()
        
        logger.info("Filling Application Information...")
        self.permit_no.click()
        # Generate a fake 5-6 digit permit number
        self.permit_no.fill(str(fake.random_number(digits=6, fix_len=True)))
        
        self.permit_from.click()
        self.permit_from.fill(fake.company())
        
        logger.info(f"Uploading file to Document Upload section: {file_path}")
        # Robust Kendo UI upload interaction targeting the first upload dropzone
        self.page.locator(".k-upload").nth(0).locator("input[type='file']").first.set_input_files(file_path)
        
        # Wait a moment for upload to register visually
        self.page.wait_for_timeout(2000)
        
        logger.info("Checking acknowledgment checkboxes...")
        self.ack_checkbox_1.click()
        self.ack_checkbox_2.click()
        self.ack_checkbox_3.click()
        
        logger.info("Entering certification signature values...")
        self.signer_name.click()
        self.signer_name.fill(fake.name())
        self.signer_title.click()
        self.signer_title.fill(fake.job())
        
        # Press Tab to trigger the final blur event and enable the submit button
        self.signer_title.press("Tab")
        
        logger.info("Clicking Complete Payment button (using force to bypass Kendo aria-disabled bugs)...")
        self.complete_payment_btn.click(force=True)

        logger.info("Waiting for Record saved successfully popup...")
        self.ok_button.wait_for(state="visible", timeout=30000)
        
        logger.info("Popup appeared -- registering native dialog handler and clicking OK...")
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.ok_button.click()
        logger.info("Clicked OK -- navigating to payment gateway page")
