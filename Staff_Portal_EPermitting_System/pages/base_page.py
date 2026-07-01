from playwright.sync_api import Page, Locator, expect
import logging
import datetime
import re

logger = logging.getLogger(__name__)

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    def click_element(self, selector: str):
        self.page.wait_for_selector(selector)
        self.page.click(selector)

    def fill_input(self, selector: str, text: str):
        self.page.wait_for_selector(selector)
        self.page.fill(selector, text)

    def get_element_text(self, selector: str) -> str:
        self.page.wait_for_selector(selector)
        return self.page.inner_text(selector)
        
    def wait_for_element(self, selector: str, timeout: int = 30000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def scroll_to_locator(self, locator: Locator):
        """Scrolls an element into view smoothly."""
        locator.scroll_into_view_if_needed()

    def safe_click(self, locator: Locator):
        """
        Scrolls the element into view and then performs a small scroll adjustment
        to ensure fixed headers do not intercept the click.
        """
        locator.scroll_into_view_if_needed()
        # Scroll up slightly to move the element out from under a fixed header
        self.page.evaluate("window.scrollBy(0, -150)")
        locator.click()

    def dispatch_bubble_click(self, locator: Locator):
        """
        Dispatches a native JS click event that bubbles up the DOM.
        This is extremely effective for problematic 'Save' buttons.
        """
        locator.scroll_into_view_if_needed()
        self.page.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }))", locator.element_handle())

    def js_click(self, locator: Locator):
        """
        Clicks an element using JavaScript to bypass pointer/hit-testing issues
        caused by layout, overlays, or CSS zoom.
        """
        locator.wait_for(state="visible")
        locator.evaluate("el => el.click()")

    def _set_kendo_numeric_value(self, element_id: str, value: float):
        """
        Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API.
        """
        self.page.evaluate(f"""
            () => {{
                var numeric = $("#" + "{element_id}").data("kendoNumericTextBox");
                if (numeric) {{
                    numeric.value({value});
                    numeric.trigger("change");
                }}
            }}
        """)

    def _wait_for_loader(self, timeout=60000):
        """Waits for the global loading spinner and blocking elements to disappear."""
        try:
            self.page.locator("#loader").wait_for(state="hidden", timeout=timeout)
            self.page.locator(".k-loading-mask").wait_for(state="hidden", timeout=15000)
            self.page.locator(".k-overlay").wait_for(state="hidden", timeout=15000)
            self.page.wait_for_timeout(500)
        except Exception:
            pass

    def _select_first_dropdown_option(self) -> None:
        """Clicks the first valid option in the visible Kendo dropdown listbox."""
        self.page.wait_for_selector("[role='listbox']:visible, .k-list-container:visible", timeout=5000)
        options = self.page.locator("[role='listbox']:visible [role='option'], .k-list-container:visible [role='option']")
        self.page.wait_for_timeout(500)
        if options.count() > 1:
            logger.info("Selecting first valid option (index 1) in Kendo dropdown")
            self.js_click(options.nth(1))
        else:
            logger.info("Selecting option (index 0) in Kendo dropdown")
            self.js_click(options.first)
        self.page.wait_for_timeout(1000)
        self._wait_for_loader()

    def fill_kendo_numeric(self, input_id: str, value: str) -> None:
        """Focuses the Kendo numeric text box and types the value dynamically using keyboard emulation."""
        logger.info(f"Filling Kendo numeric input '{input_id}' with value '{value}'")
        visible_input = self.page.locator(f"#{input_id}").locator("xpath=preceding-sibling::input").first
        
        # Click the visible Kendo numeric input element physically to trigger real focus & swap
        visible_input.click()
        self.page.wait_for_timeout(300)
        
        # Emulate select-all, delete, and type
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        self.page.keyboard.type(value)
        self.page.keyboard.press("Tab")  # Focus out to trigger Kendo model validation
        self.page.wait_for_timeout(200)

    def set_all_datefields_to_current(self) -> None:
        """Sets all active Kendo DatePickers to today's date via direct JS injection."""
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        logger.info(f"JS Injecting current date: '{current_date_str}' to all active datepicker inputs.")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"]').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                    }}
                }});
            }}
        """)
        self.page.wait_for_timeout(500)

    def select_today_in_calendar(self, trigger_button: Locator) -> None:
        """Opens calendar datepicker and clicks the today/present link dynamically."""
        logger.info("Clicking date picker calendar button.")
        self.js_click(trigger_button)
        self.page.wait_for_timeout(500)
        today_day = str(datetime.datetime.now().day)
        try:
            today_link = self.page.locator(".k-calendar .k-today a, .k-calendar-view .k-today a, .k-today a, .k-state-today a, .k-calendar .k-state-selected a").first
            self.js_click(today_link)
            logger.info("Clicked today's date using Kendo today classes.")
        except Exception:
            day_link = self.page.locator(".k-calendar:visible, .k-calendar-container:visible").get_by_role("link", name=today_day, exact=True).first
            self.js_click(day_link)
            logger.info(f"Clicked day number link '{today_day}'.")
        self.page.wait_for_timeout(500)

