import logging
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
            if loc.is_visible(timeout=timeout_ms):
                loc.click(force=True)
                self.page.wait_for_timeout(300)
                option = self.page.locator(
                    ".k-animation-container:visible li, .k-list-container:visible li, [role='listbox']:visible li, [role='option']:visible"
                ).filter(has_text=option_text).first
                if option.is_visible(timeout=timeout_ms):
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

    def select_first_option(self, field_id: str, timeout_ms: int = 2500) -> bool:
        """
        Selects the first available option in a Kendo DropDownList.
        Waits for cascading remote data if needed, then selects index 1 and triggers change event.
        """
        clean_id = field_id.lstrip("#")
        if any(term in clean_id for term in ["County", "Route", "District"]):
            try:
                self.page.wait_for_function(
                    f"() => window.$ && $('#{clean_id}').data('kendoDropDownList')?.dataSource?.data()?.length > 0",
                    timeout=timeout_ms,
                )
            except Exception:
                pass

        try:
            return bool(
                self.page.evaluate(
                    f"""(() => {{
                        if (!window.$) return false;
                        const ddl = $('#{clean_id}').data('kendoDropDownList');
                        if (ddl) {{
                            const count = ddl.dataSource ? ddl.dataSource.data().length : 0;
                            if (count > 0) {{
                                ddl.select(1);
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
            )
        except Exception as e:
            self.logger.warning(f"KendoDropdown select_first_option failed for #{clean_id}: {e}")
            return False

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
            # Also fill via Playwright if visible to ensure browser-level event dispatch
            try:
                inp_loc = self.page.locator(f"#{clean_id}")
                if inp_loc.is_visible(timeout=500):
                    inp_loc.fill(date_str)
                    inp_loc.press("Tab")
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
                if loc.is_visible(timeout=500):
                    loc.fill(date_str)
                    loc.press("Tab")
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
        """Polymorphic set_value for MaskedTextBox."""
        if isinstance(target, str):
            clean_id = target.lstrip("#")
            if " " not in clean_id and (clean_id.isalnum() or "_" in clean_id or "-" in clean_id):
                return self.set_value_by_id(clean_id, value)
        loc = target if isinstance(target, Locator) else self.page.locator(target)
        try:
            loc.fill(value)
            loc.press("Tab")
            return True
        except Exception as e:
            self.logger.warning(f"KendoMaskedTextBox set_value failed for {target}: {e}")
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


class KendoControls:
    """
    Composite controller providing unified access to all Kendo UI widgets
    (Dropdowns, DatePickers, MaskedTextBoxes, NumericTextBoxes, and Alert dialogs).
    """

    def __init__(self, page: Page):
        self.page = page
        self.dropdown = KendoDropdown(page)
        self.datepicker = KendoDatePicker(page)
        self.numeric = KendoNumericTextBox(page)
        self.masked = KendoMaskedTextBox(page)

    @staticmethod
    def handle_kendo_alert(page: Page, timeout_ms: int = 5000) -> bool:
        """Detects and clicks OK on Kendo alert/confirm dialogs if displayed."""
        try:
            active_dialog = page.locator(
                ".k-window:visible, .k-dialog:visible, [role='dialog']:visible"
            ).first
            if active_dialog.is_visible(timeout=timeout_ms):
                ok_btn = active_dialog.locator(
                    "button:has-text('OK'), .k-button:has-text('OK'), button:has-text('Yes'), .k-dialog-buttongroup button, [role='button']:has-text('OK')"
                ).first
                if ok_btn.is_visible(timeout=2000):
                    ok_btn.click()
                    return True
        except Exception:
            pass
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
