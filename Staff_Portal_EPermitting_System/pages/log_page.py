import logging
from playwright.sync_api import Page, Locator, expect
from utils.kendo_controls import KendoControls

logger = logging.getLogger(__name__)


class LogPage:
    """
    Page Object Model representing the Communication Log and Activity History section
    shared across multiple application pages in the Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        self.page = page

        # ── Communication & Log Locators ──────────────────────────────────────
        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_container = page.locator("#divfrmLog > .form-wrapper > .row > .col-md-12")
        self.communication_date_picker = page.get_by_role("button", name="select")

        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")
        self.save_button = page.get_by_role("button", name=" Save").or_(
            page.locator("button:visible:has-text('Save')")
        ).first

        self.log_app_header = page.locator("#LogAppHeader")

    def add_communication(
        self,
        subject: str = "Automated Communication",
        description: str = "Communication Description",
    ) -> None:
        """
        Adds a new Communication entry in the shared Documents and Log section.

        :param subject: Text content for the Communication Subject.
        :param description: Text content for the Communication Description.
        """
        logger.info("Adding communication record.")
        KendoControls.wait_for_loader(self.page)
        if self.add_communication_button.count() == 0 or not self.add_communication_button.is_visible():
            logger.debug("Add Communication button is not visible on page; skipping communication step.")
            return

        self._js_click(self.add_communication_button)
        KendoControls.wait_for_loader(self.page)

        if self.communication_date_picker.is_visible():
            KendoControls.set_today_date(self.page, self.communication_date_picker)

        KendoControls.select_all_dropdowns(self.page)

        if self.subject_input.is_visible():
            self.subject_input.fill(subject)

        if self.description_input.is_visible():
            self.description_input.fill(description)

        KendoControls.set_all_datefields_to_current(self.page)

        if self.save_button.is_visible():
            self._js_click(self.save_button)
            KendoControls.wait_for_loader(self.page)
            self._assert_no_validation_errors()
        logger.info("Communication record added successfully.")

    def verify_log_header(self, timeout: int = 15000) -> None:
        """
        Verifies that the Log App Header element is visible on the page.

        :param timeout: Maximum wait time in milliseconds.
        """
        logger.info("Verifying Log App Header visibility.")
        expect(self.log_app_header).to_be_visible(timeout=timeout)

    def _js_click(self, locator: Locator) -> None:
        """Dispatches a JS click event on the target element."""
        locator.wait_for(state="visible", timeout=15000)
        locator.evaluate("el => el.click()")

    def _assert_no_validation_errors(self) -> None:
        """Fails test execution if validation error messages are displayed."""
        KendoControls.wait_for_loader(self.page, timeout=5000)
        error_locators = self.page.locator(
            ".field-validation-error:visible, "
            "span.text-danger:visible, "
            ".k-tooltip-validation:visible, "
            "[data-valmsg-summary='true']:visible li, "
            ".validation-summary-errors:visible li"
        )
        count = error_locators.count()
        visible_errors = []
        for i in range(count):
            err = error_locators.nth(i)
            txt = err.inner_text().strip()
            if txt and not txt.startswith("--") and "success" not in txt.lower():
                visible_errors.append(txt)

        if visible_errors:
            err_msg = "; ".join(visible_errors)
            logger.error(f"Form validation error(s) present: {err_msg}")
            raise AssertionError(f"Mandatory form validation error(s) present on page: {err_msg}")
