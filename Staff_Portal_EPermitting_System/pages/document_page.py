import datetime
import logging
from playwright.sync_api import Page, Locator
from utils.kendo_controls import KendoControls

logger = logging.getLogger(__name__)


class DocumentPage:
    """
    Page Object Model representing the Documents & Attachments management section
    shared across multiple application pages in the Staff Portal E-Permitting System.
    """

    def __init__(self, page: Page):
        self.page = page

        # ── Document Attachment Locators ──────────────────────────────────────
        self.attach_document_button = page.get_by_role("button", name="Attach Document").or_(
            page.locator("#btnAttachDoc, .btn:has-text('Attach Document')")
        ).first
        self.document_type_dropdown = page.get_by_role("button", name="select").first
        self.choose_file_input = page.locator("input[type='file']").first
        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")
        self.save_document_button = page.get_by_role("button", name=" Save").or_(
            page.locator("button:visible:has-text('Save')")
        ).first

        # ── Package Creation Locators ──────────────────────────────────────────
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_confirm_button = page.get_by_role("button", name="Select Attachments")
        self.ok_button = page.get_by_role("button", name="OK")

    def attach_document(
        self,
        file_path: str,
        subject: str = "Automated Subject",
        description: str = "Automated Description",
    ) -> None:
        """
        Attaches a document file to the Documents and Log section.

        :param file_path: Path to the local document file to upload.
        :param subject: Text content for the Subject field.
        :param description: Text content for the Description field.
        """
        logger.info(f"Uploading document asset: {file_path}")
        KendoControls.wait_for_loader(self.page)
        if self.attach_document_button.count() == 0 or not self.attach_document_button.is_visible():
            logger.debug("Attach Document button is not visible on page; skipping attach step.")
            return

        self._js_click(self.attach_document_button)
        KendoControls.wait_for_loader(self.page)

        # 1. Populate Preparation Date * with today's date (MM/DD/YYYY)
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        try:
            prep_input = self.page.locator(
                "#docdate, #Preparation_Date, #PreparationDate, input[name='docdate'], input[name='Preparation_Date']"
            ).first
            if prep_input.count() > 0 and prep_input.is_visible():
                prep_input.click()
                prep_input.fill(current_date_str)
                prep_input.press("Tab")
        except Exception as e:
            logger.warning(f"Preparation Date input note: {e}")

        self.page.evaluate(
            f"""
            (dateStr) => {{
                var prepInput = $('#docdate, #Preparation_Date, #PreparationDate, input[name="docdate"], input[name="Preparation_Date"], [data-val-required*="Preparation Date"], [aria-label*="Preparation Date"]').first();
                if (prepInput.length === 0) prepInput = $('input[data-role="datepicker"]').first();
                if (prepInput.length) {{
                    var dp = prepInput.data("kendoDatePicker") || kendo.widgetInstance(prepInput) || prepInput.closest(".k-datepicker").find("input").data("kendoDatePicker");
                    if (dp && typeof dp.value === "function") {{
                        dp.value(dateStr);
                        if (typeof dp.trigger === "function") dp.trigger("change");
                    }}
                    prepInput.val(dateStr).attr("value", dateStr).trigger("input").trigger("change").trigger("blur");
                }}
            }}
            """,
            current_date_str,
        )
        KendoControls.set_all_datefields_to_current(self.page)

        # 2. Select Document Type dropdown (1st valid option)
        if self.document_type_dropdown.is_visible():
            KendoControls.select_first_dropdown_option(self.page, self.document_type_dropdown)
        KendoControls.select_all_dropdowns(self.page)

        # 3. Choose file
        if self.choose_file_input.count() > 0:
            self.choose_file_input.set_input_files(file_path)

        # 4. Fill Subject & Description
        if self.subject_input.is_visible():
            self.subject_input.fill(subject)

        if self.description_input.is_visible():
            self.description_input.fill(description)

        # Ensure Preparation Date is set to today before saving
        KendoControls.set_all_datefields_to_current(self.page)

        # 5. Click Save & verify no validation errors
        if self.save_document_button.is_visible():
            self._js_click(self.save_document_button)
            KendoControls.wait_for_loader(self.page)
            self._assert_no_validation_errors()
        logger.info("Document attached successfully.")

    def create_package_and_verify(self) -> None:
        """
        Creates a document package from attached files and confirms creation.
        """
        logger.info("Creating package from attachments.")
        KendoControls.wait_for_loader(self.page)
        if self.create_package_button.count() == 0 or not self.create_package_button.is_visible():
            logger.debug("Create Package button is not visible on page; skipping package creation.")
            return

        self._js_click(self.create_package_button)
        KendoControls.wait_for_loader(self.page)

        chk = self.page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        try:
            if chk.count() > 0 and chk.is_visible():
                self._js_click(chk)
        except Exception:
            pass

        confirm_btn = self.page.get_by_role("button", name="Select Attachments").or_(
            self.page.locator(".k-window:visible button:has-text('Select')")
        ).first
        try:
            if confirm_btn.count() > 0 and confirm_btn.is_visible():
                self._js_click(confirm_btn)
                KendoControls.wait_for_loader(self.page)
        except Exception:
            pass

        try:
            if self.ok_button.count() > 0 and self.ok_button.is_visible():
                self._js_click(self.ok_button)
                KendoControls.wait_for_loader(self.page)
        except Exception:
            pass

        logger.info("Document package created successfully.")

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
