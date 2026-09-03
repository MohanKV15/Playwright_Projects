import re
from playwright.sync_api import expect

class KendoMixin:
    """Mixin containing utility methods to cleanly interact with complex Kendo UI widgets."""

    # Set a Kendo masked textbox value and fire the events the form validation expects.
    def _set_masked_input_value(self, input_id: str, value: str):
        input_locator = self.page.locator(f"#{input_id}")
        try:
            if input_locator.count() == 0:
                return
        except Exception:
            return

        input_locator.first.wait_for(state="attached", timeout=15000)
        self.page.evaluate(
            """
            ({ id, value }) => {
                const el = document.getElementById(id);
                if (!el) return;

                const normalized = String(value ?? '');
                if (window.jQuery) {
                    const widget = window.jQuery(el).data('kendoMaskedTextBox');
                    if (widget) {
                        widget.value(normalized);
                        widget.trigger('change');
                    } else {
                        el.value = normalized;
                    }
                } else {
                    el.value = normalized;
                }

                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """,
            {"id": input_id, "value": value},
        )

    # Upload a file only when the target upload control exists on the page.
    def _upload_if_present(self, input_id: str, file_path: str):
        file_input = self.page.locator(f"input#{input_id}")
        try:
            if file_input.count() == 0:
                return
        except Exception:
            return
        file_input.first.set_input_files(file_path)
        try:
            self.page.wait_for_function(
                """
                (id) => {
                    const input = document.getElementById(id);
                    if (!input) return true;
                    const wrapper = input.closest('.k-upload');
                    if (!wrapper) return true;
                    const files = wrapper.querySelectorAll('.k-file');
                    if (files.length === 0) return false;
                    // Wait until at least one file has success state or checkmark
                    for (let f of files) {
                        if (f.classList.contains('k-file-success') || f.querySelector('.k-i-check') || f.querySelector('.k-file-state-success')) {
                            return true;
                        }
                    }
                    return false;
                }
                """,
                arg=input_id,
                timeout=5000,
            )
        except Exception:
            pass

        # Kendo upload can retain stale invalid CSS/aria even after successful upload.
        self.page.evaluate(
            """
            (id) => {
                const input = document.getElementById(id);
                if (!input) return;
                const wrapper = input.closest('.k-upload');
                if (!wrapper) return;
                const fileRows = wrapper.querySelectorAll('.k-file').length;
                if (fileRows <= 0) return;
                input.removeAttribute('aria-invalid');
                input.classList.remove('k-invalid');
                const msg = document.querySelector(`[data-valmsg-for="${id}"]`);
                if (msg) {
                    msg.classList.remove('field-validation-error');
                    msg.style.display = 'none';
                }
            }
            """,
            input_id,
        )
        self.page.wait_for_timeout(200)

    # Select the first option from a kendo dropdown by its hidden input id.
    def _select_kendo_dropdown_first_option(self, input_id: str):
        """Select the first available option from a kendo dropdown by hidden input id."""
        dropdown_input = self.page.locator(f"#{input_id}")
        if dropdown_input.count() == 0:
            return

        dropdown_input.first.wait_for(state="attached", timeout=15000)

        try:
            self.page.wait_for_function(
                """
                (id) => {
                    const el = document.getElementById(id);
                    if (!el || !window.jQuery) return false;
                    const ddl = window.jQuery(el).data('kendoDropDownList');
                    if (!ddl || !ddl.dataSource || !ddl.dataSource.view) return false;
                    return ddl.dataSource.view().length > 0;
                }
                """,
                arg=input_id,
                timeout=5000,
            )
        except Exception:
            pass

        selected = self.page.evaluate(
            """
            (id) => {
                const el = document.getElementById(id);
                if (!el || !window.jQuery) return false;
                const ddl = window.jQuery(el).data('kendoDropDownList');
                if (!ddl || !ddl.dataSource) return false;
                const rows = ddl.dataSource.view();
                if (rows.length === 0) return false;
                // Select the first item
                const item = rows[0];
                const valueField = ddl.options?.dataValueField;
                const textField = ddl.options?.dataTextField;
                if (valueField && item[valueField] != null) {
                    ddl.value(item[valueField]);
                } else if (textField && item[textField] != null) {
                    ddl.text(item[textField]);
                } else {
                    ddl.select(0);
                }
                ddl.trigger('change');
                return true;
            }
            """,
            input_id,
        )

        if selected:
            return

        trigger = self.page.locator(f"span[aria-owns='{input_id}_listbox']")
        if trigger.count() == 0:
            return
        self._scroll_and_click(trigger.first, timeout_ms=15000)
        # Get the first option in the dropdown
        first_option = self.page.get_by_role("option").first
        expect(first_option).to_be_visible(timeout=15000)
        first_option.click()

    # Select a Kendo dropdown value by its hidden input id.
    def _select_kendo_dropdown_by_id(self, input_id: str, option_text: str):
        """Select an option from a kendo dropdown by hidden input id."""
        dropdown_input = self.page.locator(f"#{input_id}")
        if dropdown_input.count() == 0:
            return

        dropdown_input.first.wait_for(state="attached", timeout=15000)

        try:
            self.page.wait_for_function(
                """
                (id) => {
                    const el = document.getElementById(id);
                    if (!el || !window.jQuery) return false;
                    const ddl = window.jQuery(el).data('kendoDropDownList');
                    if (!ddl || !ddl.dataSource || !ddl.dataSource.view) return false;
                    return ddl.dataSource.view().length > 0;
                }
                """,
                arg=input_id,
                timeout=5000,
            )
        except Exception:
            pass

        selected = self.page.evaluate(
            """
            ({ id, text }) => {
                const el = document.getElementById(id);
                if (!el || !window.jQuery) return false;
                const ddl = window.jQuery(el).data('kendoDropDownList');
                if (!ddl || !ddl.dataSource) return false;
                const rows = ddl.dataSource.view();
                const wanted = String(text).trim().toLowerCase();
                const getCandidates = (item) => {
                    if (!item || typeof item !== 'object') return [];
                    const fieldNames = [
                        ddl.options?.dataTextField,
                        ddl.options?.dataValueField,
                        'Text',
                        'text',
                        'Label',
                        'label',
                        'Name',
                        'name',
                        'Description',
                        'description',
                        'land_use_des',
                        'land_use_cde',
                        'Value',
                        'value',
                    ].filter(Boolean);
                    const values = [];
                    for (const key of fieldNames) {
                        if (item[key] != null) values.push(String(item[key]).trim().toLowerCase());
                    }
                    return values;
                };

                const selectItem = (item, index) => {
                    const valueField = ddl.options?.dataValueField;
                    const textField = ddl.options?.dataTextField;
                    if (valueField && item[valueField] != null) {
                        ddl.value(item[valueField]);
                    } else if (textField && item[textField] != null) {
                        ddl.text(item[textField]);
                    } else {
                        ddl.select(index);
                    }
                    ddl.trigger('change');
                    return true;
                };

                for (let i = 0; i < rows.length; i++) {
                    const item = rows[i];
                        const candidates = getCandidates(item);
                        if (candidates.some((value) => value === wanted)) {
                            return selectItem(item, i);
                        }
                    }

                    for (let i = 0; i < rows.length; i++) {
                        const item = rows[i];
                        const candidates = getCandidates(item);
                        if (candidates.some((value) => value.includes(wanted))) {
                            return selectItem(item, i);
                    }
                }
                return false;
            }
            """,
            {"id": input_id, "text": option_text},
        )

        if selected:
            return

        trigger = self.page.locator(f"span[aria-owns='{input_id}_listbox']")
        if trigger.count() == 0:
            return
        self._scroll_and_click(trigger.first, timeout_ms=15000)
        option = self.page.get_by_role("option", name=re.compile(rf"^{re.escape(option_text)}$", re.I)).first
        expect(option).to_be_visible(timeout=15000)
        option.click()

    # Set a Kendo numeric textbox value while keeping native-input fallback behavior.
    def _set_kendo_numeric_value(self, input_id: str, value: float):
        input_locator = self.page.locator(f"#{input_id}")
        if input_locator.count() == 0:
            return

        input_locator.first.wait_for(state="attached", timeout=15000)
        self.page.evaluate(
            """
            ({ id, value }) => {
                const el = document.getElementById(id);
                if (!el) return;
                if (window.jQuery) {
                    const num = window.jQuery(el).data('kendoNumericTextBox');
                    if (num) {
                        num.value(value);
                        num.trigger('change');
                    }
                }
                el.value = String(value);
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """,
            {"id": input_id, "value": value},
        )
