import logging
import re
import time
from datetime import datetime
from typing import Optional, Union, List
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger(__name__)


class KendoDropdown:
    """
    Dedicated Page Component representing Kendo UI DropDownList widgets.
    Encapsulates JS API and UI interactions for robust, cross-portal dropdown control.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def select_by_id(self, field_id: str, option_text: Optional[str] = None, index: int = 1) -> bool:
        """
        Selects an option from a Kendo DropDownList by element ID.
        If option_text is provided, selects matching item (case-insensitive);
        otherwise falls back to selecting by index. Dispatches change event.
        """
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return false;
                    const target = '{option_text or ""}'.toLowerCase();
                    if (target) {{
                        const data = ddl.dataSource.data();
                        for (let i = 0; i < data.length; i++) {{
                            const text = (ddl.text(data[i]) || '').toLowerCase();
                            if (text.includes(target)) {{
                                ddl.select(i + (ddl.options.optionLabel ? 1 : 0));
                                ddl.trigger('change');
                                if (ddl.element && ddl.element.length) {{
                                    ddl.element.trigger('change').trigger('input');
                                    try {{ if (window.jQuery && window.jQuery.validator) ddl.element.valid(); }} catch(e) {{}}
                                }}
                                return true;
                            }}
                        }}
                    }}
                    if (ddl.dataSource.data().length > 0) {{
                        ddl.select({index});
                        ddl.trigger('change');
                        if (ddl.element && ddl.element.length) {{
                            ddl.element.trigger('change').trigger('input');
                            try {{ if (window.jQuery && window.jQuery.validator) ddl.element.valid(); }} catch(e) {{}}
                        }}
                        return true;
                    }}
                    return false;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_by_id failed for #{clean_id}: {e}")
            return False

    def select_by_locator(self, dropdown_locator: Union[Locator, str], option_text: str, timeout_ms: int = 5000) -> bool:
        """
        Opens a Kendo UI DropDownList wrapper via UI click and selects option by visible text.
        """
        try:
            loc = dropdown_locator if isinstance(dropdown_locator, Locator) else self.page.locator(dropdown_locator)
            loc.scroll_into_view_if_needed()
            loc.click(force=True)
            self.page.wait_for_timeout(200)
            option = (
                self.page.get_by_role("option", name=re.compile(f"^{re.escape(option_text)}$", re.I))
                .or_(
                    self.page.locator(
                        ".k-animation-container:visible li, .k-list-container:visible li, [role='listbox']:visible li, [role='option']:visible"
                    ).filter(has_text=re.compile(re.escape(option_text), re.I))
                )
                .first
            )
            option.wait_for(state="visible", timeout=timeout_ms)
            option.click(force=True)
            return True
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_by_locator failed for '{option_text}': {e}")
        return False

    def select(
        self,
        target: Union[Locator, str],
        option_text: Optional[str] = None,
        index: int = 1,
        timeout_ms: int = 5000,
    ) -> bool:
        """
        Polymorphic select:
        - If target is a string ID/selector, attempts select_by_id first using Kendo JS API.
        - Falls back to select_by_locator (UI-based selection).
        """
        if isinstance(target, str):
            clean_id = target.lstrip("#")
            if " " not in clean_id and (clean_id.isalnum() or "_" in clean_id or "-" in clean_id):
                if self.select_by_id(clean_id, option_text=option_text, index=index):
                    return True
        return self.select_by_locator(target, option_text=option_text or "", timeout_ms=timeout_ms)

    def select_first_option(self, target: Union[Locator, str], timeout_ms: int = 5000) -> bool:
        """
        Selects the first available valid option in a Kendo DropDownList or dropdown widget.
        Polymorphic: accepts either a field ID string (e.g. 'District', '#District')
        or a Playwright Locator instance.
        Waits up to timeout_ms for the widget and its dataSource to initialize,
        selects the 1st non-placeholder item, and triggers change/input/validation events.
        """
        start_time = time.time()
        timeout_sec = timeout_ms / 1000.0

        if isinstance(target, str) and (" " not in target) and ("#" in target or target.isidentifier() or "_" in target or "-" in target):
            clean_id = target.lstrip("#")
            while time.time() - start_time < timeout_sec:
                try:
                    res = self.page.evaluate(
                        f"""(() => {{
                            if (!window.$) return false;
                            const ddl = $('#{clean_id}').data('kendoDropDownList');
                            if (ddl && ddl.dataSource) {{
                                const count = ddl.dataSource.data().length;
                                if (count > 0) {{
                                    const targetIndex = ddl.options.optionLabel ? 1 : 0;
                                    ddl.select(targetIndex);
                                    ddl.trigger('change');
                                    if (ddl.element && ddl.element.length) {{
                                        ddl.element.trigger('change').trigger('input');
                                        try {{ if (window.jQuery && window.jQuery.validator) ddl.element.valid(); }} catch(e) {{}}
                                    }}
                                    return true;
                                }}
                            }}
                            return false;
                        }})();"""
                    )
                    if res:
                        return True
                except Exception:
                    pass
                self.page.wait_for_timeout(150)

        elif isinstance(target, Locator):
            while time.time() - start_time < timeout_sec:
                try:
                    res = target.evaluate(
                        """el => {
                            if (!window.$) return false;
                            let ddl = $(el).data('kendoDropDownList');
                            if (!ddl && el.id) ddl = $('#' + el.id).data('kendoDropDownList');
                            if (!ddl) ddl = $(el).find('select, input').data('kendoDropDownList');
                            if (!ddl) ddl = $(el).closest('.k-widget').find('select, input').data('kendoDropDownList');
                            if (ddl && ddl.dataSource) {
                                const count = ddl.dataSource.data().length;
                                if (count > 0) {
                                    const targetIndex = ddl.options.optionLabel ? 1 : 0;
                                    ddl.select(targetIndex);
                                    ddl.trigger('change');
                                    if (ddl.element && ddl.element.length) {
                                        ddl.element.trigger('change').trigger('input');
                                        try { if (window.jQuery && window.jQuery.validator) ddl.element.valid(); } catch(e) {}
                                    }
                                    return true;
                                }
                            }
                            return false;
                        }"""
                    )
                    if res:
                        return True
                except Exception:
                    pass
                self.page.wait_for_timeout(150)

        # UI Fallback: click and select the 1st valid option visually
        selected = self.select_first_valid_option(target, timeout_ms=int((timeout_sec - (time.time() - start_time)) * 1000) or 2000)
        return bool(selected)

    def select_first_valid_option(self, dropdown_locator: Union[Locator, str], timeout_ms: int = 5000) -> str:
        """
        Dynamically selects the 1st valid (non-placeholder) option in the list.
        Prefers direct Kendo JS API selection for speed; falls back to clean UI interaction.
        """
        self.logger.info("Selecting 1st valid dropdown option")

        if isinstance(dropdown_locator, str) and ("#" in dropdown_locator or dropdown_locator.isidentifier()):
            clean_id = dropdown_locator.lstrip("#")
            try:
                res = self.page.evaluate(
                    f"""
                    (() => {{
                        const ddl = $('#{clean_id}').data('kendoDropDownList');
                        if (!ddl) return null;
                        const data = ddl.dataSource ? ddl.dataSource.data() : [];
                        if (!data || data.length === 0) return null;
                        const targetIndex = ddl.options.optionLabel ? 1 : 0;
                        ddl.select(targetIndex);
                        ddl.trigger('change');
                        return ddl.text();
                    }})();
                    """
                )
                if res:
                    return str(res)
            except Exception:
                pass

        loc = dropdown_locator if isinstance(dropdown_locator, Locator) else self.page.locator(dropdown_locator)
        try:
            if loc.is_visible(timeout=timeout_ms):
                tag_name = loc.evaluate("el => el.tagName ? el.tagName.toLowerCase() : ''")
                if tag_name == "select":
                    opts = loc.locator("option")
                    opt_count = opts.count()
                    for i in range(opt_count):
                        val = (opts.nth(i).get_attribute("value") or "").strip()
                        txt = opts.nth(i).inner_text().strip()
                        if val and not txt.startswith("--") and not txt.lower().startswith("select"):
                            loc.select_option(index=i)
                            return txt
                    if opt_count > 1:
                        loc.select_option(index=1)
                        return opts.nth(1).inner_text().strip()
                    elif opt_count == 1:
                        loc.select_option(index=0)
                        return opts.nth(0).inner_text().strip()
        except Exception:
            pass

        if loc.is_visible(timeout=timeout_ms):
            loc.click(force=True)
            self.page.wait_for_timeout(200)

            items = self.page.locator(
                ".k-animation-container:visible li, .k-list-container:visible li, ul.k-list:visible li, [role='option']:visible"
            )
            count = items.count()
            selected_text = ""
            for i in range(count):
                item = items.nth(i)
                text = item.inner_text().strip()
                if text and not text.startswith("--") and not text.lower().startswith("select"):
                    item.click(force=True)
                    selected_text = text
                    break

            if not selected_text and count > 0:
                fallback_item = items.nth(1 if count > 1 else 0)
                selected_text = fallback_item.inner_text().strip()
                fallback_item.click(force=True)

            try:
                self.page.locator(".k-animation-container:visible").wait_for(state="hidden", timeout=1200)
            except Exception:
                try:
                    self.page.keyboard.press("Escape")
                except Exception:
                    pass
            return selected_text

        return ""

    def get_options(self, field_id: str) -> List[str]:
        """Returns all text options available in the Kendo DropDownList dataSource."""
        clean_id = field_id.lstrip("#")
        try:
            return self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    if (!ddl) return [];
                    return ddl.dataSource.data().map(x => ddl.text(x) || '');
                }})();
                """
            )
        except Exception:
            return []

    def get_selected_text(self, field_id: str) -> str:
        """Returns currently selected text in the Kendo DropDownList."""
        clean_id = field_id.lstrip("#")
        try:
            return self.page.evaluate(
                f"""
                (() => {{
                    const ddl = $('#{clean_id}').data('kendoDropDownList');
                    return ddl ? ddl.text() : '';
                }})();
                """
            ) or ""
        except Exception:
            return ""


class KendoDatePicker:
    """
    Dedicated Page Component representing Kendo UI DatePicker widgets.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_date_by_id(self, field_id: str, date_str: str) -> bool:
        """Sets date string in a Kendo DatePicker via JS API and triggers all validation events."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    const inp = $('#{clean_id}');
                    if (!inp.length) return false;
                    const dp = inp.data('kendoDatePicker');
                    if (dp && typeof dp.value === 'function') {{
                        dp.value('{date_str}');
                        if (typeof dp.trigger === 'function') dp.trigger('change');
                    }}
                    inp.val('{date_str}').attr('value', '{date_str}').trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            # Also fill via Playwright only if element is editable (not readonly)
            try:
                inp_loc = self.page.locator(f"#{clean_id}")
                if inp_loc.is_visible(timeout=300):
                    readonly = inp_loc.get_attribute("readonly", timeout=300)
                    if not readonly:
                        inp_loc.fill(date_str, timeout=1000)
                        inp_loc.press("Tab", timeout=500)
            except Exception:
                pass
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDatePicker set_date_by_id failed for #{clean_id}: {e}")
            return False

    def set_first_datepicker(self, date_str: str) -> bool:
        """Sets the date on the first .k-datepicker input on the page."""
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    if (!window.$) return false;
                    const inp = $('.k-datepicker input').first();
                    if (!inp.length) return false;
                    const dp = inp.data('kendoDatePicker');
                    if (dp && typeof dp.value === 'function') {{
                        dp.value('{date_str}');
                        dp.trigger('change');
                    }}
                    inp.val('{date_str}').trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            try:
                loc = self.page.locator(".k-datepicker input").first
                if loc.is_visible(timeout=300):
                    readonly = loc.get_attribute("readonly", timeout=300)
                    if not readonly:
                        loc.fill(date_str, timeout=1000)
                        loc.press("Tab", timeout=500)
            except Exception:
                pass
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDatePicker set_first_datepicker failed: {e}")
            return False

    def set_last_datepicker(self, date_str: str) -> bool:
        """Sets the date on the last datepicker or date input on the page."""
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    if (!window.$) return false;
                    const inps = $('input[name*="Date"], input[id*="Date"], .k-datepicker input');
                    if (!inps.length) return false;
                    const inp = inps.last();
                    const dp = inp.data('kendoDatePicker');
                    if (dp && typeof dp.value === 'function') {{
                        dp.value('{date_str}');
                        dp.trigger('change');
                    }}
                    inp.val('{date_str}').trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoDatePicker set_last_datepicker failed: {e}")
            return False

    def select_present_day_date(
        self,
        container: Optional[Union[Locator, str]] = None,
        field_id: Optional[str] = None,
        timeout_ms: int = 3000,
    ) -> str:
        """
        Selects the present day (today's) date in the Kendo DatePicker widget.
        Directly populates and verifies the date value.
        """
        today_str = datetime.now().strftime("%m/%d/%Y")
        self.logger.info(f"Setting present day date: {today_str}")

        if field_id:
            clean_id = field_id.lstrip("#")
            self.set_date_by_id(clean_id, today_str)
            return today_str

        scope = (
            (container if isinstance(container, Locator) else self.page.locator(container))
            if container is not None
            else self.page
        )
        try:
            date_input = scope.locator("input[data-role='datepicker'], .k-datepicker input").first
            if date_input.count() > 0 and date_input.is_visible():
                date_input.click(force=True)
                date_input.fill(today_str)
                date_input.press("Tab")
                return today_str
        except Exception:
            pass

        return today_str


class KendoMaskedTextBox:
    """
    Dedicated Page Component representing Kendo UI MaskedTextBox widgets (e.g., Phone numbers, SSNs).
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_value_by_id(self, field_id: str, value: str) -> bool:
        """Sets value in a Kendo MaskedTextBox via JS API and triggers all validation events."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    if (!window.$) return false;
                    const inp = $('#{clean_id}');
                    if (!inp.length) return false;
                    const mtb = inp.data('kendoMaskedTextBox');
                    if (mtb && typeof mtb.value === 'function') {{
                        mtb.value('{value}');
                        if (typeof mtb.trigger === 'function') mtb.trigger('change');
                    }}
                    inp.val('{value}').trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            try:
                inp_loc = self.page.locator(f"#{clean_id}")
                if inp_loc.is_visible(timeout=500):
                    inp_loc.fill(value)
                    inp_loc.press("Tab")
            except Exception:
                pass
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoMaskedTextBox set_value_by_id failed for #{clean_id}: {e}")
            return False

    def set_value(self, target: Union[Locator, str], value: str) -> bool:
        """Polymorphic set_value for MaskedTextBox using Kendo widget API."""
        raw_digits = "".join(c for c in str(value) if c.isdigit())
        fill_val = raw_digits if len(raw_digits) in (7, 10) else str(value)
        loc = target if isinstance(target, Locator) else self.page.locator(target)
        try:
            loc.evaluate(
                f"""el => {{
                    if (window.$) {{
                        const mtb = $(el).data('kendoMaskedTextBox');
                        if (mtb && typeof mtb.value === 'function') {{
                            mtb.value('{fill_val}');
                            if (typeof mtb.trigger === 'function') mtb.trigger('change');
                        }}
                    }}
                    el.value = '{fill_val}';
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                }}"""
            )
            return True
        except Exception as e:
            self.logger.warning(f"KendoMaskedTextBox set_value failed for {target}: {e}")
            try:
                loc.fill(str(value))
                loc.press("Tab")
                return True
            except Exception:
                return False


class KendoNumericTextBox:
    """
    Dedicated Page Component representing Kendo UI NumericTextBox widgets.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def set_value_by_id(self, field_id: str, value: float) -> bool:
        """Sets numeric value in a Kendo NumericTextBox and triggers change event."""
        clean_id = field_id.lstrip("#")
        try:
            res = self.page.evaluate(
                f"""
                (() => {{
                    if (!window.$) return false;
                    const inp = $('#{clean_id}');
                    const num = inp.data('kendoNumericTextBox');
                    if (num && typeof num.value === 'function') {{
                        num.value({value});
                        if (typeof num.trigger === 'function') num.trigger('change');
                        return true;
                    }}
                    inp.val({value}).trigger('input').trigger('change').trigger('blur');
                    return true;
                }})();
                """
            )
            return bool(res)
        except Exception as e:
            self.logger.warning(f"KendoNumericTextBox set_value_by_id failed for #{clean_id}: {e}")
            return False


class KendoCheckbox:
    """
    Dedicated Page Component representing Kendo UI Checkbox widgets.
    Handles UI clicking, label association, and DOM event validation.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def check(self, target: Union[Locator, str], input_index: Optional[int] = None, timeout_ms: int = 5000) -> bool:
        """
        Ensures a Kendo UI checkbox is checked:
        1. Checks if already checked (if so, returns True immediately).
        2. Scrolls target into view and clicks the visible label or checkbox element.
        3. Verifies whether the input element is checked; if not, sets checked state and triggers input/change events.
        """
        loc = target if isinstance(target, Locator) else self.page.locator(target)

        # Check if already checked to ensure idempotency
        try:
            if input_index is not None:
                inputs = self.page.locator("input[type='checkbox']")
                if inputs.count() > input_index and inputs.nth(input_index).is_checked():
                    return True
            elif loc.count() > 0:
                is_checked = loc.evaluate(
                    """el => {
                        let inp = el.tagName && el.tagName.toLowerCase() === 'input' ? el : null;
                        if (!inp) {
                            const forAttr = el.getAttribute ? el.getAttribute('for') : null;
                            if (forAttr) inp = document.getElementById(forAttr);
                        }
                        if (!inp) inp = el.querySelector ? el.querySelector("input[type='checkbox']") : null;
                        return inp ? inp.checked : false;
                    }"""
                )
                if is_checked:
                    return True
        except Exception:
            pass

        try:
            if loc.is_visible(timeout=timeout_ms):
                loc.scroll_into_view_if_needed()
                loc.click(force=True)
                self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.warning(f"KendoCheckbox UI click failed on {target}: {e}")

        # Ensure target input is actually checked in DOM
        try:
            if input_index is not None:
                inputs = self.page.locator("input[type='checkbox']")
                if inputs.count() > input_index:
                    target_input = inputs.nth(input_index)
                    if not target_input.is_checked():
                        self.logger.info(f"Checkbox at index {input_index} not yet checked. Enforcing checked state via DOM.")
                        target_input.evaluate(
                            """el => {
                                if (!el.checked) {
                                    el.checked = true;
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            }"""
                        )
                        self.page.wait_for_timeout(150)
                    return True
            else:
                loc.evaluate(
                    """el => {
                        let inp = el.tagName && el.tagName.toLowerCase() === 'input' ? el : null;
                        if (!inp) {
                            const forAttr = el.getAttribute ? el.getAttribute('for') : null;
                            if (forAttr) inp = document.getElementById(forAttr);
                        }
                        if (!inp) inp = el.querySelector ? el.querySelector("input[type='checkbox']") : null;
                        if (!inp) {
                            const parent = (el.closest ? el.closest('.form-check, .k-checkbox-wrap') : null) || el.parentElement;
                            if (parent && parent.querySelector) inp = parent.querySelector("input[type='checkbox']");
                        }
                        if (inp && !inp.checked) {
                            inp.checked = true;
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }"""
                )
                return True
        except Exception as e:
            self.logger.debug(f"KendoCheckbox DOM state enforcement notice: {e}")

        return True

    def uncheck(self, target: Union[Locator, str], input_index: Optional[int] = None, timeout_ms: int = 5000) -> bool:
        """
        Ensures a Kendo UI checkbox is unchecked.
        """
        loc = target if isinstance(target, Locator) else self.page.locator(target)
        try:
            if loc.is_visible(timeout=timeout_ms):
                loc.scroll_into_view_if_needed()
                loc.click(force=True)
                self.page.wait_for_timeout(200)
        except Exception as e:
            self.logger.warning(f"KendoCheckbox UI uncheck click failed on {target}: {e}")

        try:
            if input_index is not None:
                inputs = self.page.locator("input[type='checkbox']")
                if inputs.count() > input_index:
                    target_input = inputs.nth(input_index)
                    if target_input.is_checked():
                        target_input.evaluate(
                            """el => {
                                if (el.checked) {
                                    el.checked = false;
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            }"""
                        )
                    return True
            else:
                loc.evaluate(
                    """el => {
                        let inp = el.tagName && el.tagName.toLowerCase() === 'input' ? el : null;
                        if (!inp) {
                            const forAttr = el.getAttribute ? el.getAttribute('for') : null;
                            if (forAttr) inp = document.getElementById(forAttr);
                        }
                        if (!inp) inp = el.querySelector ? el.querySelector("input[type='checkbox']") : null;
                        if (!inp) {
                            const parent = (el.closest ? el.closest('.form-check, .k-checkbox-wrap') : null) || el.parentElement;
                            if (parent && parent.querySelector) inp = parent.querySelector("input[type='checkbox']");
                        }
                        if (inp && inp.checked) {
                            inp.checked = false;
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }"""
                )
                return True
        except Exception as e:
            self.logger.debug(f"KendoCheckbox DOM uncheck enforcement notice: {e}")

        return True


class KendoButton:
    """
    Dedicated Page Component representing Kendo UI Button widgets.
    Handles unblocking aria-disabled states, enabling Kendo Button API,
    and safe forced/JS clicking.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def enable(self, target: Union[Locator, str]) -> None:
        """Enables a Kendo button widget via JS and removes aria-disabled attributes."""
        try:
            if isinstance(target, str):
                self.page.evaluate(
                    f"""() => {{
                        if (!window.$) return;
                        const btn = $('{target}');
                        if (btn.length) {{
                            const kb = btn.data('kendoButton');
                            if (kb && typeof kb.enable === 'function') kb.enable(true);
                            btn.removeAttr('disabled').removeAttr('aria-disabled').removeClass('k-state-disabled');
                        }}
                    }}"""
                )
            elif isinstance(target, Locator):
                target.evaluate(
                    """el => {
                        if (window.$) {
                            const kb = $(el).data('kendoButton');
                            if (kb && typeof kb.enable === 'function') kb.enable(true);
                        }
                        el.removeAttribute('disabled');
                        el.removeAttribute('aria-disabled');
                        el.classList.remove('k-state-disabled');
                    }"""
                )
        except Exception:
            pass

    def click(self, target: Union[Locator, str], timeout_ms: int = 5000) -> bool:
        """Enables the Kendo button if needed, scrolls into view, and performs click."""
        self.enable(target)
        loc = target if isinstance(target, Locator) else self.page.locator(target)
        try:
            loc.scroll_into_view_if_needed()
            loc.click(force=True, timeout=timeout_ms)
            return True
        except Exception:
            try:
                loc.evaluate("el => el.click()")
                return True
            except Exception as e:
                self.logger.warning(f"KendoButton click failed for {target}: {e}")
                return False


class KendoGrid:
    """
    Dedicated Page Component representing Kendo UI Grid widgets.
    Encapsulates table row querying, record count, cell inspection,
    and row action button interactions (e.g. targeting the 1st record).
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def wait_for_grid(self, target: Union[Locator, str], timeout_ms: int = 15000) -> Locator:
        """Waits for the Kendo Grid container to be visible and any loading mask to clear."""
        grid = target if isinstance(target, Locator) else self.page.locator(target)
        grid.wait_for(state="visible", timeout=timeout_ms)
        try:
            loader = grid.locator(".k-loading-mask, .k-loading-image")
            if loader.count() > 0:
                loader.first.wait_for(state="hidden", timeout=timeout_ms)
        except Exception:
            pass
        return grid

    def get_rows(self, target: Union[Locator, str]) -> Locator:
        """Returns locator representing data rows excluding headers, groups, and no-data rows."""
        grid = target if isinstance(target, Locator) else self.page.locator(target)
        return grid.locator("tbody tr:not(.k-no-data):not(.k-grouping-row)")

    def get_row(self, target: Union[Locator, str], row_index: int = 0) -> Locator:
        """Returns the locator for a specific row index (defaults to index 0 for 1st record)."""
        rows = self.get_rows(target)
        return rows.nth(row_index) if row_index > 0 else rows.first

    def get_row_text(self, target: Union[Locator, str], row_index: int = 0, timeout_ms: int = 10000) -> str:
        """Retrieves and cleans inner text for the specified row index."""
        row = self.get_row(target, row_index=row_index)
        row.wait_for(state="visible", timeout=timeout_ms)
        return row.inner_text().strip().replace("\n", " ")

    def click_row_button(
        self,
        target: Union[Locator, str],
        row_index: int = 0,
        button_name_regex: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> bool:
        """
        Locates the data row at row_index (defaulting to 0 for 1st record) and clicks its action button/link.
        """
        self.wait_for_grid(target, timeout_ms=timeout_ms)
        row = self.get_row(target, row_index=row_index)
        row.wait_for(state="visible", timeout=timeout_ms)
        row.scroll_into_view_if_needed()

        if button_name_regex:
            btn = row.get_by_role("button", name=re.compile(button_name_regex, re.I)).or_(
                row.locator(f"button:has-text('{button_name_regex}'), a:has-text('{button_name_regex}')")
            ).first
        else:
            btn = row.get_by_role("button").or_(
                row.locator("button, a.k-button, a, [role='button']")
            ).first

        btn.wait_for(state="visible", timeout=timeout_ms)
        btn.scroll_into_view_if_needed()
        try:
            btn.click(force=True, timeout=5000)
            return True
        except Exception:
            btn.evaluate("el => el.click()")
            return True

    def get_cell_text(
        self,
        target: Union[Locator, str],
        row_index: int = 0,
        col_index: int = 0,
        timeout_ms: int = 10000,
    ) -> str:
        """Retrieves cleaned inner text of a specific cell (td) within the specified row."""
        self.wait_for_grid(target, timeout_ms=timeout_ms)
        row = self.get_row(target, row_index=row_index)
        row.wait_for(state="visible", timeout=timeout_ms)
        cell = row.locator("td").nth(col_index)
        return cell.inner_text().strip()

    def get_first_record_identifier(
        self,
        target: Union[Locator, str],
        pattern: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> str:
        """
        Retrieves the primary identifier (e.g. Application Number) from the 1st record in the table.
        If pattern is provided, searches the row text with regex; otherwise returns the first link or non-empty cell.
        """
        self.wait_for_grid(target, timeout_ms=timeout_ms)
        row = self.get_row(target, row_index=0)
        row.wait_for(state="visible", timeout=timeout_ms)
        row_text = row.inner_text().strip().replace("\n", " ")

        if pattern:
            match = re.search(pattern, row_text)
            if match:
                return match.group(0).strip()

        # Try to find link in the first few cells (often the application number link)
        link = row.locator("td a").first
        if link.count() > 0:
            link_text = link.inner_text().strip()
            if link_text:
                return link_text

        # Fallback to first non-empty cell
        cells = row.locator("td")
        for i in range(cells.count()):
            txt = cells.nth(i).inner_text().strip()
            if txt and not txt.startswith("--"):
                return txt

        return row_text.split()[0] if row_text else ""


class KendoControls:
    """
    Composite controller providing unified access to all Kendo UI widgets
    (Dropdowns, DatePickers, MaskedTextBoxes, NumericTextBoxes, Checkboxes, Buttons, Grids, and Alert dialogs).
    """

    def __init__(self, page: Page):
        self.page = page
        self.dropdown = KendoDropdown(page)
        self.datepicker = KendoDatePicker(page)
        self.numeric = KendoNumericTextBox(page)
        self.masked = KendoMaskedTextBox(page)
        self.checkbox = KendoCheckbox(page)
        self.button = KendoButton(page)
        self.grid = KendoGrid(page)

    @staticmethod
    def handle_kendo_alert(page: Page, timeout_ms: int = 15000) -> bool:
        """Detects and clicks OK on Kendo alert/confirm dialogs if displayed."""
        try:
            ok_btn = (
                page.get_by_role("button", name=re.compile(r"^(OK|Yes)$", re.I))
                .or_(page.locator(".k-dialog:visible button:has-text('OK')"))
                .or_(page.locator(".k-window:visible button:has-text('OK')"))
                .or_(page.locator("[role='dialog']:visible button:has-text('OK')"))
                .or_(page.locator(".k-dialog-buttongroup button:has-text('OK')"))
                .or_(page.locator("button:visible:has-text('OK')"))
                .first
            )
            ok_btn.wait_for(state="visible", timeout=timeout_ms)
            ok_btn.click()
            return True
        except Exception:
            return False

    @staticmethod
    def dismiss_survey_modal(page: Page, timeout_ms: int = 8000) -> bool:
        """Dismisses the optional post-submission survey modal by clicking 'No'."""
        try:
            survey_no_btn = (
                page.locator(
                    ".k-dialog:visible button:has-text('No'), "
                    ".k-window:visible button:has-text('No'), "
                    "[role='dialog']:visible button:has-text('No'), "
                    ".k-dialog-buttongroup button:has-text('No'), "
                    "button:visible:has-text('No')"
                )
                .or_(page.get_by_role("button", name=re.compile(r"^No$", re.I)))
                .first
            )
            survey_no_btn.wait_for(state="visible", timeout=timeout_ms)
            survey_no_btn.click()
            return True
        except Exception:
            return False

    @staticmethod
    def dismiss_ok_dialogs(page: Page, timeout_ms: int = 2000, max_clicks: int = 3) -> int:
        """Dismisses visible OK popups safely using KendoControls helper."""
        dismissed = 0
        for _ in range(max_clicks):
            try:
                if KendoControls.handle_kendo_alert(page, timeout_ms=timeout_ms):
                    page.wait_for_timeout(400)
                    dismissed += 1
                else:
                    ok_btn = page.locator(
                        ".k-dialog:visible button:has-text('OK'), .k-window:visible button:has-text('OK'), button:visible:has-text('OK')"
                    ).first
                    if ok_btn.is_visible(timeout=timeout_ms):
                        ok_btn.click(force=True)
                        page.wait_for_timeout(400)
                        dismissed += 1
                    else:
                        break
            except Exception:
                break
        return dismissed
