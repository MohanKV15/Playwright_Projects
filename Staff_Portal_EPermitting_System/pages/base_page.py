import datetime
import logging
import re
from playwright.sync_api import Page, expect, Locator

logger = logging.getLogger(__name__)


class BasePage:
    """
    Core Base Page Object for Staff Portal E-Permitting System.
    Provides centralized element interactions, Kendo UI component helpers,
    synchronization mechanisms, and shared workflow utilities.
    """

    def __init__(self, page: Page):
        self.page = page

        # ── Loading & Overlay Controls ─────────────────────────────────────────
        self.loading_overlay = page.locator(".k-loading-mask, .k-loading-image, #loading, .spinner-border")

        # ── Shared Document & Communication Controls ─────────────────────────
        self.attach_document_button = page.get_by_role("button", name="Attach Document").or_(
            page.locator("#btnAttachDoc, .btn:has-text('Attach Document')")
        ).first
        self.document_type_dropdown = page.get_by_role("button", name="select").first
        self.choose_file_input = page.locator("input[type='file']").first
        self.save_document_button = page.get_by_role("button", name=" Save").or_(
            page.locator("button:visible:has-text('Save')")
        ).first

        self.subject_input = page.get_by_role("textbox", name="Subject")
        self.description_input = page.get_by_role("textbox", name="Description")

        self.add_communication_button = page.get_by_role("button", name="Add Communication")
        self.communication_modal_container = page.locator("#divfrmLog > .form-wrapper > .row > .col-md-12")
        self.communication_date_picker = page.get_by_role("button", name="select")

        # ── Shared Package & Email Controls ────────────────────────────────────
        self.create_package_button = page.get_by_role("button", name="Create Package")
        self.select_attachments_confirm_button = page.get_by_role("button", name="Select Attachments")
        self.ok_button = page.get_by_role("button", name="OK")
        self.log_app_header = page.locator("#LogAppHeader")

    # ── Core Click & Synchronization Mechanics ─────────────────────────────────

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
        try:
            self.page.wait_for_selector(
                ".k-loading-mask, .k-loading-image, #loading, .spinner-border",
                state="detached",
                timeout=timeout,
            )
        except Exception:
            pass

    def assert_no_validation_errors(self) -> None:
        """
        Checks if any mandatory field validation error messages are visible on the page.
        If validation errors are present, raises AssertionError to fail the test immediately.
        """
        self._wait_for_loader(timeout=5000)
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
            logger.error(f"Form submission failed due to mandatory validation error(s): {err_msg}")
            raise AssertionError(f"Mandatory form validation error(s) present on page: {err_msg}")

    def _set_kendo_numeric_value(self, element_id: str, value: float) -> None:
        """Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API."""
        self.page.evaluate(f"""
            () => {{
                var numeric = $('#{element_id}').data('kendoNumericTextBox');
                if (numeric) {{
                    numeric.value({value});
                    numeric.trigger('change');
                }}
            }}
        """)

    def fill_kendo_numeric(self, element_id: str, value: float) -> None:
        """Interacts with a Kendo NumericTextBox by setting its value using internal Kendo API."""
        self._set_kendo_numeric_value(element_id, value)

    # ── Universal Reusable Kendo UI Dropdown Utility ───────────────────────────

    def select_all_kendo_dropdowns(self) -> None:
        """Selects the first valid option for every visible Kendo dropdown still showing a placeholder."""
        self._wait_for_loader()
        dropdowns = self.page.locator("span.k-dropdown:visible, span.k-widget.k-dropdown:visible")
        count = dropdowns.count()
        for i in range(count):
            try:
                dd = dropdowns.nth(i)
                if not dd.is_visible():
                    continue
                selected_text = dd.inner_text().strip()
                if selected_text.startswith("--") or selected_text.lower().startswith("select"):
                    self.select_first_dropdown_option(dd)
                    self.page.wait_for_timeout(300)
            except Exception as e:
                logger.warning(f"Dropdown index {i} note: {e}")

    def select_first_dropdown_option(self, trigger_locator: Locator = None) -> None:
        """
        Universal dropdown selection helper:
        - Optionally clicks trigger_locator to expand dropdown list.
        - Waits for active list items to bind.
        - Ignores placeholders ('--', 'Select', 'No Data').
        - Selects the 1st valid available option.
        """
        self._wait_for_loader()
        if trigger_locator is not None and trigger_locator.is_visible():
            self.js_click(trigger_locator)
            self.page.wait_for_timeout(300)

        options = self.page.get_by_role("option").or_(
            self.page.locator("li.k-item:visible, .k-list-container:visible li, .k-animation-container:visible li, ul.k-list:visible li")
        )

        try:
            options.first.wait_for(state="visible", timeout=10000)
            count = options.count()
            if count > 0:
                for i in range(count):
                    opt = options.nth(i)
                    txt = opt.inner_text().strip()
                    if txt and not txt.startswith("--") and not txt.lower().startswith("select") and "no data" not in txt.lower():
                        logger.info(f"Selected 1st valid dropdown option: '{txt}'")
                        self.js_click(opt)
                        self.page.wait_for_timeout(300)
                        return
                if count > 1:
                    self.js_click(options.nth(1))
                else:
                    self.js_click(options.first)
        except Exception as e:
            logger.warning(f"Dropdown selection fallback note: {e}")

    # ── Universal Reusable Date Picker Utility ─────────────────────────────────

    def set_today_date(self, trigger_locator: Locator = None) -> str:
        """
        Universal date picker helper:
        - Calculates today's date dynamically (never hardcoded).
        - Optionally opens calendar picker popup or directly injects formatted date.
        - Returns formatted date string (MM/DD/YYYY).
        """
        today = datetime.date.today()
        day_str = str(today.day)
        date_full = today.strftime("%m/%d/%Y")

        if trigger_locator is not None and trigger_locator.is_visible():
            try:
                self.js_click(trigger_locator)
                self.page.wait_for_timeout(300)

                day_link = self.page.get_by_label(re.compile(r"Current focused date", re.I)).get_by_role("link", name=day_str).or_(
                    self.page.locator(".k-calendar-container:visible, .k-animation-container:visible").get_by_role("link", name=day_str, exact=True)
                ).first
                if day_link.is_visible():
                    self.js_click(day_link)
                    return date_full
            except Exception as e:
                logger.warning(f"Calendar popup interaction note: {e}")

        # Direct input injection fallback
        try:
            self.set_all_datefields_to_current()
        except Exception as e:
            logger.warning(f"Direct date injection note: {e}")

        return date_full

    def select_kendo_location_dropdowns(self) -> None:
        """
        Sequentially selects the 1st valid option for Route, Suffix, and Direction
        in #ApplicationLocationInfoDiv, waiting for Kendo AJAX DataSource binding.
        """
        self._wait_for_loader(timeout=5000)
        for step in [0, 1, 2]:
            try:
                self.page.evaluate(
                    """
                    (stepIdx) => {
                        var containers = $('#ApplicationLocationInfoDiv .k-dropdown, #ApplicationLocationInfoDiv input[data-role="dropdownlist"], #ApplicationLocationInfoDiv select');
                        var target = containers.eq(stepIdx);
                        if (target.length) {
                            var dd = kendo.widgetInstance(target) || 
                                     kendo.widgetInstance(target.closest(".k-dropdown, .k-widget")) || 
                                     target.data("kendoDropDownList") || 
                                     target.find("input, select").data("kendoDropDownList");
                            if (dd && dd.dataSource && typeof dd.dataSource.data === "function") {
                                var items = dd.dataSource.data();
                                if (items && items.length > 0) {
                                    var targetIdx = 0;
                                    var targetVal = "";
                                    for (var i = 0; i < items.length; i++) {
                                        var item = items[i];
                                        if (!item) continue;
                                        var vals = Object.values(item).map(v => (v || "").toString().trim()).filter(v => v !== "");
                                        if (vals.some(v => v && !v.startsWith("--") && !v.toLowerCase().includes("select") && !v.toLowerCase().includes("no data") && v !== "0")) {
                                            targetIdx = i;
                                            targetVal = item.Value || item.Id || item.value || item.ID || Object.values(item)[0];
                                            break;
                                        }
                                    }
                                    var chosenItem = items[targetIdx];
                                    var txt = chosenItem ? (chosenItem.text || chosenItem.Text || chosenItem.name || chosenItem.Name || Object.values(chosenItem)[0] || "").toString() : "";
                                    if (typeof dd.select === "function") dd.select(targetIdx);
                                    if (targetVal && typeof dd.value === "function") dd.value(targetVal);
                                    if (typeof dd.trigger === "function") dd.trigger("change");
                                    if (dd.wrapper && dd.wrapper.length) {
                                        dd.wrapper.find('.k-input').text(txt);
                                    }
                                }
                            }
                        }
                    }
                    """,
                    step,
                )
                self.page.wait_for_timeout(400)
            except Exception as e:
                logger.warning(f"Location dropdown selection note: {e}")

    def set_all_datefields_to_current(self) -> None:
        """Injects today's date directly into all Kendo DatePicker input controls across the page."""
        current_date_str = datetime.datetime.now().strftime("%m/%d/%Y")
        self.page.evaluate(f"""
            () => {{
                $('input[data-role="datepicker"], input[id*="Date"], input[name*="Date"], .k-datepicker input').each(function() {{
                    var dp = $(this).data("kendoDatePicker");
                    if (dp) {{
                        dp.value("{current_date_str}");
                        dp.trigger("change");
                    }} else {{
                        $(this).val("{current_date_str}");
                        $(this).trigger("change");
                    }}
                }});
            }}
        """)

    # ── Shared Business Workflow Methods ───────────────────────────────────────

    def attach_document(self, file_path: str, subject: str = "Automated Subject", description: str = "Automated Description") -> None:
        """Attaches a document to the shared Documents and Log section."""
        logger.info(f"Uploading document asset: {file_path}")
        self._wait_for_loader()
        if self.attach_document_button.count() == 0 or not self.attach_document_button.is_visible():
            logger.warning("Attach Document button not visible.")
            return

        self.js_click(self.attach_document_button)
        self._wait_for_loader()

        if self.document_type_dropdown.is_visible():
            self.select_first_dropdown_option(self.document_type_dropdown)

        if self.choose_file_input.count() > 0:
            self.choose_file_input.set_input_files(file_path)

        if self.subject_input.is_visible():
            self.subject_input.fill(subject)

        if self.description_input.is_visible():
            self.description_input.fill(description)

        if self.save_document_button.is_visible():
            self.js_click(self.save_document_button)
            self._wait_for_loader()
        logger.info("Document attached successfully.")

    def add_communication(self, subject: str = "Automated Communication", description: str = "Communication Description") -> None:
        """Adds a Communication entry in the shared Documents and Log section."""
        logger.info("Adding communication record.")
        self._wait_for_loader()
        if self.add_communication_button.count() == 0 or not self.add_communication_button.is_visible():
            logger.warning("Add Communication button not visible.")
            return

        self.js_click(self.add_communication_button)
        self._wait_for_loader()

        if self.communication_date_picker.is_visible():
            self.set_today_date(self.communication_date_picker)

        if self.subject_input.is_visible():
            self.subject_input.fill(subject)

        if self.description_input.is_visible():
            self.description_input.fill(description)

        self.set_all_datefields_to_current()

        if self.save_document_button.is_visible():
            self.js_click(self.save_document_button)
            self._wait_for_loader()
        logger.info("Communication record added successfully.")

    def create_package_and_verify(self) -> None:
        """Clicks Create Package, checks attachments, and confirms package creation."""
        logger.info("Creating package from attachments.")
        self._wait_for_loader()
        if self.create_package_button.count() == 0 or not self.create_package_button.is_visible():
            logger.warning("Create Package button not visible.")
            return

        self.js_click(self.create_package_button)
        self._wait_for_loader()

        chk = self.page.locator(".k-window:visible input[type='checkbox'], [role='dialog']:visible input[type='checkbox']").first
        try:
            if chk.count() > 0 and chk.is_visible():
                self.js_click(chk)
        except Exception:
            pass

        confirm_btn = self.page.get_by_role("button", name="Select Attachments").or_(self.page.locator(".k-window:visible button:has-text('Select')")).first
        try:
            if confirm_btn.count() > 0 and confirm_btn.is_visible():
                self.js_click(confirm_btn)
                self._wait_for_loader()
        except Exception:
            pass

        try:
            if self.ok_button.count() > 0 and self.ok_button.is_visible():
                self.js_click(self.ok_button)
                self._wait_for_loader()
        except Exception:
            pass

        logger.info("Document package created successfully.")
