import logging
from playwright.sync_api import Page, Locator
from utils.kendo_controls import KendoControls
from pages.document_page import DocumentPage
from pages.log_page import LogPage

logger = logging.getLogger(__name__)


class BasePage:
    """
    Core Base Page Object for Staff Portal E-Permitting System.
    Provides core page navigation, synchronization, DOM evaluation utilities,
    and delegates Kendo UI, Document management, and Communication Logging
    operations to specialized sub-components.
    """

    def __init__(self, page: Page):
        self.page = page

        # ── Modular Sub-Components (Lazy Evaluated to prevent God Object overhead) ─
        self._document_page = None
        self._log_page = None

        # ── Loading & Overlay Controls ─────────────────────────────────────────
        self.loading_overlay = page.locator(".k-loading-mask, .k-loading-image, #loading, .spinner-border")

    def __getattr__(self, name: str):
        """
        Dynamically delegates document and communication log attributes on-demand
        without eagerly constructing sub-components or blocking subclass attribute assignment.
        """
        doc_attrs = {
            "document_page", "attach_document_button", "document_type_dropdown",
            "choose_file_input", "save_document_button", "subject_input",
            "description_input", "create_package_button",
            "select_attachments_confirm_button", "ok_button"
        }
        if name in doc_attrs:
            if not hasattr(self, "_document_page") or self._document_page is None:
                self._document_page = DocumentPage(self.page)
            if name == "document_page":
                return self._document_page
            return getattr(self._document_page, name)

        log_attrs = {
            "log_page", "add_communication_button",
            "communication_modal_container", "communication_date_picker",
            "log_app_header"
        }
        if name in log_attrs:
            if not hasattr(self, "_log_page") or self._log_page is None:
                self._log_page = LogPage(self.page)
            if name == "log_page":
                return self._log_page
            return getattr(self._log_page, name)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # ── Core Navigation & Synchronization Mechanics ───────────────────────────

    def navigate(self, url: str) -> None:
        """Navigates to the specified URL."""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        self._wait_for_loader()

    def js_click(self, locator: Locator) -> None:
        """
        Dispatches a JS click event on the element target to bypass pointer/hit-testing
        interceptions caused by layout overlays or CSS zoom.
        """
        locator.wait_for(state="visible", timeout=15000)
        locator.evaluate("el => el.click()")

    def safe_click(self, locator: Locator) -> None:
        """Scrolls element into view and clicks safely."""
        locator.scroll_into_view_if_needed()
        locator.click()

    def scroll_to_locator(self, locator: Locator) -> None:
        """Scrolls an element into view smoothly if needed."""
        try:
            locator.scroll_into_view_if_needed()
        except Exception:
            pass

    def _wait_for_loader(self, timeout: int = 15000) -> None:
        """Waits for any active Kendo loading overlay masks or spinners to detach."""
        KendoControls.wait_for_loader(self.page, timeout=timeout)

    def assert_no_validation_errors(self) -> None:
        """
        Checks if any mandatory field validation error messages are visible on the page.
        If validation errors are present, raises AssertionError to fail the test immediately.
        """
        KendoControls.assert_no_validation_errors(self.page)

    # ── Kendo UI Controls Delegation Methods ───────────────────────────────────

    def _set_kendo_numeric_value(self, element_id: str, value: float) -> None:
        """Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API."""
        KendoControls.fill_numeric(self.page, element_id, value)

    def fill_kendo_numeric(self, element_id: str, value: float) -> None:
        """Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API."""
        KendoControls.fill_numeric(self.page, element_id, value)

    def select_all_kendo_dropdowns(self) -> None:
        """Selects the first valid option for every visible Kendo dropdown still showing a placeholder."""
        KendoControls.select_all_dropdowns(self.page)

    def select_first_dropdown_option(self, trigger_locator: Locator = None) -> None:
        """Universal dropdown selection helper."""
        KendoControls.select_first_dropdown_option(self.page, trigger_locator)

    def set_today_date(self, trigger_locator: Locator = None) -> str:
        """Universal date picker helper."""
        return KendoControls.set_today_date(self.page, trigger_locator)

    def select_kendo_location_dropdowns(self) -> None:
        """Sequentially selects valid options for location dropdowns."""
        KendoControls.select_location_dropdowns(self.page)

    def set_all_datefields_to_current(self) -> None:
        """Injects today's date directly into all Kendo DatePicker input controls."""
        KendoControls.set_all_datefields_to_current(self.page)

    # ── Document & Communication Page Object Delegations ───────────────────────

    def attach_document(
        self,
        file_path: str,
        subject: str = "Automated Subject",
        description: str = "Automated Description",
    ) -> None:
        """Delegates document upload workflow to DocumentPage component."""
        self.document_page.attach_document(file_path, subject, description)

    def add_communication(
        self,
        subject: str = "Automated Communication",
        description: str = "Communication Description",
    ) -> None:
        """Delegates communication record creation to LogPage component."""
        self.log_page.add_communication(subject, description)

    def create_package_and_verify(self) -> None:
        """Delegates document package creation workflow to DocumentPage component."""
        self.document_page.create_package_and_verify()
