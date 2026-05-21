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
        # Select today or tomorrow date for both fields
        self._select_kendo_date(selector="span[aria-controls='workStartDate_dateview']")
        self._select_kendo_date(selector="span[aria-controls='EOPWorktobecompletedBy_dateview']")

        self.page.locator("#ROPLocation").fill("testing purpose")

    # ---------- REUSABLE KENDO DATE PICKER (FIXED) ----------
    def _select_kendo_date(self, selector: str = None, index: int = None):
        """
        Robust Kendo date picker handler.
        Selects today's date if valid (not disabled); otherwise selects tomorrow's date.
        """
        # Open calendar
        if selector:
            self.page.locator(selector).click()
        elif index is not None:
            self.page.get_by_role("button", name="select").nth(index).click()
        else:
            raise ValueError("Either selector or index must be provided")

        # Wait for visible calendar
        calendar = self.page.locator(".k-calendar:visible").first
        calendar.wait_for(state="visible", timeout=10000)

        # Wait for calendar content/cells to be rendered
        calendar.locator("td:not(.k-other-month) a.k-link").first.wait_for(state="visible", timeout=5000)

        # Calculate today and tomorrow
        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        today_day = str(today.day)
        tomorrow_day = str(tomorrow.day)

        # Try to select today's date (must not be other month and must not be disabled)
        today_cell = calendar.locator("td:not(.k-other-month):not(.k-state-disabled)").get_by_role("link", name=today_day, exact=True)

        if today_cell.count() > 0:
            try:
                today_cell.first.click(timeout=5000)
                return
            except Exception:
                # Try force click if standard click fails
                try:
                    today_cell.first.click(force=True, timeout=5000)
                    return
                except Exception:
                    pass

        # If today is disabled or not found, select tomorrow
        if tomorrow.month != today.month:
            # Click next month button in calendar
            next_btn = calendar.locator(".k-nav-next")
            next_btn.wait_for(state="visible", timeout=5000)
            next_btn.click()
            # Wait for calendar content to refresh
            self.page.wait_for_timeout(500)

        tomorrow_cell = calendar.locator("td:not(.k-other-month):not(.k-state-disabled)").get_by_role("link", name=tomorrow_day, exact=True)
        tomorrow_cell.first.wait_for(state="visible", timeout=10000)
        try:
            tomorrow_cell.first.click(timeout=5000)
        except Exception:
            tomorrow_cell.first.click(force=True)

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