import logging
from playwright.sync_api import Page, Locator

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

    def _wait_for_loader(self, timeout: int = 60000) -> None:
        """Universal synchronization helper for loaders and dynamic elements."""
        try:
            self.page.locator("#loader.centering-notification, #loader.k-loading-image").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        try:
            self.page.locator(".k-loading-mask").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        try:
            visible_dialogs = self.page.locator(".k-window:visible, .k-dialog:visible")
            if visible_dialogs.count() == 0:
                self.page.locator(".k-overlay").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(500)


    def _expand_kendo_panel(self, menu_text: str) -> None:
        """Expands a Kendo PanelBar menu item containing the query text."""
        self.page.evaluate(f"""
            () => {{
                var panelBar = $("#navigationMenu2").data("kendoPanelBar");
                if (panelBar) {{
                    var items = $("#navigationMenu2 > li");
                    items.each(function() {{
                        if ($(this).text().toLowerCase().includes("{menu_text.lower()}")) {{
                            panelBar.expand($(this));
                        }}
                    }});
                }}
            }}
        """)
        self.page.wait_for_timeout(1000)


