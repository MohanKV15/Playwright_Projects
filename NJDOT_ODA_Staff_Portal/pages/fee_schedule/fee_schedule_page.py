import re
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class FeeSchedulePage(BasePage):
    """Page Object Model for the Fee Schedule section in the Staff Portal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation menu link
        self.fee_schedule_link = page.get_by_role("link", name="Fee Schedule")

        # Headings & Containers
        self.fee_schedule_heading = page.get_by_role("heading", name="Fee Schedule")
        self.partial_form_first = page.locator("#partial-form").first
        self.results_grid_container = page.locator("#frmCustomer > .form-wrapper > .row > .col-md-12")

        # Search Form Dropdown & Button
        self.search_form = page.locator("#frmFeeSearch")
        self.search_button = page.get_by_role("button", name=" Search")

        # Add Trigger
        self.add_fee_schedule_btn = page.get_by_role("button", name=" Add Fee Schedule")

        # Add Form Layout Assertions
        self.form_wrapper_nth4 = page.locator("div").filter(has_text="Application Fee Permit Fee").nth(4)
        self.form_wrapper_nth1 = page.locator("div").filter(has_text="Fee Schedule Save Cancel").nth(1)

        # Details Form Dropdown & Buttons
        self.details_form = page.locator("#frmFeeScheduleDetails")
        self.save_button = page.get_by_role("button", name=" Save")
        self.cancel_button = page.get_by_role("button", name=" Cancel")

        # Option locator (generic role option matching option name)
        self.option_item = lambda name: page.locator(
            "li[role='option']:visible, .k-list-container:visible li, .k-list-container:visible .k-list-optionlabel, .k-animation-container:visible li, .k-animation-container:visible .k-list-optionlabel, [role='option']:visible, .k-list-optionlabel:visible"
        ).filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)).first

    def navigate_to_fee_schedule(self) -> None:
        """Navigates to the Fee Schedule page."""
        logger.info("Navigating to Fee Schedule page.")
        self.fee_schedule_link.wait_for(state="visible", timeout=15000)
        self.fee_schedule_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def select_search_type(self, type_name: str) -> None:
        """Clicks the search dropdown and selects the option matching type_name."""
        logger.info(f"Selecting search type: {type_name}")
        dropdown_trigger = self.search_form.locator(".k-input, .k-dropdown-wrap, [role='listbox']").first
        dropdown_trigger.click()
        self.page.wait_for_timeout(500)
        self.option_item(type_name).click()
        self.page.wait_for_timeout(500)

    def select_search_type_by_text(self, current_text: str, next_type: str) -> None:
        """Clicks the search dropdown by finding its current text and selects the next type."""
        logger.info(f"Clicking search dropdown with text '{current_text}' and selecting '{next_type}'")
        self.search_form.get_by_text(current_text, exact=True).first.click()
        self.page.wait_for_timeout(500)
        self.option_item(next_type).click()
        self.page.wait_for_timeout(500)

    def click_search(self) -> None:
        """Clicks the Search button and synchronizes with loaders."""
        logger.info("Clicking Search button.")
        self.search_button.first.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def click_add_fee_schedule(self) -> None:
        """Clicks the Add Fee Schedule button."""
        logger.info("Clicking Add Fee Schedule button.")
        self.add_fee_schedule_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def select_details_type_by_text(self, current_text: str, next_type: str) -> None:
        """Clicks the details dropdown by finding its current text and selects the next type."""
        logger.info(f"Clicking details dropdown with text '{current_text}' and selecting '{next_type}'")
        self.details_form.get_by_text(current_text, exact=True).first.click()
        self.page.wait_for_timeout(500)
        self.option_item(next_type).click()
        self.page.wait_for_timeout(500)

    def click_save(self) -> None:
        """Clicks the Save button."""
        logger.info("Clicking Save button.")
        self.save_button.click()
        self.page.wait_for_timeout(1000)

    def click_cancel(self) -> None:
        """Clicks the Cancel button."""
        logger.info("Clicking Cancel button.")
        self.cancel_button.click()
        self.page.wait_for_timeout(1000)
