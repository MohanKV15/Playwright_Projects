import logging
from playwright.sync_api import Page, expect
from faker import Faker
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class LicenseApplicationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation
        self.license_app_button = page.locator("#btnLicenseApp")
        
        # Form Fields
        self.placeholder_1 = page.locator("#idComment_PlaceHolder1")
        self.placeholder_2 = page.locator("#idComment_PlaceHolder2")
        
        # Checkboxes (using generic selectors provided in codegen)
        self.ack_checkbox_1 = page.locator(".col-md-12.huddleUp > .form-check > .k-checkbox-label").first
        self.ack_checkbox_2 = page.locator("div:nth-child(7) > div:nth-child(3) > .form-check > .k-checkbox-label")
        
        # Signature
        self.signer_name = page.locator("#NameSign")
        self.signer_title = page.get_by_role("textbox", name="Title *")
        
        # Submission
        self.complete_payment_btn = page.get_by_role("button", name=" Complete Payment")
        self.ok_button = page.get_by_role("button", name="OK")

    def click_license_application(self) -> None:
        """Clicks the 'License Application' button to begin submission."""
        import pytest
        logger.info("Clicking '#btnLicenseApp' button to start license application")
        self.license_app_button.click()
        
        # Handle the potential STOP dialog for existing license holders
        try:
            stop_dialog_ok = self.page.get_by_role("button", name="OK")
            stop_dialog_ok.wait_for(state="visible", timeout=3000)
            logger.warning("STOP dialog detected (Account already holds a license).")
            stop_dialog_ok.click()
            pytest.skip("Skipping test: This account already holds a license and is physically blocked from submitting a new one.")
        except Exception as e:
            if "Skipping test" in str(e):
                raise e # Re-raise the pytest.skip exception so it halts the test
            # If the dialog doesn't appear, just proceed normally
            pass

    def fill_license_application_form(self) -> None:
        """Fills the license application form with dynamic Faker test data."""
        fake = Faker()
        
        logger.info("Filling Placeholder 1 and 2 fields...")
        self.placeholder_1.click()
        self.placeholder_1.fill(fake.paragraph(nb_sentences=2))
        self.placeholder_2.click()
        self.placeholder_2.fill(fake.paragraph(nb_sentences=2))
        
        logger.info("Checking acknowledgment checkboxes...")
        # Remove force=True to ensure JS validation events trigger properly on the label
        self.ack_checkbox_1.click()
        self.ack_checkbox_2.click()
        
        logger.info("Entering certification signature values...")
        self.signer_name.click()
        self.signer_name.fill(fake.name())
        self.signer_title.click()
        self.signer_title.fill(fake.job())
        # Press Tab to trigger the final blur event and enable the submit button
        self.signer_title.press("Tab")
        
        logger.info("Clicking Complete Payment button...")
        self.complete_payment_btn.click()

        logger.info("Waiting for Record saved successfully popup...")
        self.ok_button.wait_for(state="visible", timeout=30000)
        
        logger.info("Popup appeared -- registering native dialog handler and clicking OK...")
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.ok_button.click()
        logger.info("Clicked OK -- navigating to payment gateway page")
