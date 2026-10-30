import logging
import re
from faker import Faker
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class CustomerActionItemsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.fake = Faker()
        
        # Navigation Link
        self.customer_action_items_link = page.get_by_role("link", name="Customer Action Items")
        
        # Tab validation
        self.application_details_heading = page.get_by_role("heading", name="Application Details")
        self.partial_form = page.locator("#partial-form").first
        self.partial_form_section_div = page.locator("#partial-form > section > div > div")
        
        # Action Buttons
        self.add_new_button = page.get_by_role("button", name="Add New").or_(page.locator("#BtnAddNew"))
        
        # Form Validations
        self.details_container_div = page.locator("div").filter(has_text="Application Details Permit")
        self.communication_details_heading = page.get_by_role("heading", name="Customer Communication Details")
        
        # Form Fields
        self.communication_container = page.locator("#divfrmCommunication")
        self.option_dropdown = page.locator("#divfrmCommunication").get_by_text("Select option")
        self.status_dropdown = page.locator("#divfrmCommunication").get_by_text("Requested", exact=True)
        self.review_person_dropdown = page.locator("#divfrmCommunication").get_by_text("Select Review Person")
        
        self.message_input = page.get_by_role("textbox", name="Message to Customer *")
        
        # Attach Modal
        self.attach_button = page.get_by_role("button", name="Attach")
        self.send_email_attachment_modal_title = page.locator("div").filter(has_text=re.compile(r"^Send Email With Attachments$")).first
        self.attachment_grid_header = page.locator("div").filter(has_text="Date & TimeNameSelectparent_")
        
        # Action buttons
        self.select_attachments_btn = page.get_by_role("button", name="Select Attachments")
        self.save_button = page.get_by_role("button", name=" Save").or_(page.locator("#btnSubmit"))
        
        # Grid content
        self.k_grid_content = page.locator("#CommGrid, .k-grid:visible").first
        
        # Next flow tab
        self.permit_completion_link = page.get_by_role("link", name="Permit Completion")

    def _expand_navigation_menu(self) -> None:
        """Expands the Kendo PanelBar navigation menu so all submenus/links are visible."""
        logger.info("Expanding Kendo PanelBar navigation menu.")
        self._expand_kendo_panel("application")

    def navigate_to_customer_action_items(self) -> None:
        """Navigates to the Customer Action Items tab."""
        logger.info("Navigating to the Customer Action Items tab")
        self._expand_navigation_menu()
        self.customer_action_items_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        expect(self.application_details_heading).to_be_visible(timeout=15000)

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.select_first_kendo_dropdown()

    def add_customer_action_item(self) -> None:
        """Fills out and saves a new customer communication record using Faker."""
        logger.info("Adding new customer action item")
        
        expect(self.partial_form).to_be_visible(timeout=10000)
        expect(self.partial_form_section_div.first).to_be_visible(timeout=10000)
        
        self.add_new_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        
        # Verify modal elements loaded
        expect(self.details_container_div.nth(4)).to_be_visible(timeout=10000)
        expect(self.communication_details_heading).to_be_visible(timeout=10000)
        
        # 1. Option Dropdown: Select 'Additional Info Requested' (non-fee) or first option
        logger.info("Selecting Option dropdown")
        self.option_dropdown.click()
        if not self.kendo_dropdown.select_by_locator(self.page.locator("[role='listbox']:visible"), "Additional Info Requested", timeout_ms=3000):
            self._select_first_dropdown_option()

        # If a fee option was chosen, ensure Pay_Amount has a valid amount so validation passes
        try:
            pay_amt = self.page.locator("#Pay_Amount")
            if pay_amt.is_visible(timeout=1000):
                self.set_kendo_numeric("#Pay_Amount", 50.00)
        except Exception:
            pass
        
        # 2. Status Dropdown
        logger.info("Selecting Status dropdown")
        if self.status_dropdown.is_visible():
            self.status_dropdown.click()
            self._select_first_dropdown_option()
        
        # 3. Review Person Dropdown
        logger.info("Selecting Review Person dropdown")
        if self.review_person_dropdown.is_visible():
            self.review_person_dropdown.click()
            self._select_first_dropdown_option()
        
        # 4. Fill Message
        logger.info("Filling message to customer using Faker")
        self.message_input.click()
        self.message_input.fill(self.fake.sentence())
        
        # 5. Attach file
        logger.info("Opening Attachments modal")
        self.attach_button.click()
        
        # Verify Attachments modal
        expect(self.send_email_attachment_modal_title).to_be_visible(timeout=10000)
        expect(self.attachment_grid_header.nth(4)).to_be_visible(timeout=10000)
        
        # Select first checkbox dynamically if present, otherwise close modal
        logger.info("Selecting first available attachment checkbox")
        try:
            self.page.locator("input[type='checkbox']").first.wait_for(state="visible", timeout=4000)
            self.page.locator("input[type='checkbox']").first.check()
            logger.info("Attachment selected, clicking Select Attachments button")
            self.select_attachments_btn.click()
        except Exception as e:
            logger.warning(f"No attachments available to select or checkbox not visible: {e}. Closing the modal.")
            self.page.locator("span.k-icon.k-i-close:visible").first.click()
            
        self.page.wait_for_timeout(1000)
        
        # 6. Save
        logger.info("Saving customer action item")
        try:
            self.page.once("dialog", lambda dialog: dialog.accept())
        except Exception:
            pass
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        self.dismiss_kendo_dialogs()
        
        # Wait for grid to reload
        expect(self.k_grid_content).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(1000)

    def navigate_to_permit_completion(self) -> None:
        """Navigates to the next tab: Permit Completion."""
        logger.info("Navigating to the Permit Completion tab")
        self.permit_completion_link.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
