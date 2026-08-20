import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class BasePage:
    """
    Core BasePage that all Page Object Models inherit from.
    Contains global framework logic and loader-wait implementations.
    """
    
    def __init__(self, page: Page):
        self.page = page
        
        # Centralized Global Loaders
        self.global_loader = page.locator("#loader")
        self.kendo_loader = page.locator(".k-loading-mask")

    def _wait_for_loader(self) -> None:
        """
        Universally handles Kendo UI AJAX loading masks and global system loaders.
        Waits for both to safely disappear before allowing the automation to proceed.
        """
        # 1. Wait for global system loader to disappear
        try:
            self.global_loader.wait_for(state="hidden", timeout=15000)
        except Exception:
            pass

        # 2. Wait for local Kendo UI data-grid mask to disappear
        try:
            self.kendo_loader.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
            
        # 3. Wait for background network traffic to settle if possible
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    def _wait_for_page_ready(self) -> None:
        """
        General utility to pause execution until all AJAX and UI rendering completes.
        """
        self._wait_for_loader()

    # ---------- GENERAL UI WRAPPERS ----------
    def navigate(self, url: str) -> None:
        logger.info(f"Navigating to URL: {url}")
        self.page.goto(url)

    def click_element(self, selector: str) -> None:
        logger.info(f"Clicking element with selector: {selector}")
        self.page.wait_for_selector(selector)
        self.page.click(selector)

    def fill_input(self, selector: str, text: str) -> None:
        logger.info(f"Filling selector {selector} with text value")
        self.page.wait_for_selector(selector)
        self.page.fill(selector, text)

    def get_element_text(self, selector: str) -> str:
        self.page.wait_for_selector(selector)
        text = self.page.inner_text(selector)
        logger.info(f"Retrieved element text for selector {selector}: {text}")
        return text
        
    def wait_for_element(self, selector: str, timeout: int = 30000) -> None:
        logger.info(f"Waiting for selector {selector} (timeout: {timeout}ms)")
        self.page.wait_for_selector(selector, timeout=timeout)

    from playwright.sync_api import Locator
    
    def scroll_to_locator(self, locator: 'Locator') -> None:
        """Scrolls an element into view smoothly."""
        logger.info("Scrolling locator into view")
        locator.scroll_into_view_if_needed()

    def safe_click(self, locator: 'Locator') -> None:
        """
        Scrolls the element into view and then performs a small scroll adjustment
        to ensure fixed headers do not intercept the click.
        """
        logger.info("Performing safe click (scroll & header offset adjustment)")
        locator.scroll_into_view_if_needed()
        # Scroll up slightly to move the element out from under a fixed header
        self.page.evaluate("window.scrollBy(0, -150)")
        locator.click()

    def dispatch_bubble_click(self, locator: 'Locator') -> None:
        """
        Dispatches a native JS click event that bubbles up the DOM.
        This is extremely effective for problematic buttons.
        """
        logger.info("Dispatching bubbling click event using JS evaluation")
        locator.scroll_into_view_if_needed()
        self.page.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }))", locator.element_handle())

    def js_click(self, locator: 'Locator') -> None:
        """
        Clicks an element using JavaScript to bypass pointer/hit-testing issues
        caused by layout, overlays, or CSS zoom.
        """
        logger.info("Performing direct JavaScript element click")
        locator.wait_for(state="visible")
        locator.evaluate("el => el.click()")

    def _set_kendo_numeric_value(self, element_id: str, value: float) -> None:
        """
        Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API.
        """
        logger.info(f"Setting Kendo numeric text box '{element_id}' to value '{value}'")
        self.page.evaluate(f"""
            () => {{
                var numeric = $("#" + "{element_id}").data("kendoNumericTextBox");
                if (numeric) {{
                    numeric.value({value});
                    numeric.trigger("change");
                }}
            }}
        """)
