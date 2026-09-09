import logging
import re
from typing import Dict, Optional, Union
from faker import Faker
from playwright.sync_api import Locator, Page, expect

from IDOT_ODA_Staff_Portal.pages.application_permit.application_details_page import ApplicationDetailsPage
from IDOT_ODA_Staff_Portal.pages.core.base_page import BasePage

logger = logging.getLogger(__name__)
fake = Faker()


class CustomerActionItemsPage(BasePage):
    """
    Page Object Model representing the Customer Action Items workflow
    in the IDOT Outdoor Advertising Staff Portal.

    Workflow:
    - Activate application permit context (delegated to ApplicationDetailsPage)
    - Navigate to Customer Action Items listing page (4319CustCommListingStaffFull)
    - Verify listing headers and elements
    - Add New Customer Action Item (4319CustCommDetailsStaffFull)
    - Dynamically select 1st valid option for Action Item Type, Status, and Review Person
    - Populate Message to Customer with dynamic Faker text
    - Attach document via 'Send Email With Attachments' modal
    - Save action item and verify redirect to listing page
    - Verify newly created record exists in the listing table
    - Re-open saved record and verify details view displays accurately
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logger

        # 1. Navigation & Context
        self.app_details = ApplicationDetailsPage(page)
        self.sidebar_action_items_link = page.locator(
            "a[href*='CustCommListingStaffFull'], .sidebar a:has-text('Customer Action Items'), nav a:has-text('Customer Action Items')"
        ).filter(visible=True).first

        # 2. Listing View Elements (4319CustCommListingStaffFull)
        self.header_app_details_permit = page.get_by_text("Application Details Permit").first
        self.heading_customer_communication = page.get_by_role("heading", name="Customer Communication").first
        self.add_new_button = page.locator(
            "button:has-text('Add New'), a:has-text('Add New'), [role='button']:has-text('Add New')"
        ).first
        self.grid_rows = page.locator("table.k-selectable tbody tr")

        # 3. Details / Form Elements (4319CustCommDetailsStaffFull)
        self.form_details_header = page.get_by_text("Customer Communication Details Action Item Type *").first
        self.action_item_type_id = "#Communication_Type"
        self.review_status_id = "#Review_Status"
        self.review_by_id = "#Review_By"
        self.message_input = page.get_by_role(
            "textbox", name=re.compile(r"Message to Customer", re.I)
        ).or_(
            page.locator("label:has-text('Message to Customer') ~ textarea, #divfrmCommunication textarea")
        ).first

        # 4. Attachment Modal Elements
        self.attach_button = page.locator("#btnAttachFromLog, button:has-text('Attach')").first
        self.modal_email_attachments_title = page.get_by_text("Send Email With Attachments").first
        self.modal_select_attachments_btn = page.locator(
            "#btnSendAttachments, button:has-text('Select Attachments')"
        ).first

        # 5. Form Actions
        self.save_button = page.locator("#btnSubmit, button:has-text('Save')").first

    # -------------------------------------------------------------------------
    # Navigation & Page Verification
    # -------------------------------------------------------------------------
    def navigate_to_customer_action_items(self, company_name: str = "IDOTOAtest2") -> None:
        """
        Activates application session via company search, clicks 1st record row to enter permit details,
        and navigates to Customer Action Items via sidebar menu.
        """
        self.logger.info("Activating application session for company: %s", company_name)
        self.app_details.search_by_company(company_name=company_name)
        self._wait_for_loader()

        expect(self.app_details.permit_grid_rows.first).to_be_visible(timeout=25000)
        first_row = self.app_details.permit_grid_rows.first

        # Activate permit session by clicking action button on 1st record row
        action_btn = first_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=15000)
        action_btn.click(force=True)
        self._wait_for_loader()

        # Expand Application/Permits menu if collapsed
        expect(self.app_details.app_permits_menu).to_be_visible(timeout=15000)
        if not self.sidebar_action_items_link.is_visible():
            self.app_details.app_permits_menu.click(force=True)

        self.logger.info("Clicking sidebar link: Customer Action Items")
        expect(self.sidebar_action_items_link).to_be_visible(timeout=15000)
        self.sidebar_action_items_link.click(force=True)
        self._wait_for_loader()

        self.page.wait_for_url("**/4319CustCommListingStaffFull**", timeout=20000)
        self.verify_listing_page_loaded()

    def verify_listing_page_loaded(self) -> None:
        """
        Verifies that Customer Action Items listing page is loaded properly.
        """
        self.logger.info("Verifying Customer Action Items listing page elements")
        expect(self.header_app_details_permit).to_be_visible(timeout=15000)
        expect(self.heading_customer_communication).to_be_visible(timeout=15000)
        expect(self.add_new_button).to_be_visible(timeout=15000)

    # -------------------------------------------------------------------------
    # Form Interaction (Add New, Select 1st Dropdowns, Faker Message, Attach)
    # -------------------------------------------------------------------------
    def click_add_new(self) -> None:
        """
        Clicks 'Add New' button and asserts that the details form is displayed.
        """
        self.logger.info("Clicking 'Add New' button")
        self.add_new_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_url("**/4319CustCommDetailsStaffFull**", timeout=20000)
        self._wait_for_loader()
        expect(self.form_details_header).to_be_visible(timeout=15000)

    def select_first_valid_dropdown_option(self, dropdown_locator_or_id: Union[Locator, str]) -> str:
        """
        Selects the first valid option dynamically from a Kendo DropDownList.
        """
        return self.kendo_dropdown.select_first_valid_option(dropdown_locator_or_id)

    def fill_customer_action_item_form(
        self,
        message: Optional[str] = None,
        attach_document: bool = True,
    ) -> Dict[str, str]:
        """
        Fills the Customer Action Item form:
        - Selects 1st valid option for Action Item Type
        - Selects 1st valid option for Review Status
        - Selects 1st valid option for Review Person
        - Generates dynamic message using Faker and fills Message to Customer
        - Optionally opens Attach modal, selects an available attachment, and confirms
        Returns dictionary containing all populated form values.
        """
        # 1. Select 1st valid option from all 3 required Kendo dropdowns
        action_type = self.select_first_valid_dropdown_option(self.action_item_type_id)
        self.logger.info("Selected 1st Action Item Type: %s", action_type)

        review_status = self.select_first_valid_dropdown_option(self.review_status_id)
        self.logger.info("Selected 1st Review Status: %s", review_status)

        review_by = self.select_first_valid_dropdown_option(self.review_by_id)
        self.logger.info("Selected 1st Review Person: %s", review_by)

        # 2. Fill Message to Customer using Faker
        generated_message = message or f"Customer Action Item: {fake.sentence(nb_words=6)}"
        self.logger.info("Populating Message to Customer: %s", generated_message)
        self.message_input.wait_for(state="visible", timeout=10000)
        self.message_input.fill(generated_message)

        # 3. Handle Attach modal if requested
        if attach_document and self.attach_button.is_visible():
            self.logger.info("Opening Attach Documents modal")
            self.attach_button.click(force=True)
            self._wait_for_loader()

            modal = self.page.locator(".k-window:visible, .modal:visible").first
            expect(modal).to_be_visible(timeout=10000)

            # Check the first available attachment checkbox in modal
            modal_checkbox = modal.locator("input[type='checkbox']").first
            if modal_checkbox.is_visible(timeout=5000):
                modal_checkbox.check(force=True)
                self.logger.info("Checked attachment checkbox")

            self.modal_select_attachments_btn.click(force=True)
            self.logger.info("Clicked 'Select Attachments'")
            self._wait_for_loader()
            expect(modal).not_to_be_visible(timeout=10000)
            self.page.wait_for_timeout(500)

        return {
            "action_type": action_type,
            "status": review_status,
            "review_by": review_by,
            "message": generated_message,
        }

    def save_action_item(self) -> None:
        """
        Submits the form and waits for redirect back to the listing page.
        """
        self.logger.info("Saving Customer Action Item")
        self.save_button.click(force=True)
        self._wait_for_loader()
        self.page.wait_for_url("**/4319CustCommListingStaffFull**", timeout=25000)
        self._wait_for_loader()
        self.verify_listing_page_loaded()

    def create_customer_action_item(
        self,
        message: Optional[str] = None,
        attach_document: bool = True,
    ) -> Dict[str, str]:
        """
        High-level workflow:
        1. Clicks 'Add New'
        2. Populates form fields (1st dropdowns, Faker message, attachment)
        3. Saves form and waits for listing page reload
        Returns the data dictionary of submitted values.
        """
        self.click_add_new()
        data = self.fill_customer_action_item_form(message=message, attach_document=attach_document)
        self.save_action_item()
        return data

    # -------------------------------------------------------------------------
    # Verification & Re-opening of Record
    # -------------------------------------------------------------------------
    def verify_action_item_in_table(self, expected_text: Optional[str] = None) -> Locator:
        """
        Verifies that customer action items exist in the listing table and returns the row.
        """
        self.logger.info("Verifying Customer Action Items listing table has records")
        rows = self.grid_rows.filter(
            has=self.page.locator("button, a.k-button, [role='button']")
        )
        if expected_text:
            rows = rows.filter(has_text=expected_text)
        expect(rows.first).to_be_visible(timeout=20000)
        matching_row = rows.first
        self.logger.info("Found table record: %s", matching_row.inner_text().strip())
        return matching_row

    def open_action_item_and_verify_details(self, row: Optional[Locator] = None) -> None:
        """
        Clicks the view/action button on the table row and asserts that
        the Customer Communication Details form re-opens and displays properly.
        """
        target_row = row or self.grid_rows.first
        self.logger.info("Clicking action button on table row to open details")
        action_btn = target_row.locator("button, a.k-button, [role='button']").first
        expect(action_btn).to_be_visible(timeout=10000)
        action_btn.click(force=True)
        self._wait_for_loader()

        self.page.wait_for_url("**/4319CustCommDetailsStaffFull**", timeout=20000)
        self._wait_for_loader()
        expect(self.form_details_header).to_be_visible(timeout=15000)
        self.logger.info("Customer Communication Details form successfully displayed")
