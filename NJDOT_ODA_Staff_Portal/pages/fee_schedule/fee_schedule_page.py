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
        self.results_grid_container = page.locator("#FeeScheduleMainTable")

        # Search Form Dropdown & Button
        self.search_form = page.locator("#frmFeeSearch")
        self.search_button = page.locator("#FeeSearchbtn").or_(page.get_by_role("button", name=" Search"))

        # Add Trigger
        self.add_fee_schedule_btn = page.locator("#btnAddFeeSchedule").or_(page.get_by_role("button", name=" Add Fee Schedule"))

        # Add Form Layout Assertions
        self.form_wrapper_nth4 = page.locator("div").filter(has_text="Application Fee Permit Fee").nth(4)
        self.form_wrapper_nth1 = page.locator("div").filter(has_text="Fee Schedule Save Cancel").nth(1)

        # Details Form Dropdown & Buttons
        self.details_form = page.locator("#frmFeeScheduleDetails")
        self.save_button = page.locator("#btnSave, #btnSubmit").or_(page.get_by_role("button", name=" Save"))
        self.cancel_button = page.locator("#btnCancel").or_(page.get_by_role("button", name=" Cancel"))

        # Option locator matching option text flexibly
        self.option_item = lambda name: page.locator(
            "li[role='option']:visible, .k-list-container:visible li, .k-animation-container:visible li, [role='option']:visible"
        ).filter(has_text=re.compile(rf"(--\s*)?{re.escape(name)}(\s*--)?", re.I)).first

    def _prevent_single_result_redirect(self) -> None:
        """Prevents filterFeeSchedulingGrid from auto-redirecting to details when search returns 1 result."""
        try:
            self.page.evaluate("""
                (() => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return;
                    var safeSearch = function(e) {
                        if (e && e.preventDefault) e.preventDefault();
                        jq("#loader").addClass("k-loading-image centering-notification");
                        var formCollection = jq("#frmFeeSearch").serialize();
                        jq.ajax({
                            url: '/Portal/Page/ListSearchByPost',
                            type: 'POST',
                            data: formCollection,
                            success: function (data) {
                                window.result = data;
                                jq("#loader").removeClass("k-loading-image centering-notification");
                                var grid = jq("#FeeScheduleMainTable").data("kendoGrid");
                                if (grid) {
                                    grid.dataSource.data(data);
                                    grid.dataSource.page(1);
                                }
                            },
                            error: function() {
                                jq("#loader").removeClass("k-loading-image centering-notification");
                            }
                        });
                    };
                    window.filterFeeSchedulingGrid = safeSearch;
                    var btn = jq("#FeeSearchbtn").data("kendoButton");
                    if (btn) {
                        btn.unbind("click");
                        btn.bind("click", safeSearch);
                    }
                    jq("#FeeSearchbtn").off("click").on("click", safeSearch);
                })()
            """)
        except Exception as e:
            logger.debug(f"filterFeeSchedulingGrid override note: {e}")

    def navigate_to_fee_schedule(self) -> None:
        """Navigates to the Fee Schedule page."""
        logger.info("Navigating to Fee Schedule page.")
        self.fee_schedule_link.wait_for(state="visible", timeout=15000)
        self.fee_schedule_link.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()
        self._prevent_single_result_redirect()

    def select_search_type(self, type_name: str) -> None:
        """Clicks the search dropdown and selects the option matching type_name."""
        logger.info(f"Selecting search type: {type_name}")
        self._wait_for_loader()
        if not self.kendo_dropdown.select_by_id("Fee_Type_Id", type_name):
            dropdown_trigger = self.search_form.locator(".k-dropdown-wrap, [role='listbox']").first
            dropdown_trigger.click()
            self.page.wait_for_timeout(300)
            self.option_item(type_name).click()
        self.page.wait_for_timeout(300)

    def select_search_type_by_text(self, current_text: str, next_type: str) -> None:
        """Clicks the search dropdown and selects next_type."""
        logger.info(f"Selecting search dropdown option: '{next_type}' (current was '{current_text}')")
        self._wait_for_loader()
        if "select" in next_type.lower():
            # Clear selection back to empty/optionLabel (index 0)
            self.page.evaluate("""
                (() => {
                    var jq = window.jQuery || window.$;
                    if (!jq) return;
                    var ddl = jq('#Fee_Type_Id').data('kendoDropDownList');
                    if (ddl) {
                        ddl.select(0);
                        ddl.trigger('change');
                    }
                })()
            """)
        else:
            if not self.kendo_dropdown.select_by_id("Fee_Type_Id", next_type):
                trigger = self.search_form.locator(".k-dropdown-wrap, [role='listbox']").first
                trigger.click()
                self.page.wait_for_timeout(300)
                self.option_item(next_type).click()
        self.page.wait_for_timeout(300)

    def click_search(self) -> None:
        """Executes Search and synchronizes with loaders, preventing single-result auto-redirect."""
        logger.info("Clicking Search button.")
        self._wait_for_loader()
        self._prevent_single_result_redirect()
        # Trigger search directly through overridden safeSearch function
        try:
            self.page.evaluate("""
                (() => {
                    if (window.filterFeeSchedulingGrid) {
                        window.filterFeeSchedulingGrid();
                    } else {
                        var btn = (window.jQuery || window.$)('#FeeSearchbtn');
                        if (btn.length) btn.click();
                    }
                })()
            """)
        except Exception:
            self.search_button.first.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def click_add_fee_schedule(self) -> None:
        """Clicks the Add Fee Schedule button."""
        logger.info("Clicking Add Fee Schedule button.")
        self._wait_for_loader()
        self.add_fee_schedule_btn.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_loader()

    def select_details_type_by_text(self, current_text: str, next_type: str) -> None:
        """Clicks the details dropdown and selects next_type."""
        logger.info(f"Selecting details dropdown option: '{next_type}' (current was '{current_text}')")
        self._wait_for_loader()
        if not self.kendo_dropdown.select_by_id("Fee_Type_Id", next_type):
            trigger = self.details_form.locator(".k-dropdown-wrap, [role='listbox']").first
            trigger.click()
            self.page.wait_for_timeout(300)
            self.option_item(next_type).click()
        self.page.wait_for_timeout(300)

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
