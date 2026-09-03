import re


class KendoUtils:
    """Helper methods for interacting with Kendo widgets."""

    def __init__(self, page, logger=None):
        self.page = page
        self.logger = logger

    def set_numeric_textbox_value(self, input_id: str, value: float) -> None:
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
                        return;
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

    def set_masked_input(self, input_id: str, value: str) -> None:
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
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """,
            {"id": input_id, "value": value},
        )

    def select_dropdown_first_option(self, input_id: str) -> bool:
        selected = self.page.evaluate(
            """
            (id) => {
                const el = document.getElementById(id);
                if (!el || !window.jQuery) return false;
                const ddl = window.jQuery(el).data('kendoDropDownList');
                if (!ddl || !ddl.dataSource) return false;
                const rows = ddl.dataSource.view();
                if (!rows || rows.length === 0) return false;
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
            return True

        # UI fallback: open dropdown trigger and pick first visible option via DOM click.
        trigger = self.page.locator(f"span[aria-owns='{input_id}_listbox']")
        if trigger.count() == 0:
            return False
        try:
            trigger.first.wait_for(state="visible", timeout=10000)
            trigger.first.scroll_into_view_if_needed()
            trigger.first.click(timeout=10000)
        except Exception:
            return False

        # JS click avoids transient overlay/pointer interception from kendo animation container.
        selected_via_dom = self.page.evaluate(
            """
            (id) => {
                const listboxId = `${id}_listbox`;
                const listbox = document.getElementById(listboxId);
                const option = listbox?.querySelector("li[role='option']");
                if (!option) return false;
                option.scrollIntoView({ block: 'nearest' });
                option.click();
                return true;
            }
            """,
            input_id,
        )
        return bool(selected_via_dom)

    def select_dropdown_by_text(self, input_id: str, option_text: str) -> bool:
        selected = self.page.evaluate(
            """
            ({ id, text }) => {
                const el = document.getElementById(id);
                if (!el || !window.jQuery) return false;
                const ddl = window.jQuery(el).data('kendoDropDownList');
                if (!ddl || !ddl.dataSource) return false;
                const rows = ddl.dataSource.view() || [];
                const wanted = String(text).trim().toLowerCase();
                const fields = [
                    ddl.options?.dataTextField, ddl.options?.dataValueField,
                    'Text', 'text', 'Label', 'label', 'Name', 'name', 'Description', 'description'
                ].filter(Boolean);
                for (let i = 0; i < rows.length; i++) {
                    const item = rows[i];
                    const candidates = fields
                        .map((f) => item?.[f])
                        .filter((v) => v != null)
                        .map((v) => String(v).trim().toLowerCase());
                    if (candidates.some((v) => v === wanted || v.includes(wanted))) {
                        const valueField = ddl.options?.dataValueField;
                        const textField = ddl.options?.dataTextField;
                        if (valueField && item[valueField] != null) ddl.value(item[valueField]);
                        else if (textField && item[textField] != null) ddl.text(item[textField]);
                        else ddl.select(i);
                        ddl.trigger('change');
                        return true;
                    }
                }
                return false;
            }
            """,
            {"id": input_id, "text": option_text},
        )
        if selected:
            return True

        trigger = self.page.locator(f"span[aria-owns='{input_id}_listbox']")
        if trigger.count() == 0:
            return False
        trigger.first.click()
        option = self.page.get_by_role("option", name=re.compile(rf"^{re.escape(option_text)}$", re.I)).first
        option.wait_for(state="visible", timeout=15000)
        option.click()
        return True
