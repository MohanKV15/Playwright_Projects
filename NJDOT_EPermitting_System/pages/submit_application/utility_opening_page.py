import re
import logging
from datetime import datetime, timedelta
from NJDOT_EPermitting_System.pages.submit_application.permit_major_page import PermitMajorPage


class UtilityOpeningPage(PermitMajorPage):
    APPLY_BUTTON = "#btnSubmit9"

    def __init__(self, page, script_name: str = "test_utility_opening"):
        super().__init__(page, script_name=script_name)
        self.logger = logging.getLogger(__name__)

    # ---------- NAVIGATION ----------
    def select_utility_opening(self):
        self.page.locator(self.APPLY_BUTTON).wait_for(state="visible", timeout=15000)

    def click_apply_button(self):
        self.page.locator(self.APPLY_BUTTON).click()
        self.page.get_by_role("button", name="Yes").click()

    def assert_utility_opening_page_loaded(self):
        self.page.wait_for_url(re.compile(r"HighwayOccupancy", re.I), timeout=30000)

    # ---------- ADDITIONAL DETAILS ----------
    def fill_additional_details(self):
        # Select tomorrow's date for both fields to avoid past date validations
        tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        self._set_kendo_date_value("workStartDate", tomorrow_str)
        self._set_kendo_date_value("EOPWorktobecompletedBy", tomorrow_str)

        self.page.locator("#ROPLocation").fill("testing purpose")

    def _set_kendo_date_value(self, input_id: str, value: str):
        """Set a Kendo DatePicker value directly using JavaScript to avoid flaky calendar UI clicks."""
        self.logger.info(f"Setting Kendo DatePicker {input_id} to {value}")
        input_locator = self.page.locator(f"#{input_id}")
        input_locator.wait_for(state="attached", timeout=15000)
        self.page.evaluate(
            """
            ({ id, value }) => {
                const el = document.getElementById(id);
                if (!el) return;
                if (window.jQuery) {
                    const dp = window.jQuery(el).data('kendoDatePicker');
                    if (dp) {
                        dp.value(value);
                        dp.trigger('change');
                        return;
                    }
                }
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """,
            {"id": input_id, "value": value},
        )

    # ---------- DIMENSIONS ----------
    def add_dimensions(self):
        self.page.get_by_role("button", name="Add New").click()

        popup = self.page.locator("#SizeOfOpeningAddNewPopup:visible").first
        popup.wait_for(state="visible", timeout=10000)

        # Wait for inputs
        self.page.locator("#Numeric_Placeholder1").wait_for(state="attached", timeout=10000)
        self.page.locator("#Numeric_Placeholder2").wait_for(state="attached", timeout=10000)
        self.page.locator("#Numeric_Placeholder4").wait_for(state="attached", timeout=10000)

        # Safe Kendo value set
        self.page.evaluate("""
            () => {
                const setValue = (id, val) => {
                    const el = document.getElementById(id);
                    if (!el || !window.jQuery) return;

                    const widget = window.jQuery(el).data('kendoNumericTextBox');
                    if (!widget) return;

                    widget.value(val);
                    widget.trigger('change');
                };

                setValue('Numeric_Placeholder1', 5);
                setValue('Numeric_Placeholder2', 6);
                setValue('Numeric_Placeholder4', 1);

                if (typeof calculateProductUOP === 'function') {
                    calculateProductUOP();
                }
            }
        """)

        # Wait for calculated value
        self.page.wait_for_function(
            """() => {
                const val = document.getElementById('Numeric_Placeholder3')?.value;
                return val && parseFloat(val) > 0;
            }""",
            timeout=5000
        )

        popup.locator("#UOPSaveBtn").click()
        popup.wait_for(state="hidden", timeout=10000)

    # ---------- ATTACHMENTS ----------
    def upload_utility_opening_attachments(self):
        self._upload_if_present("OverallSitePlans", self.SUPPORTING_DOCUMENT_PATH)