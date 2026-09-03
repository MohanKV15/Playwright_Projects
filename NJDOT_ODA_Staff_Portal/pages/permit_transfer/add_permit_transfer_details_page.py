import logging
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AddPermitTransferDetailsPage(BasePage):
    """Page Object Model for the Add Permit Transfer Details section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation elements
        self.permit_transfer_menu_link = page.get_by_role("link", name="Permit Transfer ")
        self.permit_transfer_sub_link = page.locator("#navigationMenu2").get_by_role("link", name="Permit Transfer", exact=True)

        # Parent Page Layout validation
        self.permit_transfer_heading = page.get_by_role("heading", name="Permit Transfer", exact=True)
        self.partial_form_first = page.locator("#partial-form").first
        self.add_permit_transfer_btn = page.get_by_role("button", name=" Add Permit Transfer")

        # Details Page Elements
        self.permit_transfer_details_heading = page.get_by_role("heading", name="Permit Transfer Details")
        self.partial_form_details = page.locator("#partial-form")
        self.permit_no_input = page.locator("#Appl_Transfer_Permit_No")
        self.search_transfer_details_btn = page.locator("#btnSearchTransferDetails")
        self.dealer_name_input = page.locator("#Dealer_Name")
        self.search_dealer_btn = page.get_by_role("button", name=" Search")

        # Dealer Search Dialog validation
        self.dealer_dialog_title = page.locator("#dealerLinkWindow_wnd_title")
        self.dealer_dialog_desc_text = page.get_by_text("Dealer Search (Choose the")
        self.dealer_dialog_partial_form = page.locator("#partial-form").nth(2)
        self.dealer_dialog_grid_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")
        self.dealer_checkbox = page.locator("#selectedChk")
        self.ok_button = page.get_by_role("button", name="OK")

        # Radios & Details Inputs
        self.radio_label_1 = page.locator("div:nth-child(3) > .k-radio-label").first
        self.radio_label_2 = page.locator("div:nth-child(21) > div:nth-child(3) > .k-radio-label")
        self.permit_from_input = page.locator("#Appl_Transfer_Permit_From")
        self.save_button = page.get_by_text("Save")

        # Parent Grid and Find elements
        self.page_load_container = page.locator("#permitTransferOnPageLoad")
        self.find_button = page.get_by_role("button", name=" Find")
        self.dialog_dealer_search_text = page.locator("div").filter(has_text="Dealer Search (Choose the").nth(4)
        self.dialog_dealer_search_input = page.locator("#Dealer_Name")
        self.dialog_search_btn = page.get_by_label("Dealer Search").get_by_role("button", name=" Search")
        self.dialog_results_container = page.locator("div:nth-child(2) > #partial-form > #frmCustomer > .form-wrapper > .row > .col-md-12")

        # Search grid
        self.grid_search_text = page.get_by_text("Search", exact=True)
        self.grid_results_container = page.locator("#frmCustomer > .form-wrapper > div > div:nth-child(2)").first

    def _expand_navigation_menu(self) -> None:
        """Expands Kendo PanelBar for Permit Transfer."""
        logger.info("Expanding Permit Transfer PanelBar navigation.")
        self._expand_kendo_panel("permit transfer")

    def navigate_to_permit_transfer(self) -> None:
        """Navigates to the Permit Transfer list and validates elements."""
        self._expand_navigation_menu()
        if not self.permit_transfer_sub_link.is_visible():
            self.permit_transfer_menu_link.click()
            self.page.wait_for_timeout(1000)
        self.permit_transfer_sub_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.permit_transfer_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_first).to_be_visible(timeout=10000)

    def click_add_permit_transfer(self) -> None:
        """Clicks the Add Permit Transfer button and validates headings."""
        logger.info("Clicking Add Permit Transfer button.")
        self.add_permit_transfer_btn.wait_for(state="visible", timeout=10000)
        self.add_permit_transfer_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.permit_transfer_details_heading).to_be_visible(timeout=15000)
        expect(self.partial_form_details.first).to_be_visible(timeout=10000)

    def search_transfer_details(self, permit_no: str) -> None:
        """Enters permit number and searches transfer details."""
        logger.info(f"Searching transfer details for Permit No: {permit_no}")
        self.permit_no_input.wait_for(state="visible", timeout=10000)
        self.permit_no_input.click()
        self.permit_no_input.fill(permit_no)
        self.search_transfer_details_btn.click()
        self._wait_for_loader()

    def search_and_select_dealer(self, dealer_name: str) -> None:
        """Searches for dealer name, validates dialog elements, selects check and accepts popup."""
        logger.info(f"Searching and selecting dealer: {dealer_name}")
        self.dealer_name_input.wait_for(state="visible", timeout=10000)
        self.dealer_name_input.click()
        self.dealer_name_input.fill(dealer_name)
        self.search_dealer_btn.click()
        self._wait_for_loader()

        # Validate dialog boxes and grid wrappers
        expect(self.dealer_dialog_title).to_be_visible(timeout=15000)
        expect(self.dealer_dialog_desc_text).to_be_visible(timeout=10000)
        expect(self.dealer_dialog_partial_form).to_be_visible(timeout=10000)
        expect(self.dealer_dialog_grid_container).to_be_visible(timeout=10000)

        # Check selection and dismiss popup
        self.dealer_checkbox.check()
        self.handle_popup_continue()

    def fill_details_form(self, from_text: str) -> None:
        """Selects radio elements and fills transfer description field."""
        logger.info("Filling details form elements.")
        self.radio_label_1.click()
        self.page.wait_for_timeout(300)
        self.radio_label_2.click()
        self.page.wait_for_timeout(300)

        self.permit_from_input.click()
        self.permit_from_input.fill(from_text)

    def save_and_confirm(self) -> None:
        """Saves the permit transfer details and dismisses operation completed alert."""
        logger.info("Clicking Save text/button.")
        self.save_button.click()
        self._wait_for_loader()

        # Explicit assertions as requested by the user
        logger.info("Asserting domain and success text are visible/attached in the completion popup.")
        expect(self.page.get_by_text("u-njoda.bemcorp.net").first).to_be_attached(timeout=15000)
        expect(self.page.locator(".k-window:visible, .k-dialog:visible").get_by_text("Operation Completed").first).to_be_visible(timeout=15000)

        # Click OK
        logger.info("Dismissing success popup.")
        self.ok_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        # Verify returned parent page layout
        expect(self.partial_form_first).to_be_visible(timeout=15000)
        expect(self.permit_transfer_heading).to_be_visible(timeout=10000)
        expect(self.page_load_container).to_be_visible(timeout=10000)

    def find_and_select_transfer_dealer(self, dealer_name: str) -> None:
        """Clicks Find, searches and selects dealer in the popup search grid."""
        logger.info("Clicking Find button.")
        self.find_button.click()
        self.page.wait_for_timeout(1000)

        # Verify modal window headers
        expect(self.dealer_dialog_title).to_be_visible(timeout=15000)
        expect(self.dialog_dealer_search_text).to_be_visible(timeout=10000)

        self.dialog_dealer_search_input.click()
        self.dialog_dealer_search_input.fill(dealer_name)
        self.dialog_search_btn.click()
        self._wait_for_loader()

        # Check selection and accept popup
        expect(self.dialog_results_container).to_be_visible(timeout=15000)
        self.dealer_checkbox.check()
        self.handle_popup_continue()

        # Confirm returned parent view is stable
        expect(self.page_load_container).to_be_visible(timeout=15000)

    def execute_grid_search(self) -> None:
        """Triggers grid search and verifies results are displayed."""
        logger.info("Clicking Search text/button.")
        self.grid_search_text.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

        expect(self.grid_results_container).to_be_visible(timeout=15000)
        logger.info("Search successfully executed and results verified.")

    def handle_popup_continue(self) -> None:
        """Dismisses the 'Are sure you want to continue?' dialog box."""
        logger.info("Dismissing 'Are sure you want to continue?' confirmation dialog.")
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(
            has_text=re.compile(r"Are sure you want to continue\?", re.I)
        ).first
        
        try:
            expect(active_dialog).to_be_visible(timeout=15000)
            active_dialog.get_by_role("button", name="OK").click()
        except Exception:
            logger.warning("Confirmation dialog not found. Clicking fallback OK button directly.")
            self.ok_button.click()
        self.page.wait_for_timeout(1000)

    def handle_popup_completed(self) -> None:
        """Dismisses the 'Operation Completed' dialog box."""
        logger.info("Dismissing 'Operation Completed' dialog.")
        active_dialog = self.page.locator(".k-widget.k-window:visible, .k-dialog:visible, .k-window:visible").filter(
            has_text=re.compile(r"Operation Completed|Operation completed", re.I)
        ).first
        
        try:
            expect(active_dialog).to_be_visible(timeout=15000)
            active_dialog.get_by_role("button", name="OK").click()
        except Exception:
            logger.warning("Operation completed dialog not found. Clicking fallback OK button directly.")
            self.ok_button.click()
        self.page.wait_for_timeout(1000)
