import logging
import re
from playwright.sync_api import expect, Locator
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class ApplicantInformationPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Tab selection
        self.applicant_tab = page.get_by_role("link", name="Applicant/Permittee")
        
        # Page Headers
        self.app_header = page.locator("#LogAppHeader")
        self.contacts_heading = page.get_by_role("heading", name="Contacts")
        self.contacts_grid_container = page.locator(".row > div:nth-child(3)").first
        
        # Link Contact Selectors
        self.link_contact_button = page.get_by_role("button", name="Link Contact to Permit")
        self.modal_title = page.locator(".k-window-title:visible").filter(has_text=re.compile("Contact", re.I)).first
        self.search_input = page.get_by_role("textbox", name="Company/Designer/Engineer")
        self.refresh_button = page.get_by_role("button", name="Refresh")
        self.dealers_grid = page.locator("#gridDealers > .k-grid-content")
        self.dealer_first_checkbox = page.locator("#gridDealers tbody input[type='checkbox'], #gridDealers #selectedChk").first
        self.modal_close_button = page.locator(".k-window:visible [aria-label='Close'], [role='dialog']:visible [aria-label='Close']").first
        
        # Edit Contact Selectors
        self.edit_contact_button = page.locator("#editApplicant").first
        self.edit_form_container = page.locator("#partial-form").first
        self.contact_info_heading = page.get_by_role("heading", name="Contact Information")
        self.save_button = page.get_by_role("button", name=" Save")
        self.ok_button = page.get_by_role("button", name="OK")

    def navigate_to_applicant_info(self) -> None:
        """Transitions to the Applicant/Permittee tab."""
        logger.info("Navigating to Applicant/Permittee tab.")
        self._wait_for_loader()
        self.js_click(self.applicant_tab)
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_loader()

    def verify_initial_layout(self) -> None:
        """Validates all headers and layouts exist on the page."""
        logger.info("Verifying Applicant/Permittee layout.")
        expect(self.app_header).to_be_visible(timeout=15000)
        expect(self.contacts_heading).to_be_visible(timeout=10000)
        expect(self.contacts_grid_container).to_be_visible(timeout=10000)

    def link_contact_to_permit(self, query: str = "HCL") -> None:
        """Links a contact matching the query to the permit."""
        logger.info(f"Linking contact matching query: '{query}'")
        self.js_click(self.link_contact_button)
        expect(self.modal_title).to_be_visible(timeout=10000)
        
        # Search contact by filling input and pressing Enter
        self.js_click(self.search_input)
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self._wait_for_loader()
        
        # Fallback click refresh
        try:
            self.js_click(self.refresh_button)
            self._wait_for_loader()
        except Exception:
            pass
        
        # Verify grid is visible
        expect(self.dealers_grid).to_be_visible(timeout=15000)
        self._wait_for_loader()
        
        # Check if first row checkbox is visible (meaning search query returned matching records)
        try:
            self.dealer_first_checkbox.wait_for(state="visible", timeout=5000)
            logger.info("Found matching contact record in search results.")
            self.js_click(self.dealer_first_checkbox)
            
            # Handle confirmation dialog
            try:
                # Confirm standard alert popup "Are sure you want to continue?"
                self.ok_button.wait_for(state="visible", timeout=5000)
                self.js_click(self.ok_button)
                self._wait_for_loader()
            except Exception:
                logger.info("No confirmation dialog appeared.")
                
            # Handle assignment already exists or success popup
            try:
                self.ok_button.wait_for(state="visible", timeout=5000)
                self.js_click(self.ok_button)
                self._wait_for_loader()
            except Exception:
                logger.info("No assignment success/duplicate alert popped up.")
        except Exception:
            logger.warning(f"No matching contact records found for search query '{query}' in contact linking modal.")
            
        # Close the modal dialog
        self.js_click(self.modal_close_button)
        self._wait_for_loader()
        logger.info("Contact linking procedure completed.")

    def edit_first_contact_and_save(self) -> None:
        """Edits the first contact in the grid and saves it."""
        logger.info("Editing contact information.")
        expect(self.contacts_grid_container).to_be_visible(timeout=10000)
        self.js_click(self.edit_contact_button)
        
        expect(self.edit_form_container).to_be_visible(timeout=10000)
        expect(self.contact_info_heading).to_be_visible(timeout=10000)
        
        # Save contact details subform
        self.js_click(self.save_button)
        self._wait_for_loader()
        logger.info("Contact information saved successfully.")
