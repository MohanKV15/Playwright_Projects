import logging
from playwright.sync_api import Page, expect
from faker import Faker
from pages.core.base_page import BasePage

logger = logging.getLogger(__name__)

class NameChangePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Navigation
        self.name_change_button = page.locator("#btnNameChange")
        
        # Form Fields
        self.new_name = page.locator("#NewName")
        
        # Checkboxes
        self.ack_checkbox_1 = page.locator(".k-checkbox-label").first
        self.ack_checkbox_2 = page.locator("div:nth-child(3) > .form-check > .k-checkbox-label")
        self.ack_checkbox_3 = page.locator("div:nth-child(5) > .col-md-12.huddleUp > .form-check > .k-checkbox-label")
        
        # Signature
        self.signer_name = page.locator("#SignName")
        self.signer_title = page.locator("#SignTitle")
        
        # Submission
        self.submit_btn = page.get_by_role("button", name=" Submit")
        self.ok_button = page.get_by_role("button", name="OK")
        
        # Success Screen
        self.success_heading = page.get_by_role("heading", name="Successful")
        self.success_message = page.get_by_text("Application has been submitted. Status notifications will be provided through")
        self.return_home_btn = page.get_by_role("button", name=" Return Home")

    def click_name_change(self) -> None:
        """Clicks the 'Name Change' button to begin submission."""
        import pytest
        logger.info("Clicking '#btnNameChange' button to start Name Change application")
        self.name_change_button.click()
        
        # Handle the potential STOP dialog for blocked accounts
        try:
            stop_dialog_ok = self.page.get_by_role("button", name="OK")
            stop_dialog_ok.wait_for(state="visible", timeout=3000)
            logger.warning("STOP dialog detected. Clicking OK...")
            stop_dialog_ok.click()
            pytest.skip("Skipping test: The account is blocked from submitting this application.")
        except Exception as e:
            if "Skipping test" in str(e):
                raise e
            pass

    def fill_name_change_form(self) -> None:
        """Fills the Name Change form with dynamic Faker test data."""
        fake = Faker()
        
        logger.info("Filling New Name field...")
        self.new_name.click()
        self.new_name.fill(fake.company())
        
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
        
        logger.info("Clicking Submit button...")
        # Use force=True in case Kendo aria-disabled bug persists on this page
        self.submit_btn.click(force=True)

        logger.info("Waiting for Record saved successfully popup...")
        self.ok_button.wait_for(state="visible", timeout=30000)
        
        logger.info("Popup appeared -- clicking OK...")
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.ok_button.click()

    def verify_success_and_return(self) -> None:
        """Verifies the success screen text and clicks Return Home."""
        logger.info("Verifying Success Screen...")
        expect(self.success_heading).to_be_visible(timeout=30000)
        expect(self.success_message).to_be_visible()
        
        logger.info("Clicking Return Home button...")
        self.return_home_btn.click()
